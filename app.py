from flask import Flask, request, jsonify
import subprocess
from pathlib import Path
import configparser

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.ini"

@app.route("/")
def home():
    return "✅ Automation Web App is Running"

@app.route("/run_estamp", methods=["POST"])
def run_estamp():
    data = request.json
    update_config_dates(data["start_date"], data["end_date"])
    subprocess.run(["python", str(BASE_DIR / "download_estamp_v1.05.py")])
    return jsonify({"status": "E-Stamp download complete"})

@app.route("/run_receipt", methods=["POST"])
def run_receipt():
    data = request.json
    update_config_dates(data["start_date"], data["end_date"])
    subprocess.run(["python", str(BASE_DIR / "download_receipt_v1.05.py")])
    return jsonify({"status": "Receipt download complete"})

@app.route("/merge_files", methods=["POST"])
def merge_files():
    subprocess.run(["python", str(BASE_DIR / "merge_files_v1.02.py")])
    return jsonify({"status": "Merge complete"})

def update_config_dates(start, end):
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config["dates"]["start_date"] = start
    config["dates"]["end_date"] = end
    with open(CONFIG_PATH, "w") as f:
        config.write(f)

if __name__ == "__main__":
    app.run(debug=True)