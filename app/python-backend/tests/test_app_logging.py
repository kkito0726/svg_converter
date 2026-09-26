import io
import json
import logging
import os
import re
from glob import glob

import pytest

from app import app
from service.converter_service import ConvertService

SVG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "svg")
SVG_PATH = sorted(glob(os.path.join(SVG_DIR, "*.svg")))[0]
SECRET_MARKER = "do-not-log-this-marker"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def sample_svg() -> bytes:
    with open(SVG_PATH, "rb") as f:
        content = f.read()
    # 中身がログに出ていないかを確かめるための目印を末尾のコメントに入れる
    return content + f"<!-- {SECRET_MARKER} -->".encode()


@pytest.fixture
def debug_request_logging():
    logger = logging.getLogger("request_logging")
    original = logger.level
    logger.setLevel(logging.DEBUG)
    yield
    logger.setLevel(original)


def post_svg(client, svg_bytes: bytes, filename="sample.svg", power=0.5, speed=2000, headers=None, json_data=None):
    return client.post(
        "/svg2csv",
        data={
            "file": (io.BytesIO(svg_bytes), filename),
            "json_data": json_data if json_data is not None else json.dumps({"power": power, "speed": speed}),
        },
        content_type="multipart/form-data",
        headers=headers or {},
    )


def only(entries, event):
    matched = [e for e in entries if e["event"] == event]
    assert len(matched) == 1, f"{event} が {len(matched)} 件: {entries}"
    return matched[0]


def test_success_logs_convert_and_request_completed(client, log_output, sample_svg):
    res = post_svg(client, sample_svg, headers={"User-Agent": "pytest-agent"})

    assert res.status_code == 200
    completed = only(log_output, "request.completed")
    assert completed["log_level"] == "info"
    assert completed["method"] == "POST"
    assert completed["path"] == "/svg2csv"
    assert completed["status"] == 200
    assert completed["duration_ms"] >= 0
    assert completed["content_length"] > len(sample_svg)
    assert completed["user_agent"] == "pytest-agent"
    assert "client_ip" in completed
    assert "request" not in completed
    assert "reason" not in completed

    converted = only(log_output, "convert.completed")
    assert converted["svg_bytes"] == len(sample_svg)
    assert converted["power"] == 0.5
    assert converted["speed"] == 2000
    assert converted["svg2csv_ms"] >= 0
    assert converted["plot_ms"] >= 0
    assert converted["csv_bytes"] == len(res.get_json()["csv_text"].encode())
    assert converted["request_id"] == completed["request_id"]


def test_rejected_request_logs_request_details(client, log_output, sample_svg):
    # Werkzeug のテストクライアントは headers で渡した Cookie を無視するので cookie jar に入れる
    client.set_cookie("session", "secret-cookie")
    res = post_svg(
        client,
        sample_svg,
        filename="Secret Name.svg",
        power=5,
        headers={"Authorization": "Bearer secret-token"},
    )

    assert res.status_code == 400
    completed = only(log_output, "request.completed")
    assert completed["log_level"] == "warning"
    assert completed["reason"] == "out_of_range"
    request = completed["request"]
    assert request["headers"]["Cookie"] == "[REDACTED]"
    assert request["headers"]["Authorization"] == "[REDACTED]"
    assert json.loads(request["form"]["json_data"]) == {"power": 5, "speed": 2000}
    (file_summary,) = request["files"]
    assert file_summary["ext"] == ".svg"
    assert file_summary["filename_len"] == len("Secret Name.svg")
    assert file_summary["size"] == len(sample_svg)
    logged = str(log_output)
    assert "secret-cookie" not in logged
    assert "secret-token" not in logged
    assert "Secret Name" not in logged
    assert SECRET_MARKER not in logged


@pytest.mark.parametrize(
    "kwargs,reason",
    [
        ({"json_data": ""}, "missing_params"),
        ({"json_data": "{broken"}, "invalid_params"),
        ({"speed": 0}, "out_of_range"),
        ({"filename": "image.png"}, "invalid_extension"),
    ],
)
def test_reason_codes(client, log_output, sample_svg, kwargs, reason):
    assert post_svg(client, sample_svg, **kwargs).status_code == 400
    assert only(log_output, "request.completed")["reason"] == reason


def test_invalid_svg_reason(client, log_output):
    assert post_svg(client, b"<svg><not-closed>").status_code == 400
    assert only(log_output, "request.completed")["reason"] == "invalid_svg"


def test_missing_file_reason(client, log_output):
    res = client.post(
        "/svg2csv",
        data={"json_data": json.dumps({"power": 0.5, "speed": 2000})},
        content_type="multipart/form-data",
    )
    assert res.status_code == 400
    assert only(log_output, "request.completed")["reason"] == "no_file"


