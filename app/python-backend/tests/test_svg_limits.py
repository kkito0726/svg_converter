import io
import json

import pytest

import svg2csv.svg as svg
from app import app

SVG_NS = 'xmlns="http://www.w3.org/2000/svg"'


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def post_svg(client, svg_bytes: bytes):
    return client.post(
        "/svg2csv",
        data={
            "file": (io.BytesIO(svg_bytes), "limits.svg"),
            "json_data": json.dumps({"power": 0.5, "speed": 2000}),
        },
        content_type="multipart/form-data",
    )


def single_path_svg(n_segments: int) -> bytes:
    d = "M0,0" + "L1,0" * n_segments
    return f'<svg {SVG_NS} width="10" height="10"><g><path d="{d}"/></g></svg>'.encode()


def many_paths_svg(n_paths: int) -> bytes:
    paths = '<path d="M0,0 L1,0"/>' * n_paths
    return f'<svg {SVG_NS} width="10" height="10"><g>{paths}</g></svg>'.encode()


def test_default_limits_leave_headroom_for_real_drawings():
    # 実データ (サンプルSVG: 要素 170 以下 / MEA11_CM: 813 線分) より十分大きい
    assert svg.MAX_ELEMENTS >= 50_000
    assert svg.MAX_SEGMENTS >= 200_000


def test_segments_at_limit_are_accepted(client, monkeypatch):
    monkeypatch.setattr(svg, "MAX_SEGMENTS", 10)
    assert post_svg(client, single_path_svg(10)).status_code == 200


def test_segments_over_limit_return_400(client, monkeypatch):
    monkeypatch.setattr(svg, "MAX_SEGMENTS", 10)
    res = post_svg(client, single_path_svg(11))
    assert res.status_code == 400
    assert "線分" in res.get_json()["error"]


def test_segment_limit_is_cumulative_across_paths(client, monkeypatch):
    monkeypatch.setattr(svg, "MAX_SEGMENTS", 10)
    assert post_svg(client, many_paths_svg(11)).status_code == 400


def test_elements_over_limit_return_400(client, monkeypatch):
    monkeypatch.setattr(svg, "MAX_ELEMENTS", 20)
    res = post_svg(client, many_paths_svg(30))
    assert res.status_code == 400
    assert "要素" in res.get_json()["error"]


def test_elements_at_limit_are_accepted(client, monkeypatch):
    # svg + g + 18 paths = 20 要素
    monkeypatch.setattr(svg, "MAX_ELEMENTS", 20)
    assert post_svg(client, many_paths_svg(18)).status_code == 200


@pytest.mark.parametrize(
    "d",
    [
        "M0,0 L1,0 L1,1 Z",
        "M0,0 1,0 1,1 2,2",  # M の後の暗黙の lineto
        "m0 0 h10 v10 h-10 z",
        "M0,0 C1,1 2,2 3,3 S5,5 6,6 Q7,7 8,8 T9,9",
        "M0,0 A5,5 0 0,1 10,10",
        "M1e2,-2.5.5.5L3-4",  # 指数・区切りなしの数値
    ],
)
def test_segment_estimate_is_an_upper_bound(d):
    from svgpathtools import parse_path

    assert svg.estimate_segments(d) >= len(parse_path(d))


def test_oversized_path_is_rejected_before_full_parse(client, monkeypatch):
    # 巨大な1本の path はパース (全線分オブジェクトの生成) 前に拒否する
    monkeypatch.setattr(svg, "MAX_SEGMENTS", 10)

    def fail_parse(_d):
        raise AssertionError("parse_path must not run for an oversized path")

    monkeypatch.setattr(svg, "parse_path", fail_parse)
    assert post_svg(client, single_path_svg(1000)).status_code == 400
