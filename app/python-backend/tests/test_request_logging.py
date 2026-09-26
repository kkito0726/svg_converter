import io
import re

import pytest
from werkzeug.datastructures import FileStorage, MultiDict

from request_logging import (
    REDACTED,
    level_for_status,
    read_svg_head,
    redact_headers,
    resolve_client_ip,
    resolve_request_id,
    summarize_files,
    summarize_form,
    truncate,
)

HEX_ID = re.compile(r"^[0-9a-f]{32}$")


def test_valid_request_id_is_kept():
    assert resolve_request_id("abc-123-XYZ") == "abc-123-XYZ"


@pytest.mark.parametrize("value", [None, "", "a" * 65, "abc\n", "a b", "<script>"])
def test_invalid_request_id_is_replaced(value):
    assert HEX_ID.match(resolve_request_id(value))


def test_generated_request_ids_are_unique():
    assert resolve_request_id(None) != resolve_request_id(None)


def test_redact_headers_keeps_allowlisted_values_only():
    headers = [
        ("Content-Type", "multipart/form-data"),
        ("User-Agent", "Mozilla/5.0"),
        ("cf-ray", "8c7a-NRT"),
        ("Cookie", "session=secret"),
        ("Authorization", "Bearer secret"),
        ("Cf-Access-Jwt-Assertion", "secret"),
        ("Cf-Access-Authenticated-User-Email", "user@example.com"),
        ("CF-Connecting-IP", "198.51.100.1"),
        ("X-Forwarded-For", "192.0.2.1"),
    ]
    assert redact_headers(headers) == {
        "Content-Type": "multipart/form-data",
        "User-Agent": "Mozilla/5.0",
        "cf-ray": "8c7a-NRT",
        "Cookie": REDACTED,
        "Authorization": REDACTED,
        "Cf-Access-Jwt-Assertion": REDACTED,
        "Cf-Access-Authenticated-User-Email": REDACTED,
        "CF-Connecting-IP": REDACTED,
        "X-Forwarded-For": REDACTED,
    }


def test_redact_headers_strips_query_from_referer():
    headers = [("Referer", "https://example.com/page?token=secret#frag")]
    assert redact_headers(headers) == {"Referer": "https://example.com/page"}


def test_redact_headers_truncates_long_values():
    value = redact_headers([("Accept", "x" * 2000)])["Accept"]
    assert len(value) < 600


def test_truncate_keeps_short_values():
    assert truncate("abc", 3) == "abc"


def test_truncate_marks_cut_values():
    value = truncate("abcdef", 3)
    assert value.startswith("abc")
    assert value.endswith("[truncated]")


def test_summarize_form_truncates_to_1kb():
    form = MultiDict({"json_data": "x" * 5000, "other": "1"})
    summary = summarize_form(form)
    assert summary["other"] == "1"
    assert summary["json_data"].startswith("x" * 1024)
    assert len(summary["json_data"]) < 1100


def svg_file(content: bytes = b"<svg/>", filename="My Drawing.SVG") -> FileStorage:
    return FileStorage(stream=io.BytesIO(content), filename=filename, content_type="image/svg+xml")


def test_summarize_files_has_metadata_but_no_filename():
    storage = svg_file(b"<svg>12345</svg>")
    storage.stream.seek(3)
    (summary,) = summarize_files(MultiDict([("file", storage)]))
    assert summary == {
        "field": "file",
        "content_type": "image/svg+xml",
        "size": 16,
        "ext": ".svg",
        "filename_len": len("My Drawing.SVG"),
    }
    assert storage.stream.tell() == 3


def test_summarize_files_truncates_long_extension():
    (summary,) = summarize_files(MultiDict([("file", svg_file(filename="a." + "x" * 100))]))
    assert len(summary["ext"]) <= 16


def test_read_svg_head_returns_first_bytes_and_restores_position():
    storage = svg_file(b"<svg>" + b"a" * 5000 + b"\xff")
    storage.stream.seek(10)
    head = read_svg_head(MultiDict([("file", storage)]), limit=2048)
    assert head == ("<svg>" + "a" * 2043)
    assert storage.stream.tell() == 10


def test_read_svg_head_replaces_invalid_utf8():
    assert read_svg_head(MultiDict([("file", svg_file(b"\xff<svg/>"))])) == "�<svg/>"


def test_read_svg_head_without_file_is_none():
    assert read_svg_head(MultiDict()) is None


@pytest.mark.parametrize("real_ip", ["203.0.113.5", "2001:db8::1"])
def test_client_ip_comes_from_x_real_ip(real_ip):
    assert resolve_client_ip(real_ip, "172.18.0.3") == real_ip


@pytest.mark.parametrize("real_ip", [None, "", "evil\nvalue", "999.1.1.1"])
def test_client_ip_falls_back_to_remote_addr(real_ip):
    assert resolve_client_ip(real_ip, "172.18.0.3") == "172.18.0.3"


@pytest.mark.parametrize("status,level", [(200, "info"), (302, "info"), (400, "warning"), (413, "warning"), (500, "error")])
def test_level_for_status(status, level):
    assert level_for_status(status) == level
