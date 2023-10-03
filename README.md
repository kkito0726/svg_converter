## 環境構築

### 1. inkscape のインストール

> [inkscape Software Installation](https://inkscape.org/release/inkscape-1.3/)

### 2. 拡張機能 (Axidraw)のインストール

> [Axidraw Software Installation](https://wiki.evilmadscientist.com/Axidraw_Software_Installation)

## 使い方

### 1. inkscape の使い方

- AMC で塗りつぶしたい範囲を図形を使って作る。
- 図形の塗りつぶしは白にしておき、オブジェクトは Path に変換しておく
- エクステンション > EggBot > Hatch fill...でウィンドウを出して線の間隔等調節して、横線で埋める。
- 曲線は Stage Controller で制御できないため消しておく(横線の間隔を狭くすることで曲線を表現できる)。
- グループ化はすべて解除して、一つの Layer に Path が存在している状態にしておく。
- 画像の中心が原点になるので

---

### 2. SVG ファイルを CSV へ変換

- Google Drive のマイドライブ直下に細胞班共有ドライブに入っている svgpy フォルダをダウンロードする。

Google colaboratory で以下を実行

```python
# パッケージのインストール
!pip install git+https://github.com/kkito0726/svg_converter.git
!pip install cssselect

# ディレクトリの移動
%cd ./drive/MyDrive/
```

### 電極と一緒にプロット

```python
from svg2csv import *
import os

filename = input("ファイルパスの入力: ")
power = input("レーザーパワーの入力 (W): ")
velocity = input("ステージの速度を入力 (μm/s): ")

# CSVへ変換
svg2csv(filename, float(power), int(velocity))

# 結果をプロット
csv_path = os.path.splitext(filename)[0] + ".csv"
plot_csv(csv_path, color="gradation")
```

```python
import pandas as pd
import matplotlib.pyplot as plt
import re

def read_plot_csv(csv_path: str):
    data = (
        pd.read_csv(
            csv_path,
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

    return lines

electrode = read_plot_csv("/content/drive/MyDrive/研究/inkscape/515/515_electrode_hatch.csv")
glass = read_plot_csv("/content/drive/MyDrive/研究/inkscape/515/後加工/515_electrode_add_process.csv")

# グラフを描画する。
figure = plt.figure(figsize=(12, 12))
ax = figure.add_subplot(111)
ax.set_aspect("equal")

[plt.plot(*xy, color="gray") for xy in electrode]
[plt.plot(*xy, color="red") for xy in glass]

plt.show()
```

---

### 3. Raspberry pi で実行する

2 で出力された CSV ファイルを raspberry pi の任意のフォルダに転送して、ターミナルで目的のファイルの改装まで cd コマンドで移動し以下のコマンドを実行

```bash
$ amc_plt csv_fileのパス　-c
```

-c は MEA 電極基板で位置合わせするときにつけるオプション。35 mm dish 等に加工する場合はいらない。

### 4. Raspberry pi のシャットダウン

シャットダウンする場合は以下のコマンドを実行する。

```bash
$ sudo shutdown -h now
```
