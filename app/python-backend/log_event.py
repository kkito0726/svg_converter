from enum import StrEnum


class LogEvent(StrEnum):
    """ログの event 名 (docs/logging-design.md 3.2)。StrEnum なので JSON には文字列のまま出る"""

    REQUEST_COMPLETED = "request.completed"
    # request.completed の組み立てに失敗した (レスポンスは返している)
    REQUEST_LOG_FAILED = "request.log_failed"
    CONVERT_COMPLETED = "convert.completed"
    CONVERT_FAILED = "convert.failed"
