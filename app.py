
import os
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory

# CONFIGURATION FLASK
app = Flask(__name__, static_folder=None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logging.basicConfig(level=logging.INFO)

# BANCHECK API
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


# STATIC FILES: IMAGES
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


# HEALTH CHECK
@app.route("/health")
def health():
    image_path = os.path.join(STATIC_DIR, "klaus-bg.JPG")

    return jsonify({
        "status": "online",
        "static_folder_exists": os.path.isdir(STATIC_DIR),
        "image_exists": os.path.isfile(image_path),
        "static_files": os.listdir(STATIC_DIR)
            if os.path.isdir(STATIC_DIR) else []
    })


# CHECK PHONE NUMBER
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


# START SERVER
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )



