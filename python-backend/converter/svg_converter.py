import os

import pandas as pd
from svg2csv.svg import convert_svg_csv


def svg_converter(file_name: str, power: float, velocity: int) -> str:
    data = convert_svg_csv(file_name, power, velocity)

    out_name = os.path.splitext(os.path.basename(file_name))[0]
    out_csv_path = f"./static/{power}W_{velocity}_{out_name}.csv"
    pd.DataFrame(data).to_csv(out_csv_path, header=False, index=False)

    return out_csv_path
