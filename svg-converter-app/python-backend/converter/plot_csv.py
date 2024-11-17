import pandas as pd
import re, base64, io
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib

matplotlib.use("Agg")  # GUIバックエンドを使用しないように設定


# base64でグラフを変換する
def output_base64(func) -> str:
    def warapper(*args, **kwargs):
        buf = io.BytesIO()
        func(*args, *kwargs)

        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode("utf-8")

        return image_base64

    return warapper


@output_base64
def plot_csv(file_name: str, color="gray"):
    # amc_plot用のcsvファイルを描画する
    # file_name: csvファイル名
    # color: 'gray'->灰色で表示（デフォルト）
    #        'gradation'->amc_plotの描画順に青から赤のグラデーションで表示

    # amc_pltで描画するcsv形式のデータファイルを読み込む。
    # コメント行と空行を読み飛ばす。
    data = (
        pd.read_csv(
            file_name,
            names=["x", "y", "mode", "velocity"],
            dtype={"x": float, "y": float, "mode": str, "velocity": float},
            comment="#",
        )
        .dropna()
        .reset_index()
    )

    # 折線の座標を抽出する。
    # 'mode'列の文字を連結してmodesとしたのち、
    # 正規表現を用いてMLLL...となるひと続きの折線の座標を抽出する。
    modes = "".join(data["mode"].tolist())
    lines_span = [m.span() for m in re.finditer(r"ML+", modes)]
    lines = [data.loc[start : end - 1, "x":"y"].values.T for start, end in lines_span]

    # グラフを描画する。
    figure = plt.figure(figsize=(12, 12))
    ax = figure.add_subplot(111)
    ax.set_aspect("equal")

    if color == "gradation":  # 描画順に色にグラデーションをつける。
        [plt.plot(*xy, color=cm.jet(i / len(lines))) for i, xy in enumerate(lines)]
    else:  # 単色で描画。
        [plt.plot(*xy, color=color) for xy in lines]
