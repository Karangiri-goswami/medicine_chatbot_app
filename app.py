from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    try:
        import requests
        from google import genai
        return jsonify({"status": "installed", "msg": "It works!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "trace": getattr(e, '__traceback__', None)}), 500

@app.route("/medicine_details", methods=["POST"])
def medicine_details():
    return jsonify({"status": "test"})