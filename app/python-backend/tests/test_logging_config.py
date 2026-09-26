import io
import json
import logging

import pytest
import structlog

from logging_config import LogSettings, build_logging_dict, configure_logging, load_settings


def test_load_settings_defaults():
    assert load_settings({}) == LogSettings(level="INFO", format="json")


def test_load_settings_normalizes_case():
    assert load_settings({"LOG_LEVEL": "debug", "LOG_FORMAT": "CONSOLE"}) == LogSettings(
        level="DEBUG", format="console"
    )


@pytest.mark.parametrize("env", [{"LOG_LEVEL": "verbose"}, {"LOG_FORMAT": "xml"}])
def test_load_settings_rejects_invalid_values(env):
    with pytest.raises(ValueError):
        load_settings(env)


def test_noisy_libraries_are_limited_to_warning():
    loggers = build_logging_dict(LogSettings(level="DEBUG", format="json"))["loggers"]
    assert loggers["matplotlib"]["level"] == "WARNING"
    assert loggers["PIL"]["level"] == "WARNING"


def test_gunicorn_error_logs_are_routed_to_root_handler():
    loggers = build_logging_dict(LogSettings(level="INFO", format="json"))["loggers"]
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
