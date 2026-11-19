import os
import re
import requests

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

API_URL = os.environ.get("API_URL")
API_KEY = os.environ.get("API_KEY")


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(".", "style.css")


@app.route("/script.js")
def javascript():
    return send_from_directory(".", "script.js")


@app.route("/check", methods=["POST"])
def check():

    if not API_URL or not API_KEY:
        return jsonify({
            "error": "API NOT CONFIGURED"
        }), 503

    data = request.get_json(silent=True) or {}

    phone = data.get("phone", "")

    if not isinstance(phone, str) or not re.fullmatch(
        r"\+[1-9]\d{7,14}", phone
    ):
        return jsonify({
            "error": "INVALID NUMBER"
        }), 400

    try:

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "phone": phone
            },
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        # Adaptasyon selon documentation de ton API.
        banned = result.get("banned")

        if not isinstance(banned, bool):
            return jsonify({
                "error": "INVALID API RESPONSE"
            }), 502

        return jsonify({
            "banned": banned
        })

    except requests.Timeout:

        return jsonify({
            "error": "API TIMEOUT"
        }), 504

    except (requests.RequestException, ValueError):

        return jsonify({
            "error": "API CONNECTION ERROR"
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
