import io
import json
import logging

import pytest
import structlog

from logging_config import LogFormat, LogLevel, LogSettings, build_logging_dict, configure_logging, load_settings


def test_load_settings_defaults():
    assert load_settings({}) == LogSettings(level=LogLevel.INFO, format=LogFormat.JSON)


def test_load_settings_normalizes_case_to_enums():
    settings = load_settings({"LOG_LEVEL": "debug", "LOG_FORMAT": "CONSOLE"})
    assert settings == LogSettings(level=LogLevel.DEBUG, format=LogFormat.CONSOLE)
    assert isinstance(settings.level, LogLevel)
    assert isinstance(settings.format, LogFormat)


@pytest.mark.parametrize(
    "env,allowed",
    [({"LOG_LEVEL": "verbose"}, "DEBUG, INFO, WARNING, ERROR"), ({"LOG_FORMAT": "xml"}, "json, console")],
)
def test_load_settings_rejects_invalid_values(env, allowed):
    with pytest.raises(ValueError, match=allowed):
        load_settings(env)


@pytest.mark.parametrize(
    "level,numeric",
    [(LogLevel.DEBUG, logging.DEBUG), (LogLevel.INFO, logging.INFO), (LogLevel.WARNING, logging.WARNING), (LogLevel.ERROR, logging.ERROR)],
)
def test_log_level_numeric_matches_stdlib(level, numeric):
    assert level.numeric == numeric


def test_logging_dict_uses_plain_level_name():
    assert build_logging_dict(LogSettings(level=LogLevel.DEBUG, format=LogFormat.JSON))["root"]["level"] == "DEBUG"


def test_noisy_libraries_are_limited_to_warning():
    loggers = build_logging_dict(LogSettings(level=LogLevel.DEBUG, format=LogFormat.JSON))["loggers"]
    assert loggers["matplotlib"]["level"] == "WARNING"
    assert loggers["PIL"]["level"] == "WARNING"


def test_gunicorn_error_logs_are_routed_to_root_handler():
    loggers = build_logging_dict(LogSettings(level=LogLevel.INFO, format=LogFormat.JSON))["loggers"]
    assert loggers["gunicorn.error"]["handlers"] == []
    assert loggers["gunicorn.error"]["propagate"] is True


def test_gunicorn_access_logs_are_suppressed(emit):
    # logconfig_dict を渡すと gunicorn は accesslog=None でも gunicorn.access に出すため、レベルで止める
    out = emit({}, lambda: logging.getLogger("gunicorn.access").info('"GET /healthz HTTP/1.1" 200'))
    assert out == ""


@pytest.fixture
def emit():
    """env で設定したロガーの出力を文字列で受け取る"""

    def _emit(env, log):
        configure_logging(env)
        stream = io.StringIO()
        logging.getLogger().handlers[0].setStream(stream)
        log()
        return stream.getvalue()

    yield _emit
    structlog.contextvars.clear_contextvars()
    configure_logging({})


def test_json_output_has_common_fields(emit):
    def log():
        structlog.contextvars.bind_contextvars(request_id="req-1")
        structlog.get_logger("svc").info("convert.completed", svg_bytes=10, note="日本語")

    line = json.loads(emit({}, log))
    assert line["event"] == "convert.completed"
    assert line["level"] == "info"
    assert line["logger"] == "svc"
    assert line["timestamp"].endswith("Z")
    assert line["request_id"] == "req-1"
    assert line["svg_bytes"] == 10
    assert line["note"] == "日本語"


def test_json_output_starts_with_timestamp_and_level(emit):
    def log():
        structlog.contextvars.bind_contextvars(request_id="req-1")
        structlog.get_logger("svc").warning("convert.completed", svg_bytes=10, plot_ms=5)

    keys = list(json.loads(emit({}, log)))
    assert keys[:3] == ["timestamp", "level", "event"]
    assert set(keys[3:-1]) == {"request_id", "svg_bytes", "plot_ms"}
    assert keys[-1] == "logger"


def test_request_completed_puts_method_and_status_first(emit):
    def log():
        structlog.get_logger("request_logging").warning(
            "request.completed",
            path="/svg2csv",
            status=400,
            duration_ms=1,
            client_ip="203.0.113.5",
            request={"headers": {}},
            reason="out_of_range",
            method="POST",
        )

    keys = list(json.loads(emit({}, log)))
    assert keys == [
        "timestamp",
        "level",
        "event",
        "method",
        "status",
        "reason",
        "path",
        "duration_ms",
        "client_ip",
        "logger",
        "request",
    ]


def test_stdlib_json_output_starts_with_timestamp_and_level(emit):
    out = emit({}, lambda: logging.getLogger("gunicorn.error").info("Booting worker"))
    assert list(json.loads(out)) == ["timestamp", "level", "event", "logger"]


def test_stdlib_logs_use_same_json_format(emit):
    out = emit({}, lambda: logging.getLogger("gunicorn.error").info("Booting worker"))
    line = json.loads(out)
    assert line["event"] == "Booting worker"
    assert line["logger"] == "gunicorn.error"
    assert line["level"] == "info"


def test_exception_is_rendered_as_traceback(emit):
    def log():
        try:
            1 / 0
        except ZeroDivisionError:
            structlog.get_logger("svc").exception("convert.failed")

    line = json.loads(emit({}, log))
    assert line["level"] == "error"
    assert "ZeroDivisionError" in line["exception"]


def test_newlines_in_values_do_not_break_lines(emit):
    out = emit({}, lambda: structlog.get_logger("svc").warning("x", value="a\nb"))
    assert out.count("\n") == 1


def test_level_below_threshold_is_dropped(emit):
    assert emit({"LOG_LEVEL": "WARNING"}, lambda: structlog.get_logger("svc").info("x")) == ""


def test_console_format_is_human_readable(emit):
    out = emit({"LOG_FORMAT": "console"}, lambda: structlog.get_logger("svc").info("hello"))
    assert "hello" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)
