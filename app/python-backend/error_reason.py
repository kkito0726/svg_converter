from enum import StrEnum


class ErrorReason(StrEnum):
    """ログ集計用の失敗理由コード (docs/logging-design.md 3.3)。StrEnum なので JSON には文字列のまま出る"""

    MISSING_PARAMS = "missing_params"
    INVALID_PARAMS = "invalid_params"
    OUT_OF_RANGE = "out_of_range"
    NO_FILE = "no_file"
    INVALID_EXTENSION = "invalid_extension"
    INVALID_SVG = "invalid_svg"
    TOO_LARGE = "too_large"
    INTERNAL_ERROR = "internal_error"
