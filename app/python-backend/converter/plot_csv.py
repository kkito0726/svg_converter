import base64
import io
import re
from typing import IO

import numpy as np
import pandas as pd
from matplotlib import colormaps, rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

FIGURE_SIZE_INCH = (12, 12)
GRADATION = "gradation"


def plot_csv(file_name: str | IO[str], color: str = "gray") -> str:
    """
    amc_plot用のcsvファイルを描画し、PNG画像をbase64文字列で返す
    file_name: csvファイル名、またはファイルオブジェクト
    color: 'gray'->灰色で表示（デフォルト）
           'gradation'->amc_plotの描画順に青から赤のグラデーションで表示
    """
    lines = read_lines(file_name)

    # 折線を1本ずつ plot すると本数に比例してメモリと時間を消費するため、
    # LineCollection でまとめて1つの描画オブジェクトとして扱う
    figure = Figure(figsize=FIGURE_SIZE_INCH)
    ax = figure.add_subplot(111)
    ax.set_aspect("equal")
    ax.add_collection(
        LineCollection(
            lines,
            colors=line_colors(len(lines), color),
            # plt.plot (Line2D) の既定値に合わせて見た目を従来と揃える
            linewidths=rcParams["lines.linewidth"],
            capstyle=rcParams["lines.solid_capstyle"],
            joinstyle=rcParams["lines.solid_joinstyle"],
        )
    )
    ax.autoscale_view()

    buf = io.BytesIO()
    FigureCanvasAgg(figure).print_png(buf)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def read_lines(file_name: str | IO[str]) -> list[np.ndarray]:
    """csvを読み込み、MLLL...と続く折線ごとの座標配列 (N×2) のリストを返す"""
    # コメント行と空行を読み飛ばす。
    data = pd.read_csv(
        file_name,
        names=["x", "y", "mode", "velocity"],
        dtype={"x": float, "y": float, "mode": str, "velocity": float},
        comment="#",
    ).dropna()

    # 'mode'列の文字を連結し、正規表現でひと続きの折線の範囲を抽出する。
    modes = "".join(data["mode"].tolist())
    xy = data[["x", "y"]].to_numpy()
    return [xy[start:end] for start, end in (m.span() for m in re.finditer(r"ML+", modes))]


def line_colors(n_lines: int, color: str):
    if color == GRADATION:  # 描画順に色にグラデーションをつける。
        return colormaps["jet"](np.arange(n_lines) / max(n_lines, 1))
    return color  # 単色で描画。
