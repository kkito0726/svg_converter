import os

from svg2csv.plot import plot_csv
from svg2csv.svg import svg2csv

if __name__ == "__main__":
    filename = input("ファイルパスの入力: ")
    power = input("レーザーパワーの入力 (W): ")
    velocity = input("ステージの速度を入力 (μm/s): ")

    svg2csv(filename, float(power), int(velocity))
    csv_path = os.path.splitext(filename)[0] + ".csv"
    plot_csv(csv_path, color="gradation")
