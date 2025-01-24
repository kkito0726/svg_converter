## 環境構築

### 1. inkscape のインストール

> [inkscape Software Installation](https://inkscape.org/release/inkscape-1.3/)

### 2. 拡張機能 (Axidraw)のインストール

> [Axidraw Software Installation](https://wiki.evilmadscientist.com/Axidraw_Software_Installation)

### 3. SVG Converterの環境構築

アプリケーションを docker-compose で動かす。

1. [Git install](https://qiita.com/T-H9703EnAc/items/4fbe6593d42f9a844b1c)
2. [Docker Desktop install](https://docs.docker.com/get-docker/)
3. Docker Desktop を起動した状態で、git bash (Git インストール時に同時に入る)で以下のコマンドを実行

初回のみ

```bash
mkdir ~/Workspace
cd ~/Workspace
git clone https://github.com/kkito0726/svg_converter.git
```

docker コンテナの起動

```bash
cd ~/Workspace/svg_converter/svg-converter-app
docker compose up -d --build
```

完了したら Docker Desktop の svg-converter-app の中の react-frontend の 4174:4173 と書いてあるリンクを押す (環境構築した後は常にここから起動)

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

1. アプリ左上のボタンから作成したSVGファイルをアップロードする
2. Power (W)とSpeed (μm/s)を入力してSubmitボタンを押す
3. 処理が終わると描画位置のグラフが出て、右下からCSVファイルをダウンロードできる
4. 過去に変換したファイルはDownloads画面からダウンロードできる。使わないファイルは定期的に削除する

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
## アップデート方法

```bash
cd ~/Workspace/svg_converter
git pull
cd ~/Workspace/svg_converter/svg-converter-app
docker compose up -d --build
```
