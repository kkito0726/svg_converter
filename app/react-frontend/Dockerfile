# 成果物は静的ファイルなので、ビルドはホストのアーキテクチャで行う (arm64 の QEMU エミュレーションを避ける)
# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect <image>:<tag>
FROM --platform=$BUILDPLATFORM node:26.10.0-alpine@sha256:0b36e8c136b94cd4fcf02188228e76c31ad5872eef3fec8cbd2eee500cfd9e80 AS build

WORKDIR /usr/src/client

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# nginx は安定版 (stable) の系統を使う。1.27 系 (mainline) は 2025-06 にサポート終了
FROM nginx:1.31.0-alpine@sha256:2f07d83bf561b506400dc183b1b2003803e39efbd22451f848adaba14d28c7c7

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.inc /etc/nginx/conf.d/security-headers.inc
COPY --from=build /usr/src/client/dist /usr/share/nginx/html

EXPOSE 80
