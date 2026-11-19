
import os
import re
import requests

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")

@app.route("/script.js")
def javascript():
    return send_from_directory(BASE_DIR, "script.js")

@app.route("/check", methods=["POST"])
def check():

    api_url = os.environ.get("API_URL")
    api_key = os.environ.get("API_KEY")

    if not api_url or not api_key:
        return jsonify({"error": "API NOT CONFIGURED"}), 503

    data = request.get_json(silent=True) or {}
    phone = data.get("phone", "")

    if not isinstance(phone, str) or not re.fullmatch(r"\+[1-9]\d{7,14}", phone):
        return jsonify({"error": "INVALID NUMBER"}), 400

    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={"phone": phone},
            timeout=15
        )

        response.raise_for_status()
        result = response.json()

        banned = result.get("banned")

        if not isinstance(banned, bool):
            return jsonify({"error": "UNKNOWN API RESPONSE"}), 502

        return jsonify({"banned": banned})

    except requests.Timeout:
        return jsonify({"error": "API TIMEOUT"}), 504

    except (requests.RequestException, ValueError):
        return jsonify({"error": "API CONNECTION ERROR"}), 502

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
