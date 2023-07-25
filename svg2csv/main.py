from svg import svg2csv

if __name__ == "__main__":
    filename = input("ファイルパスの入力: ")
    power = input("レーザーパワーの入力 (W): ")
    velocity = input("ステージの速度を入力 (μm/s): ")

    svg2csv(filename, float(power), int(velocity))
