"""ログ設定: structlog と標準 logging を統合し、1 行 1 イベントで stdout に出す (docs/logging-design.md)"""

import logging.config
import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

import structlog


class LogLevel(StrEnum):
    """LOG_LEVEL で指定できるレベル。値は標準 logging のレベル名"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @property
    def numeric(self) -> int:
        return logging.getLevelNamesMapping()[self.value]


class LogFormat(StrEnum):
    JSON = "json"
    # 開発用のカラー表示
    CONSOLE = "console"


# DEBUG にすると大量に出るライブラリ
NOISY_LOGGERS = ("matplotlib", "PIL")

SHARED_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
]


@dataclass(frozen=True)
class LogSettings:
    level: LogLevel
    format: LogFormat


def _parse_enum[E: StrEnum](enum_type: type[E], env_name: str, value: str) -> E:
    try:
        return enum_type(value)
    except ValueError as e:
        allowed = ", ".join(member.value for member in enum_type)
        raise ValueError(f"{env_name} は {allowed} のいずれかを指定してください: {value}") from e


def load_settings(env: Mapping[str, str]) -> LogSettings:
    return LogSettings(
        level=_parse_enum(LogLevel, "LOG_LEVEL", env.get("LOG_LEVEL", LogLevel.INFO).upper()),
        format=_parse_enum(LogFormat, "LOG_FORMAT", env.get("LOG_FORMAT", LogFormat.JSON).lower()),
    )


# JSON の先頭に並べるキー。残りのキーはこの後ろに元の順で続く
LEADING_KEYS = ("timestamp", "level", "event", "logger")


def order_leading_keys(_logger, _method_name: str, event_dict: dict) -> dict:
    """読みやすいように時刻・レベル・イベント名を先頭に並べる"""
    leading = {key: event_dict[key] for key in LEADING_KEYS if key in event_dict}
    rest = {key: value for key, value in event_dict.items() if key not in leading}
    return {**leading, **rest}


def _render_processors(log_format: LogFormat) -> list:
    if log_format == LogFormat.CONSOLE:
        # ConsoleRenderer は自前で「時刻 レベル イベント」の順に表示する
        return [structlog.dev.ConsoleRenderer()]
    return [
        structlog.processors.format_exc_info,
        order_leading_keys,
        structlog.processors.JSONRenderer(ensure_ascii=False),
    ]


def build_logging_dict(settings: LogSettings) -> dict:
    """logging.config.dictConfig 用の設定 (gunicorn の logconfig_dict にも使う)"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog": {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": SHARED_PROCESSORS,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    *_render_processors(settings.format),
                ],
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "structlog",
            },
        },
        "root": {"level": settings.level.value, "handlers": ["stdout"]},
        "loggers": {
            **{name: {"level": LogLevel.WARNING.value} for name in NOISY_LOGGERS},
            # gunicorn 自身のログも root のハンドラ (同じフォーマット) に流す
            "gunicorn.error": {"handlers": [], "propagate": True},
            # アクセスログは request.completed で出す。logconfig_dict を渡すと gunicorn は
            # accesslog=None でも INFO で出してくるので、レベルで止める
            "gunicorn.access": {"level": LogLevel.WARNING.value, "handlers": [], "propagate": True},
        },
    }


def configure_logging(env: Mapping[str, str] = os.environ) -> LogSettings:
    settings = load_settings(env)
    logging.config.dictConfig(build_logging_dict(settings))
    structlog.configure(
        processors=[*SHARED_PROCESSORS, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        # テストで structlog.testing の設定に差し替えられるようにキャッシュしない
        cache_logger_on_first_use=False,
    )
    return settings
