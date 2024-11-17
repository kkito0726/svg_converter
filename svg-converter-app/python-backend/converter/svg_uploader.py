from flask import request
import os

UPLOAD_FOLDER = "./uploads"


def svg_upload() -> str:
    # ファイルを取得
    if "file" not in request.files:
        return ""

    file = request.files["file"]
    if file.filename == "":
        return ""

    if not file.filename.endswith(".svg"):
        return ""

    # ファイルを保存
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return filepath
