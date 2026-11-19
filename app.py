
import os
import re
import logging
import requests

from flask import Flask, request, jsonify, send_from_directory

# =====================================
# KLAUS CHECKER V2
# POWERED BY KLAUSDEV
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

API_URL = os.environ.get("API_URL", "").strip()
API_KEY = os.environ.get("API_KEY", "").strip()

TIMEOUT = 15


# =====================================
# FRONTEND ROUTES
# =====================================

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(BASE_DIR, "style.css")


@app.route("/script.js")
def javascript():
    return send_from_directory(BASE_DIR, "script.js")


# =====================================
# HEALTH CHECK
# =====================================

@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "application": "KLAUS CHECKER",
        "version": "2.0",
        "api_configured": bool(API_URL and API_KEY)
    })


# =====================================
# WHATSAPP NUMBER CHECK
# =====================================

@app.route("/check", methods=["POST"])
def check():

    # Check API configuration

    if not API_URL or not API_KEY:

        return jsonify({
            "success": False,
            "error": "API NOT CONFIGURED"
        }), 503

    # Read request

    data = request.get_json(silent=True) or {}

    phone = data.get("phone", "")

    # Validate phone number

    if not isinstance(phone, str):

        return jsonify({
            "success": False,
            "error": "INVALID PHONE NUMBER"
        }), 400

    phone = phone.strip()

    if not re.fullmatch(r"\+[1-9]\d{7,14}", phone):

        return jsonify({
            "success": False,
            "error": "INVALID PHONE NUMBER"
        }), 400

    # Connect to API

    try:

        logging.info("KLAUS CHECKER: API request started")

        response = requests.post(
            API_URL,

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            json={
                "phone": phone
            },

            timeout=TIMEOUT
        )

        logging.info(
            "KLAUS CHECKER: API HTTP %s",
            response.status_code
        )

        # Authentication errors

        if response.status_code in (401, 403):

            return jsonify({
                "success": False,
                "error": "API AUTHENTICATION FAILED"
            }), 502

        # Other HTTP errors

        response.raise_for_status()

        # Decode JSON

        try:

            api_result = response.json()

        except ValueError:

            logging.error("API returned invalid JSON")

            return jsonify({
                "success": False,
                "error": "INVALID API JSON"
            }), 502

        # Validate API response

        if not isinstance(api_result, dict):

            return jsonify({
                "success": False,
                "error": "INVALID API RESPONSE"
            }), 502

        # Expected API format:
        # {"banned": true}
        # {"banned": false}

        banned = api_result.get("banned")

        if not isinstance(banned, bool):

            logging.error(
                "Unsupported API response fields: %s",
                list(api_result.keys())
            )

            return jsonify({
                "success": False,
                "error": "API RESPONSE FORMAT NOT SUPPORTED"
            }), 502

        # Return confirmed status

        return jsonify({
            "success": True,
            "phone": phone,
            "banned": banned,
            "message": (
                "NUMÉRO BANNI"
                if banned
                else "NUMÉRO NON BANNI"
            )
        }), 200

    except requests.Timeout:

        logging.error("KLAUS CHECKER: API timeout")

        return jsonify({
            "success": False,
            "error": "API TIMEOUT"
        }), 504

    except requests.RequestException as error:

        status = getattr(
            getattr(error, "response", None),
            "status_code",
            None
        )

        logging.error(
            "KLAUS CHECKER API ERROR: %s HTTP %s",
            type(error).__name__,
            status
        )

        return jsonify({
            "success": False,
            "error": "API CONNECTION ERROR"
        }), 502

    except Exception:

        logging.exception("Unexpected server error")

        return jsonify({
            "success": False,
            "error": "INTERNAL SERVER ERROR"
        }), 500


# =====================================
# SERVER START
# =====================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
