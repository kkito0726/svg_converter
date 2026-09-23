import json
import logging
import os
from dataclasses import asdict

from flask import Flask, jsonify, request
from svg2csv.svg import InvalidSvgError
from werkzeug.exceptions import HTTPException
from service.converter_service import ConvertService

POWER_RANGE = (0.01, 1.22)
SPEED_RANGE = (1, 10000)
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "20"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


class RequestError(ValueError):
    pass


def parse_params(raw_json: str | None) -> tuple[float, int]:
    if not raw_json:
        raise RequestError("json_data is required")
    try:
        params = json.loads(raw_json)
        power = float(params["power"])
        speed = int(params["speed"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        raise RequestError("power / speed の形式が不正です") from e

    if not POWER_RANGE[0] <= power <= POWER_RANGE[1]:
        raise RequestError(f"power は {POWER_RANGE[0]}-{POWER_RANGE[1]} W の範囲で指定してください")
    if not SPEED_RANGE[0] <= speed <= SPEED_RANGE[1]:
        raise RequestError(f"speed は {SPEED_RANGE[0]}-{SPEED_RANGE[1]} μm/s の範囲で指定してください")
    return power, speed


def get_svg_file():
    file = request.files.get("file")
    if file is None or not file.filename:
        raise RequestError("SVGファイルが選択されていません")
    if not file.filename.lower().endswith(".svg"):
        raise RequestError("SVGファイル(.svg)を選択してください")
    return file


@app.route("/svg2csv", methods=["POST"])
def upload_file():
    try:
        power, speed = parse_params(request.form.get("json_data"))
        file = get_svg_file()
        res = ConvertService.convert(file.stream, file.filename, power, speed)
    except (RequestError, InvalidSvgError) as e:
        return jsonify({"error": str(e)}), 400
    except HTTPException:
        raise
    except Exception:
        logging.exception("SVG conversion failed")
        return jsonify({"error": "変換中にエラーが発生しました"}), 500

    return jsonify(asdict(res)), 200


@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": f"ファイルサイズは {MAX_UPLOAD_MB}MB 以下にしてください"}), 413


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
