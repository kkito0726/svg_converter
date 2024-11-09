from svgpy import SVGParser, PathParser, formatter
import pandas as pd
import os
import re
from typing import List


def svg2cmd(file_name: str) -> List[List[str]]:
    # svgデータから全ての線分または折れ線のノード座標を取り出して
    # 配列として返す関数

    # pathの座標データを取得
    parser = SVGParser()
    tree = parser.parse(file_name)
    root = tree.getroot()
    paths = root.get_elements_by_tag_name("path")

    commands = []
    for path in paths:
        path_txt = path.get_attribute("d")

        parser = SVGParser()
        new_path = parser.create_element_ns("http://www.w3.org/2000/svg", "path")

        path_data = PathParser.parse(path_txt)
        path.set_path_data(path_data)

        formatter.precision = 1

        normalized = PathParser.normalize(path_data)
        new_path.set_path_data(normalized)
        path_txt_normalized = new_path.get_attribute("d")
        commands.append(path_txt_normalized.split(" "))

    return commands


def svg2csv(file_name: str, power: float, velocity: int) -> None:
    # svgデータからamc_plot用の座標データを作成する関数
    # file_name: svgファイル（Inkscape上で全てのオブジェクトの
    #            グループ化を解除し、輪郭線などのベジエ曲線は除去しておくこと）
    # power: レーザーパワー[W]
    # velocity: 描画速度[um/s]（全ての線分で同じ描画速度となる
    #           ＝場所ごとに描画速度を変えたい場合は別ファイルを作る必要あり）

    parser = SVGParser()
    tree = parser.parse(file_name)
    root = tree.getroot()

    # 座標のずれを補正するためのパラメータを取得（グループ化解除していれば不要？）
    translate = root.get_elements_by_tag_name("g")[0].get_attribute("transform")
    if translate == None:
        translate = [0, 0]
    else:
        translate = re.split("[(),]", translate)[1:3]
        translate = [item if item else "0" for item in translate]
        translate = [float(i) for i in translate]

    width = float(root.get_elements_by_tag_name("svg")[0].attrib["width"])
    height = float(root.get_elements_by_tag_name("svg")[0].attrib["height"])

    # power設定
    data = []
    data.append(["#power", power, "", ""])

    # 描画データの変換
    paths = svg2cmd(file_name)

    for path in paths:
        for command in path:
            if command[0] == "M":
                mode = "M"
                x, y = [float(i) for i in command[1:].split(",")]
                x0, y0 = x, y
            elif command[0] == "L":
                mode = "L"
                x, y = [float(i) for i in command[1:].split(",")]
            elif command[0] == "Z":
                mode = "L"
                x, y = x0, y0
            else:
                mode = "L"
                x, y = [float(i) for i in command[:].split(",")]

            x, y = x + translate[0] - width / 2, y + translate[1] - height / 2
            # InkscapeとAMCでは座標系が天地逆なのを修正
            # Inkscapeは左上が原点でy軸は下向き
            # amc_plotは左下が原点でy軸は上向き
            # data.append([x, y, mode, velocity])
            data.append([x, -y, mode, velocity])

        data.append(["", "", "", ""])

    # ファイルの書き出し
    out_name = os.path.splitext(file_name)[0] + ".csv"
    pd.DataFrame(data).to_csv(out_name, header=False, index=False)
