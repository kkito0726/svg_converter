# 成果物は静的ファイルなので、ビルドはホストのアーキテクチャで行う (arm64 の QEMU エミュレーションを避ける)
FROM --platform=$BUILDPLATFORM node:22-alpine AS build

WORKDIR /usr/src/client

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY security-headers.inc /etc/nginx/conf.d/security-headers.inc
COPY --from=build /usr/src/client/dist /usr/share/nginx/html

EXPOSE 80
