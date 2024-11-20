# SVG Converter

インクスケープで作成した SVG ファイルを AMC 描画用の CSV ファイルに変換するアプリ

## 1. 環境構築

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

svg_converter/svg-converter-app/python-backend の中に細胞班共有フォルダにある svgpy ファルダをコピーしてくる

```
--- svg_converter
    --- svg-converter-app
        --- python-backend
            --- svgpy
```

docker コンテナの起動

```bash
cd ~Workspace/svg_converter/svg-converter-app
docker compose up -d --build
```

完了したら Docker Desktop の svg-converter-app の中の react-frontend の再生ボタンを押す (環境構築移行は常にここから起動)

アップデート方法

```bash
cd ~Workspace/svg_converter
git pull
cd ~Workspace/svg_converter/svg-converter-app
docker compose up -d --build
```
