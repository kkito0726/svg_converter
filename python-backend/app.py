import json
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from service.converter_service import ConvertService
from service.csv_service import CsvService

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/svg2csv", methods=["POST"])
def upload_file():
    json_data = request.form.get("json_data")
    if json_data:
        try:
            json_data = json.loads(json_data)
            power = json_data["power"]
            speed = json_data["speed"]

        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}, 400
    else:
        return {"error": "amc_data is required"}, 400

    res = ConvertService.convert(float(power), int(speed))
    return (
        jsonify({"csv_url": res.csv_url, "plot_base64_image": res.plot_base64_image}),
        200,
    )


@app.route("/all-csvs", methods=["GET"])
def get_all_csvs():
    return jsonify(CsvService.get_csvs("./static")), 200


@app.route("/csv", methods=["DELETE"])
def delete_csv():
    json_data = request.get_json()
    CsvService.delete_csv(json_data["csv_name"])
    return "{}", 200


@app.route("/all-csvs", methods=["DELETE"])
def delete_all_csvs():
    CsvService.delete_all_csvs()
    return "{}", 200


CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:4173",
                "http://localhost:4174",
            ]
        }
    },
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
