import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

import pytest  # noqa: E402
import structlog  # noqa: E402
from structlog.testing import LogCapture  # noqa: E402


@pytest.fixture
def log_output():
    """structlog のログを dict のリストとして受け取る (request_id などの contextvars も含める)"""
    capture = LogCapture()
    original = structlog.get_config()
    structlog.configure(processors=[structlog.contextvars.merge_contextvars, capture])
    yield capture.entries
    structlog.configure(**original)
