# 成果物は静的ファイルなので、ビルドはホストのアーキテクチャで行う (arm64 の QEMU エミュレーションを避ける)
# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect <image>:<tag>
FROM --platform=$BUILDPLATFORM node:24.22.1-alpine@sha256:06d7adf3e0ef61a13f1d28682726366f97a15aa1888c934d3ecec86c33918b53 AS build

WORKDIR /usr/src/client

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# nginx は安定版 (stable) の系統を使う。1.27 系 (mainline) は 2025-06 にサポート終了
FROM nginx:1.30.5-alpine@sha256:bf3201ab56f23e5954646379c775d511fc466e9f11376d9725361064ad07ed35

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.inc /etc/nginx/conf.d/security-headers.inc
COPY --from=build /usr/src/client/dist /usr/share/nginx/html

EXPOSE 80
