FROM python:3.12-slim

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