def test_too_large_logs_headers_only(client, log_output, monkeypatch):
    monkeypatch.setitem(app.config, "MAX_CONTENT_LENGTH", 100)

    assert post_svg(client, b"x" * 1000).status_code == 413
    completed = only(log_output, "request.completed")
    assert completed["reason"] == "too_large"
    assert completed["log_level"] == "warning"
    assert "headers" in completed["request"]
    assert "form" not in completed["request"]
    assert "files" not in completed["request"]


def test_internal_error_logs_traceback_but_hides_it_from_client(client, log_output, sample_svg, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("internal detail")

    monkeypatch.setattr(ConvertService, "convert", staticmethod(boom))

    res = post_svg(client, sample_svg)

    assert res.status_code == 500
    assert "internal detail" not in res.get_data(as_text=True)
    failed = only(log_output, "convert.failed")
    assert failed["log_level"] == "error"
    assert failed["exc_info"] is True
    completed = only(log_output, "request.completed")
    assert completed["log_level"] == "error"
    assert completed["reason"] == "internal_error"
    assert failed["request_id"] == completed["request_id"]


def test_request_id_is_propagated(client, log_output, sample_svg):
    res = post_svg(client, sample_svg, headers={"X-Request-ID": "req-123"})

    assert res.headers["X-Request-ID"] == "req-123"
    assert only(log_output, "request.completed")["request_id"] == "req-123"


def test_invalid_request_id_is_replaced(client, log_output, sample_svg):
    res = post_svg(client, sample_svg, headers={"X-Request-ID": "bad id"})

    request_id = res.headers["X-Request-ID"]
    assert re.fullmatch(r"[0-9a-f]{32}", request_id)
    assert only(log_output, "request.completed")["request_id"] == request_id


def test_cf_ray_is_bound(client, log_output, sample_svg):
    post_svg(client, sample_svg, headers={"CF-Ray": "8c7a-NRT"})
    assert only(log_output, "convert.completed")["cf_ray"] == "8c7a-NRT"


def test_client_ip_trusts_only_x_real_ip(client, log_output, sample_svg):
    headers = {
        "X-Real-IP": "203.0.113.5",
        "CF-Connecting-IP": "198.51.100.1",
        "X-Forwarded-For": "192.0.2.1",
    }
    post_svg(client, sample_svg, headers=headers)
    assert only(log_output, "request.completed")["client_ip"] == "203.0.113.5"


def test_user_agent_is_truncated(client, log_output, sample_svg):
    post_svg(client, sample_svg, headers={"User-Agent": "a" * 1000})
    assert len(only(log_output, "request.completed")["user_agent"]) < 300


def test_healthz_is_not_logged(client, log_output):
    assert client.get("/healthz").status_code == 200
    assert [e for e in log_output if e["event"] == "request.completed"] == []


@pytest.mark.usefixtures("debug_request_logging")
def test_debug_level_logs_request_and_svg_head(client, log_output):
    svg = f"<svg><!-- {SECRET_MARKER} --></svg>".encode()
    post_svg(client, svg)

    request = only(log_output, "request.completed")["request"]
    assert SECRET_MARKER in request["svg_head"]
    assert "headers" in request


def test_oversized_body_on_unknown_path_logs_headers_only(client, log_output, monkeypatch):
    monkeypatch.setitem(app.config, "MAX_CONTENT_LENGTH", 100)

    res = client.post("/nope", data={"file": (io.BytesIO(b"x" * 1000), "a.svg")}, content_type="multipart/form-data")

    assert res.status_code == 404
    completed = only(log_output, "request.completed")
    assert completed["log_level"] == "warning"
    assert "headers" in completed["request"]
    assert "form" not in completed["request"]
    assert [e for e in log_output if e["event"] == "request.log_failed"] == []


def test_context_does_not_leak_between_requests(client, log_output, sample_svg):
    post_svg(client, sample_svg, headers={"CF-Ray": "first-ray", "X-Request-ID": "first"})
    post_svg(client, sample_svg)

    second = [e for e in log_output if e["event"] == "request.completed"][1]
    assert second["request_id"] != "first"
    assert "cf_ray" not in second


def test_internal_error_response_has_request_id(client, log_output, sample_svg, monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("internal detail")

    monkeypatch.setattr(ConvertService, "convert", staticmethod(boom))

    res = post_svg(client, sample_svg, headers={"X-Request-ID": "err-1"})

    assert res.status_code == 500
    assert res.headers["X-Request-ID"] == "err-1"
