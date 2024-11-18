from flask import Flask, request, jsonify
import os
import json
from service.converter_service import ConvertService
from flask_cors import CORS

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
