# ベースイメージはバージョンと digest で固定する (タグの付け替えで意図しない/悪意のある版が入らないように)。
# 更新するときは新しいタグの digest を確認してから書き換える: docker buildx imagetools inspect python:<tag>
FROM python:3.12.14-slim-trixie@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f

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

# worker 数やログ設定は gunicorn.conf.py を参照
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
