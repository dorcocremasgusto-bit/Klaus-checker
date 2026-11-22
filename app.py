

import os
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logging.basicConfig(level=logging.INFO)

API_URL = "https://baron0.com/api/v2/check"
API_KEY = os.environ.get("BANCHECK_API_KEY", "")


# PAGE PRINCIPALE
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# CSS
@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")


# JAVASCRIPT
@app.route("/script.js")
def javascript():
    return send_from_directory(BASE_DIR, "script.js")


# IMAGES ET FICHIERS STATIC
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


# HEALTH CHECK
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "application": "KLAUS CHECKER",
        "api_configured": bool(API_KEY)
    })


# VERIFICATION DU NUMERO
@app.route("/check", methods=["POST"])
def check():

    if not API_KEY:
        return jsonify({
            "error": "BANCHECK API KEY NOT CONFIGURED"
        }), 503

    data = request.get_json(silent=True) or {}
    number = data.get("number")

    if not isinstance(number, str):
        return jsonify({
            "error": "NUMBER REQUIRED"
        }), 400

    number = number.strip()

    if not number.startswith("+"):
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
            json={"number": number},
            timeout=20
        )

        logging.info(
            "BanCheck HTTP status: %s",
            response.status_code
        )

        try:
            body = response.json()
        except ValueError:
            return jsonify({
                "error": "INVALID API RESPONSE"
            }), 502

        if response.status_code != 200:
            return jsonify({
                "error": "BANCHECK API ERROR",
                "status": response.status_code
            }), 502

        banned = body.get("banned")

        if not isinstance(banned, bool):
            return jsonify({
                "error": "UNKNOWN NUMBER STATUS"
            }), 502

        return jsonify({
            "banned": banned,
            "reason": body.get("reason")
        })

    except requests.Timeout:
        return jsonify({
            "error": "API TIMEOUT"
        }), 504

    except requests.RequestException:
        logging.exception("BanCheck connection error")
        return jsonify({
            "error": "API CONNECTION ERROR"
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
