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

docker コンテナの起動 (GitHub Actions でビルド済みのイメージを ghcr.io から取得する)

```bash
cd ~/Workspace/svg_converter
docker compose pull
docker compose up -d
```

完了したらブラウザで http://localhost:4174 を開く (Docker Desktop の svg_converter の中の react-frontend の 4174:80 と書いてあるリンクからも開ける)

#### 開発時 (ローカルのソースからビルドする)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

#### 自宅サーバー (Raspberry Pi 5) で Cloudflare Tunnel を使って公開する

1. Cloudflare Zero Trust > Networks > Tunnels でトンネルを作成し、トークンを控える
2. トンネルの Public Hostname を追加し、Service に `http://react-frontend:80` を指定する
3. サーバー上で `.env.example` を `.env` にコピーし、`CLOUDFLARE_TUNNEL_TOKEN` を設定する
4. 起動

```bash
docker compose -f docker-compose.yml -f docker-compose.deploy.yml pull
docker compose -f docker-compose.yml -f docker-compose.deploy.yml up -d
```

- アプリに認証機能はないため、利用者を限定する場合は Cloudflare Access でアクセス制限をかける
- この構成ではホストのポート (4174) を公開しない。アクセスは Tunnel 経由のみ (Access を迂回させないため)。Docker Compose v2.24 以降が必要 (`docker compose version` で確認)
- 1 回の変換で扱える量には上限がある (SVG の要素 50,000 個・線分 200,000 本)。超えると 400 エラーになる
- 変換 API は nginx でレート制限 (1 IP あたり 20 回/分) をかけている
- `.env` はトークンを含むため Git の管理対象外 (`.gitignore` 済み)。コミットしないこと
- 変換結果はディスクに保存しないため、ボリュームやファイル削除の運用は不要

### イメージの公開 (GitHub Actions)

`main` へのマージ (`app/` 配下の変更時) でのみ、`.github/workflows/docker-publish.yml` がテスト後に
amd64 / arm64 のイメージをビルドして ghcr.io に公開する。PR ではテストのみ実行する。

- `ghcr.io/kkito0726/svg-converter-backend`
- `ghcr.io/kkito0726/svg-converter-frontend`

タグは `latest` と `sha-<短縮SHA>`。特定のバージョンに固定する場合は `.env` に `IMAGE_TAG` を設定する。

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

1. 「01 · Input」の枠に作成した SVG ファイルをドラッグ&ドロップする (クリックしてファイルを選択してもよい)。読み込んだファイルはサムネイル・ファイル名・サイズ付きで表示される
2. 「02 · Parameters」でレーザーパワー (W) とステージ速度 (μm/s) を入力して「CSVに変換」を押す
3. 変換が終わると描画順 (青→赤) のプレビューが表示され、「CSVをダウンロード」から CSV を保存できる

> サーバーは変換結果を一切保存しない（ステートレス）。ダウンロードURLはブラウザ内だけで有効な一時URLなので、
> ページを再読み込みしたり次の変換を実行すると消える。必要なCSVはその場でダウンロードしておくこと。

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

研究室の PC などで使う場合

```bash
cd ~/Workspace/svg_converter
git pull
docker compose pull
docker compose up -d
```

自宅サーバー (Cloudflare Tunnel で公開している場合)

```bash
cd ~/Workspace/svg_converter
git pull
docker compose -f docker-compose.yml -f docker-compose.deploy.yml pull
docker compose -f docker-compose.yml -f docker-compose.deploy.yml up -d
```
