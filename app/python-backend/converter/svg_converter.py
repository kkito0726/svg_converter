import os
from typing import IO

import pandas as pd
from svg2csv.svg import convert_svg_csv


def svg_converter(svg_stream: IO[bytes], power: float, velocity: int) -> str:
    """SVGを読み込み、AMCプロット用CSVの文字列を返す (ファイルには書き出さない)"""
    data = convert_svg_csv(svg_stream, power, velocity)
    return pd.DataFrame(data).to_csv(header=False, index=False)


def csv_file_name(svg_file_name: str, power: float, velocity: int) -> str:
    stem = os.path.splitext(os.path.basename(svg_file_name))[0]
    return f"{power}W_{velocity}_{stem}.csv"
