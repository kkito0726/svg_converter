import xml.etree.ElementTree as ET
from svgpathtools import parse_path
import pandas as pd
import os, re


def svg2cmd(file_name: str) -> list[list[str]]:
    """
    SVGデータからすべての線分または折れ線のノード座標を取得して配列として返す。

    Parameters:
        file_name (str): SVGファイルのパス。

    Returns:
        List[List[str]]: 各pathのコマンドリスト。
    """
    # SVGファイルのパース
    tree = ET.parse(file_name)
    root = tree.getroot()
    namespaces = {"svg": "http://www.w3.org/2000/svg"}

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


def convert_svg_csv(file_name: str, power: float, velocity: int):
    """
    SVGデータからAMCプロット用の座標データを作成する関数
    """
    # SVGファイルをパースして変換
    tree = ET.parse(file_name)
    root = tree.getroot()
    namespaces = {"svg": "http://www.w3.org/2000/svg"}

    # translate情報を取得
    transform = root.find(".//svg:g", namespaces).attrib.get("transform", "")
    translate = re.split("[(),]", transform)[1:3]
    translate = [float(item) if item else float(0) for item in translate]

    # SVG全体のサイズを取得
    svg_elem = root.find(".//svg:svg", namespaces)
    width = float(root.attrib["width"])
    height = float(root.attrib["height"])

    # 描画データ変換
    paths = svg2cmd(file_name)
    data = []
    data.append(["#power", power, "", ""])  # Power設定

    for path in paths:
        for command in path:
            if command.startswith("M"):  # 移動
                x, y = map(float, command[1:].split(","))
                x0, y0 = x, y
            elif command.startswith("L"):  # 直線
                x, y = map(float, command[1:].split(","))
            elif command.startswith("Z"):  # 終端
                x, y = x0, y0
            else:
                x, y = map(float, command.split(","))

            # translateを適用し、中心座標を補正
            x = x + translate[0] - width / 2
            y = y + translate[1] - height / 2

            # y座標系をAMCに合わせる
            data.append([x, -y, "L", velocity])

        # 空行でパスを区切る
        data.append(["", "", "", ""])

    # CSVとして保存
    return os.path.splitext(file_name)[0] + ".csv", data


def svg2csv(file_name: str, power: float, velocity: int) -> None:
    out_name, data = convert_svg_csv(file_name, power, velocity)
    pd.DataFrame(data).to_csv(out_name, header=False, index=False)
