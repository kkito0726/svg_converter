import base64
import io
import time

import pytest
from PIL import Image

from converter.plot_csv import plot_csv
from converter.svg_converter import svg_converter

# Raspberry Pi でも余裕を持って返せる上限 (旧実装は 30,000 本で 1GB を超えて落ちていた)
MANY_LINES = 30_000
MAX_SECONDS = 5.0
IMAGE_SIZE = (1200, 1200)


def make_hatched_svg(n_lines: int) -> bytes:
    """ハッチング塗りつぶしを模した、短い水平線を大量に含むSVG"""
    paths = "".join(
        f'<path d="M{(i % 200) * 5},{i // 200 * 2} L{(i % 200) * 5 + 4},{i // 200 * 2}"/>'
        for i in range(n_lines)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400">'
        f"<g>{paths}</g></svg>"
    ).encode()


def to_csv_text(svg: bytes) -> str:
    return svg_converter(io.BytesIO(svg), 0.5, 2000)


def decode_png(image_base64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(image_base64)))


@pytest.mark.parametrize("color", ["gradation", "gray"])
def test_plot_returns_png_of_expected_size(color):
    image = decode_png(plot_csv(io.StringIO(to_csv_text(make_hatched_svg(50))), color))
    assert image.format == "PNG"
    assert image.size == IMAGE_SIZE


def test_plot_draws_lines_on_canvas():
    image = decode_png(plot_csv(io.StringIO(to_csv_text(make_hatched_svg(50))), "gradation"))
    # 背景の白以外の色 (描画された線) が含まれている
    colors = {c for _, c in image.convert("RGB").getcolors(maxcolors=1_000_000)}
    assert len(colors) > 10


def test_plot_handles_csv_without_lines():
    image = decode_png(plot_csv(io.StringIO("#power,0.5,,\n"), "gradation"))
    assert image.size == IMAGE_SIZE


def test_plot_many_lines_is_fast():
    csv_text = to_csv_text(make_hatched_svg(MANY_LINES))
    started = time.perf_counter()
    plot_csv(io.StringIO(csv_text), "gradation")
    assert time.perf_counter() - started < MAX_SECONDS
