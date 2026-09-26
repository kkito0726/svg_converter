"""リクエスト単位のログ (request_id の付与と request.completed の出力)。仕様は docs/logging-design.md"""

import ipaddress
import logging
import os
import re
import time
import uuid
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit

import structlog
from flask import Flask, Response, g, request
from werkzeug.datastructures import FileStorage, MultiDict
from werkzeug.exceptions import HTTPException

from error_reason import ErrorReason
from stream_utils import stream_size

REDACTED = "[REDACTED]"
TRUNCATED_MARK = "…[truncated]"
REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9-]{1,64}")
# 値をログに出してよいヘッダ (小文字)。それ以外は名前だけ出して値は伏せる
HEADER_ALLOWLIST = frozenset(
    {
        "content-type",
        "content-length",
        "user-agent",
        "accept",
        "accept-language",
        "origin",
        "referer",
        "x-request-id",
        "cf-ray",
        "cf-ipcountry",
    }
)
HEADER_VALUE_LIMIT = 512
FORM_VALUE_LIMIT = 1024
USER_AGENT_LIMIT = 256
EXT_LIMIT = 16
SVG_HEAD_LIMIT = 2048
CF_RAY_LIMIT = 64

logger = structlog.get_logger(__name__)
# DEBUG が有効かどうかは標準 logging のレベル設定で判定する
stdlib_logger = logging.getLogger(__name__)


def truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[:limit] + TRUNCATED_MARK


def resolve_request_id(header_value: str | None) -> str:
    if header_value and REQUEST_ID_PATTERN.fullmatch(header_value):
        return header_value
    return uuid.uuid4().hex


def resolve_client_ip(real_ip_header: str | None, remote_addr: str | None) -> str | None:
    """nginx が上書きした X-Real-IP を使う。CF-Connecting-IP / X-Forwarded-For は偽装できるので読まない"""
    try:
        return str(ipaddress.ip_address(real_ip_header or ""))
    except ValueError:
        return remote_addr


def _strip_query(url: str) -> str:
    """Referer のクエリ文字列にはトークンが入り得るので、scheme / host / path だけ残す"""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def _header_value(name: str, value: str) -> str:
    lowered = name.lower()
    if lowered not in HEADER_ALLOWLIST:
        return REDACTED
    return truncate(_strip_query(value) if lowered == "referer" else value, HEADER_VALUE_LIMIT)


def redact_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {name: _header_value(name, value) for name, value in headers}


def summarize_form(form: MultiDict) -> dict[str, str]:
    return {key: truncate(value, FORM_VALUE_LIMIT) for key, value in form.items()}


def _summarize_file(field: str, storage: FileStorage) -> dict:
    filename = storage.filename or ""
    return {
        "field": field,
        "content_type": storage.content_type,
        "size": stream_size(storage.stream),
        "ext": os.path.splitext(filename)[1].lower()[:EXT_LIMIT],
        # ファイル名そのものは個人名などを含み得るので出さない
        "filename_len": len(filename),
    }


def summarize_files(files: MultiDict) -> list[dict]:
    return [_summarize_file(field, storage) for field, storage in files.items(multi=True)]


def read_svg_head(files: MultiDict, limit: int = SVG_HEAD_LIMIT) -> str | None:
    storage = files.get("file")
    if storage is None:
        return None
    position = storage.stream.tell()
    storage.stream.seek(0)
    head = storage.stream.read(limit)
    storage.stream.seek(position)
    return head.decode("utf-8", errors="replace")


def level_for_status(status: int) -> str:
    if status >= 500:
        return "error"
    if status >= 400:
        return "warning"
    return "info"


def set_log_reason(reason: ErrorReason) -> None:
    """request.completed に載せる集計用の理由コード (docs/logging-design.md 3.3)"""
    g.log_reason = reason


def _bind_request_context() -> None:
    g.request_started = time.perf_counter()
    g.request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    cf_ray = request.headers.get("CF-Ray")
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=g.request_id,
        **({"cf_ray": truncate(cf_ray, CF_RAY_LIMIT)} if cf_ray else {}),
    )


def _request_details(status: int, include_svg_head: bool) -> dict:
    headers = {"headers": redact_headers(request.headers.items())}
    # 413 でボディを読むと再び RequestEntityTooLarge になるのでヘッダだけにする
    if status == 413:
        return headers
    try:
        # 404 などルートがボディを読まなかった場合は、ここで初めてパースされて上限超過になり得る
        body = {"form": summarize_form(request.form), "files": summarize_files(request.files)}
    except HTTPException:
        return headers
    svg_head = {"svg_head": read_svg_head(request.files)} if include_svg_head else {}
    return {**headers, **body, **svg_head}


def _completed_fields(response: Response) -> dict:
    status = response.status_code
    debug = stdlib_logger.isEnabledFor(logging.DEBUG)
    reason = g.get("log_reason")
    return {
        "method": request.method,
        "path": request.path,
        "status": status,
        "duration_ms": round((time.perf_counter() - g.request_started) * 1000),
        "content_length": request.content_length,
        "client_ip": resolve_client_ip(request.headers.get("X-Real-IP"), request.remote_addr),
        "user_agent": truncate(request.headers.get("User-Agent", ""), USER_AGENT_LIMIT),
        **({"reason": reason} if reason else {}),
        **({"request": _request_details(status, debug)} if status >= 400 or debug else {}),
    }


def register_request_logging(app: Flask, exclude_paths: Iterable[str] = ()) -> None:
    excluded = frozenset(exclude_paths)

    @app.before_request
    def bind_request_context() -> None:
        _bind_request_context()

    @app.after_request
    def log_request_completed(response: Response) -> Response:
        response.headers["X-Request-ID"] = g.request_id
        if request.path in excluded:
            return response
        try:
            fields = _completed_fields(response)
        except Exception:
            # ログの組み立てに失敗してもレスポンスは返す
            logger.exception("request.log_failed")
            return response
        getattr(logger, level_for_status(response.status_code))("request.completed", **fields)
        return response

    @app.teardown_request
    def clear_request_context(_exc: BaseException | None) -> None:
        structlog.contextvars.clear_contextvars()
