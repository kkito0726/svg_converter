# 成果物は静的ファイルなので、ビルドはホストのアーキテクチャで行う (arm64 の QEMU エミュレーションを避ける)
# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect <image>:<tag>
FROM --platform=$BUILDPLATFORM node:24.22.2-alpine@sha256:8a32c8cf649a49915a66e81e7a609223c708d0adabf288ee3f4077d765542f85 AS build

WORKDIR /usr/src/client

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# nginx は安定版 (stable) の系統を使う。1.27 系 (mainline) は 2025-06 にサポート終了
FROM nginx:1.30.6-alpine@sha256:0e52bd054126cdc040b1276c0af347aeb02a41b9cfe305d6094767ac30e97949

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.inc /etc/nginx/conf.d/security-headers.inc
COPY --from=build /usr/src/client/dist /usr/share/nginx/html

EXPOSE 80
