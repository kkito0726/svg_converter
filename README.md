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

Google colaboratory で以下を実行

```python
# パッケージのインストール
!pip install git+https://github.com/miute/svgpy
!pip install git+https://github.com/kkito0726/svg_converter.git
```

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

---

### 3. Raspberry pi で実行する

2 で出力された CSV ファイルを raspberry pi の任意のフォルダに転送して、ターミナルで目的のファイルの改装まで cd コマンドで移動し以下のコマンドを実行

```bash
$ amc_plt csv_fileのパス　-c
```

## -c は MEA 電極基板で位置合わせするときにつけるオプション。35 mm dish 等に加工する場合はいらない。

### 4. Raspberry pi のシャットダウン

シャットダウンする場合は以下のコマンドを実行する。

```bash
$ sudo shutdown -h now
```
