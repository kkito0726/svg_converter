from flask import Flask, request
import os
import json
from service.converter_service import ConvertService
from flask_cors import CORS

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/svg2csv", methods=["POST"])
def upload_file():
    amc_data = request.form.get("amc_data")
    if amc_data:
        try:
            amc_data = json.loads(amc_data)
            power = amc_data["power"]
            speed = amc_data["speed"]

        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}, 400
    else:
        return {"error": "amc_data is required"}, 400

    return ConvertService.convert(float(power), int(speed)), 200


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
