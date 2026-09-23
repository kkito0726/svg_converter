import base64
import io
import json
import os
from glob import glob

import pytest

from app import app
from svg2csv.svg import convert_svg_csv
import pandas as pd

SVG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "svg")
SVG_FILES = sorted(glob(os.path.join(SVG_DIR, "*.svg")))
PNG_SIGNATURE = b"\x89PNG"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def post_svg(client, svg_bytes: bytes, filename="sample.svg", power=0.5, speed=2000):
    return client.post(
        "/svg2csv",
        data={
            "file": (io.BytesIO(svg_bytes), filename),
            "json_data": json.dumps({"power": power, "speed": speed}),
        },
        content_type="multipart/form-data",
    )


def test_sample_svgs_exist():
    assert SVG_FILES, "svg/ にサンプルSVGが見つかりません"


@pytest.mark.parametrize("svg_path", SVG_FILES, ids=os.path.basename)
def test_convert_returns_csv_and_plot_in_response(client, svg_path, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with open(svg_path, "rb") as f:
        res = post_svg(client, f.read(), os.path.basename(svg_path))

    assert res.status_code == 200
    body = res.get_json()
    stem = os.path.splitext(os.path.basename(svg_path))[0]
    assert body["csv_name"] == f"0.5W_2000_{stem}.csv"
    expected = pd.DataFrame(convert_svg_csv(svg_path, 0.5, 2000)).to_csv(header=False, index=False)
    assert body["csv_text"] == expected
    assert body["csv_text"].startswith("#power,0.5,,")
    assert base64.b64decode(body["plot_base64_image"]).startswith(PNG_SIGNATURE)
    # ステートレス: カレントディレクトリに何も書き出さない
    assert list(tmp_path.iterdir()) == []


def test_missing_file_returns_400(client):
    res = client.post(
        "/svg2csv",
        data={"json_data": json.dumps({"power": 0.5, "speed": 2000})},
        content_type="multipart/form-data",
    )
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_non_svg_extension_returns_400(client):
    assert post_svg(client, b"<svg/>", "image.png").status_code == 400


@pytest.mark.parametrize("power,speed", [(0, 2000), (1.5, 2000), (0.5, 0), (0.5, 10001)])
def test_out_of_range_params_return_400(client, power, speed):
    with open(SVG_FILES[0], "rb") as f:
        assert post_svg(client, f.read(), power=power, speed=speed).status_code == 400


def test_missing_json_data_returns_400(client):
    res = client.post(
        "/svg2csv",
        data={"file": (io.BytesIO(b"<svg/>"), "a.svg")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 400


def test_broken_svg_returns_400(client):
    assert post_svg(client, b"<svg><not-closed>").status_code == 400


def test_svg_without_group_returns_400(client):
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><path d="M0,0 L1,1"/></svg>'
    assert post_svg(client, svg).status_code == 400


def test_too_large_upload_returns_413(client, monkeypatch):
    monkeypatch.setitem(app.config, "MAX_CONTENT_LENGTH", 100)
    assert post_svg(client, b"x" * 1000).status_code == 413


def test_removed_storage_endpoints_are_gone(client):
    assert client.get("/all-csvs").status_code == 404
    assert client.delete("/csv").status_code == 404
