# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect python:<tag>
FROM python:3.14.6-slim-trixie@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /usr/src/server

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ステートレス運用: 変換結果はメモリ上のみで扱い、ディスクには書き出さない
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 5001

# pyplot はスレッドセーフではないのでスレッドではなくプロセスで並列化する
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "--max-requests", "200", "--max-requests-jitter", "20", "app:app"]
