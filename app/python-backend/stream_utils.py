import os
from typing import IO


def stream_size(stream: IO[bytes]) -> int:
    """読み取り位置を変えずにストリームのバイト数を返す"""
    position = stream.tell()
    size = stream.seek(0, os.SEEK_END)
    stream.seek(position)
    return size
