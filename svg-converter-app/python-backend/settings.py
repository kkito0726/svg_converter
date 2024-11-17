import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
if os.getenv("FLASK_ENV") == "docker":
    MINIO_HOST = os.environ.get("MINIO_HOST")
else:
    MINIO_HOST = os.environ.get("MINIO_LOCALHOST")
