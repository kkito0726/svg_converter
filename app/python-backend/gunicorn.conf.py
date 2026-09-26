import os
import sys

# gunicorn コマンドから起動すると sys.path にこのディレクトリが入らないため追加する
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logging_config import build_logging_dict, load_settings  # noqa: E402

bind = "0.0.0.0:5001"
# pyplot はスレッドセーフではないのでスレッドではなくプロセスで並列化する
workers = 2
timeout = 120
max_requests = 200
max_requests_jitter = 20

# アクセスログはアプリの request.completed で出すので gunicorn 側では出さない
# (logconfig_dict 使用時は gunicorn.access ロガーのレベルで止めている: logging_config.py)
accesslog = None
# gunicorn 自身のログもアプリと同じ形式 (docs/logging-design.md) で stdout に出す
logconfig_dict = build_logging_dict(load_settings(os.environ))
