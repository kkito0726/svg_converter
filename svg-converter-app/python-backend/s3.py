from minio import Minio
import settings

minio_client = Minio(
    settings.MINIO_HOST,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)
