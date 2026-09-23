import xml.etree.ElementTree as ET
from svgpathtools import parse_path
import pandas as pd
import os, re


NAMESPACES = {"svg": "http://www.w3.org/2000/svg"}

# 1リクエストで処理する量の上限。匿名アップロードで共有ワーカーのメモリを使い切らせないため。
# 実データ (要素数百・線分数千程度) より十分大きく、ワーカー1つのメモリの取り分には収まる値にする。
MAX_ELEMENTS = 50_000
MAX_SEGMENTS = 200_000

_PATH_TOKEN_RE = re.compile(r"[A-Za-z]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
# 1線分あたりに必要な数値の個数。円弧はフラグが連結 ("01") されうるので少なめに数えて上限側に倒す。
_ARGS_PER_SEGMENT = {"m": 2, "l": 2, "t": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "a": 5}


def estimate_segments(d: str, limit: int | None = None) -> int:
    """path の d 属性を線分オブジェクトを作らずに走査し、線分数の上限値を見積もる"""
    segments = 0
    command, args, is_moveto = None, 0, False
    for match in _PATH_TOKEN_RE.finditer(d):
        token = match.group()
        if token.isalpha():
            command, args = token.lower(), 0
            is_moveto = command == "m"
            if command == "z":
                segments += 1
        elif command in _ARGS_PER_SEGMENT:
            args += 1
            if args == _ARGS_PER_SEGMENT[command]:
                args = 0
                if is_moveto:
                    is_moveto = False  # 最初の座標は移動のみ。以降の組は暗黙の lineto
                else:
                    segments += 1
        if limit is not None and segments > limit:
            break
    return segments


class InvalidSvgError(ValueError):
    """変換できないSVGが渡されたときの例外"""


def svg2cmd(file_name) -> list[list[str]]:
    """
    SVGデータからすべての線分または折れ線のノード座標を取得して配列として返す。

    Parameters:
        file_name: SVGファイルのパス、またはファイルオブジェクト。

    Returns:
        List[List[str]]: 各pathのコマンドリスト。
    """
    return _root2cmd(ET.parse(file_name).getroot())


def _root2cmd(root: ET.Element) -> list[list[str]]:
    namespaces = NAMESPACES

    # <path>要素を取得
    paths = root.findall(".//svg:path", namespaces)
    commands = []
    total_segments = 0

    for path in paths:
        d_attr = path.attrib.get("d")
        if not d_attr:
            continue

        # 巨大な path で線分オブジェクトを大量に作る前に、見積もりで打ち切る
        remaining = MAX_SEGMENTS - total_segments
        if estimate_segments(d_attr, limit=remaining) > remaining:
            raise InvalidSvgError(f"線分が多すぎます (上限 {MAX_SEGMENTS:,} 本)")

        # `d`属性をパース
        path_obj = parse_path(d_attr)
        total_segments += len(path_obj)
        if total_segments > MAX_SEGMENTS:
            raise InvalidSvgError(f"線分が多すぎます (上限 {MAX_SEGMENTS:,} 本)")
        normalized_commands = []

        for segment in path_obj:
            start = segment.start
            end = segment.end

            normalized_commands.append(
                f"M{round(start.real, 1)},{round(start.imag, 1)}"
            )

            normalized_commands.append(f"L{round(end.real, 1)},{round(end.imag, 1)}")

        commands.append(normalized_commands)

    return commands


def _parse_root(source) -> ET.Element:
    """要素数を数えながらパースし、上限を超えた時点で打ち切る"""
    try:
        parser = ET.iterparse(source, events=("start",))
        for count, _ in enumerate(parser, start=1):
            if count > MAX_ELEMENTS:
                raise InvalidSvgError(f"SVGの要素が多すぎます (上限 {MAX_ELEMENTS:,} 個)")
        return parser.root
    except ET.ParseError as e:
        raise InvalidSvgError("SVGファイルを解析できません") from e


def convert_svg_csv(file_name, power: float, velocity: int):
    """
    SVGデータからAMCプロット用の座標データを作成する関数
    file_name: SVGファイルのパス、またはファイルオブジェクト
    """
    # SVGファイルをパースして変換 (ストリームも扱えるようにパースは1回だけ)
    root = _parse_root(file_name)
    namespaces = NAMESPACES

    # translate情報を取得
    group = root.find(".//svg:g[svg:path]", namespaces)
    if group is None:
        raise InvalidSvgError("path を含むレイヤー(g要素)が見つかりません")
    transform = group.attrib.get("transform", "")
    if transform:
        translate = re.split("[(),]", transform)[1:3]
        translate = [float(item) if item else float(0) for item in translate]
    else:
        translate = [0., 0.]

    # SVG全体のサイズを取得
    try:
        width = float(root.attrib["width"])
        height = float(root.attrib["height"])
    except (KeyError, ValueError) as e:
        raise InvalidSvgError("SVGのwidth/height属性を数値として読めません") from e

    # power設定
    data = []
    data.append(["#power", power, "", ""])

    # 描画データ変換
    paths = _root2cmd(root)
    for path in paths:
        for command in path:
            x, y = [float(i) for i in command[1:].split(",")]
            mode = "M" if command[0] == "M" else "L"
            x, y = x + translate[0] - width / 2, y + translate[1] - height / 2
            # InkscapeとAMCでは座標系が天地逆なのを修正
            # Inkscapeは左上が原点でy軸は下向き
            # amc_plotは左下が原点でy軸は上向き
            # data.append([x, y, mode, velocity])
            data.append([x, -y, mode, velocity])

        data.append(["", "", "", ""])

    return data


def svg2csv(file_name: str, power: float, velocity: int) -> None:
    data = convert_svg_csv(file_name, power, velocity)
    out_name = os.path.splitext(file_name)[0] + ".csv"
    pd.DataFrame(data).to_csv(out_name, header=False, index=False)
