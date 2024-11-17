import io
from s3 import minio_client
from urllib.parse import urlparse

BUCKET_NAME = "output_csv"


class MinioRepository:
    @staticmethod
    def save_csv(csv_buf: io.StringIO, csv_name):
        ensure_bucket_exists(BUCKET_NAME)
        minio_client.put_object(
            BUCKET_NAME,
            csv_name,
            csv_buf,
            length=len(csv_buf.getvalue()),
            content_type="text/csv",
        )

        csv_url = f"http://localhost:9003/{BUCKET_NAME}/{csv_name}"
        return csv_url


def ensure_bucket_exists(bucket_name):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)


def extract_bucket_and_object(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        raise ValueError(
            "Invalid URL scheme. Only 'http' and 'https' schemes are supported."
        )

    parts = parsed_url.path.split("/", 2)
    if len(parts) < 3:
        raise ValueError("Invalid URL format. Bucket name and object name are missing.")

    bucket_name = parts[1]
    object_name = parts[2]

    return bucket_name, object_name
