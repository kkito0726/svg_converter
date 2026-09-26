"""ログ設定: structlog と標準 logging を統合し、1 行 1 イベントで stdout に出す (docs/logging-design.md)"""

import logging.config
import os
from collections.abc import Mapping
from dataclasses import dataclass

import structlog

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
LOG_FORMATS = ("json", "console")
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
    level: str
    format: str


def load_settings(env: Mapping[str, str]) -> LogSettings:
    level = env.get("LOG_LEVEL", "INFO").upper()
    log_format = env.get("LOG_FORMAT", "json").lower()
    if level not in LOG_LEVELS:
        raise ValueError(f"LOG_LEVEL は {', '.join(LOG_LEVELS)} のいずれかを指定してください: {level}")
    if log_format not in LOG_FORMATS:
        raise ValueError(f"LOG_FORMAT は {', '.join(LOG_FORMATS)} のいずれかを指定してください: {log_format}")
    return LogSettings(level=level, format=log_format)


def _render_processors(log_format: str) -> list:
    if log_format == "console":
        return [structlog.dev.ConsoleRenderer()]
    return [structlog.processors.format_exc_info, structlog.processors.JSONRenderer(ensure_ascii=False)]


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
        "root": {"level": settings.level, "handlers": ["stdout"]},
        "loggers": {
            **{name: {"level": "WARNING"} for name in NOISY_LOGGERS},
            # gunicorn 自身のログも root のハンドラ (同じフォーマット) に流す
            "gunicorn.error": {"handlers": [], "propagate": True},
            # アクセスログは request.completed で出す。logconfig_dict を渡すと gunicorn は
            # accesslog=None でも INFO で出してくるので、レベルで止める
            "gunicorn.access": {"level": "WARNING", "handlers": [], "propagate": True},
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
