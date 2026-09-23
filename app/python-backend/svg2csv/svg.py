import xml.etree.ElementTree as ET
from svgpathtools import parse_path
import pandas as pd
import os, re


NAMESPACES = {"svg": "http://www.w3.org/2000/svg"}


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

    for path in paths:
        d_attr = path.attrib.get("d")
        if not d_attr:
            continue

        # `d`属性をパース
        path_obj = parse_path(d_attr)
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


def convert_svg_csv(file_name, power: float, velocity: int):
    """
    SVGデータからAMCプロット用の座標データを作成する関数
    file_name: SVGファイルのパス、またはファイルオブジェクト
    """
    # SVGファイルをパースして変換 (ストリームも扱えるようにパースは1回だけ)
    try:
        root = ET.parse(file_name).getroot()
    except ET.ParseError as e:
        raise InvalidSvgError("SVGファイルを解析できません") from e
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
