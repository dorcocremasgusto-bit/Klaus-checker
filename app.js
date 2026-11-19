import os
import re
import requests

from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

API_URL = os.environ.get("https://baron0.com/api/v2/check")
API_KEY = os.environ.get("bk_v1_0na8mbdd5QJyZsTI5zuu4XNzce_hqn4gn744UAE5dBBBxAzEVWqKifseOxO_5k4i7I4Fj9sw7RMLeucgpdbX_rWQQ5_mnMi1u5M0R9mB1JvBaakH26BxhReBfCPL-9cJK_zpRcDnW8TeQIm8XJyHQHmCKW4Vu_XK8qJ0OeBrByZuUP-mktvdZ4ssXgo72EBMeIeHFj13_1HdER1nDoPB2js_WnXm2hDZexFgxpRy4hbRJyvPM1V_t1wBBtL3tc_KZ9dE1begeRVRy5Klf3ft5L960-8AT0ssseMfbbT8-C7MCowJETqvaIzKEupNIMRl3D_JOUF-EOA0yvDHCrzXGloHP77GNc1saW4vp9xjQ5BEkQQh_J6dinqk8R313RsigKTCeJtLQu67JY_G90wh21T9tIQ0S74tPRx_UrcK_vWc7A8Qkvcz2nWrkE_9y_qvQDbuiX_hfvkiixWpp8i_okEz-Vg4ez4o7971RjQVYnbXPNILIgcDZt96LWcFlYdU9PkOUWeYCmPUxXfTDabTkSzKc6iLKx99o9tyBhhRQZFxltcIycJfK9YoHFGo2n8BvFZidyjaiJ2Nawg")


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
