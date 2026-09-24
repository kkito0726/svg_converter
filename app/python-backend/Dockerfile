# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect python:<tag>
FROM python:3.12.14-slim-trixie@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9

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
