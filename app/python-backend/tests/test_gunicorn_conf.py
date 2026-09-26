import importlib.util
import os

import pytest

CONF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gunicorn.conf.py")


def load_conf():
    spec = importlib.util.spec_from_file_location("gunicorn_conf", CONF_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gunicorn_uses_app_logging_config(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    conf = load_conf()

    assert conf.accesslog is None
    assert conf.logconfig_dict["root"]["level"] == "INFO"
    assert conf.logconfig_dict["loggers"]["gunicorn.access"]["level"] == "WARNING"


def test_gunicorn_fails_fast_on_invalid_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "verbose")
    with pytest.raises(ValueError):
        load_conf()
