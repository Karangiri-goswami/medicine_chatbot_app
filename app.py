from flask import Flask, request, jsonify, abort
from google import genai   # ✅ NEW SDK
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from functools import wraps
import time
import re
import sqlite3
import requests

load_dotenv()

app = Flask(__name__)

# ==================== LOGGING ====================
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ==================== API KEYS ====================
SERVER_API_KEY = os.getenv("SERVER_API_KEY", "your-secret-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==================== GEMINI CLIENT ====================
client = genai.Client(api_key=GEMINI_API_KEY)


# ==================== RATE LIMIT ====================
request_counts = {}

def rate_limit(requests_per_minute=10):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            if ip not in request_counts:
                request_counts[ip] = []

            request_counts[ip] = [t for t in request_counts[ip] if now - t < 60]

            if len(request_counts[ip]) >= requests_per_minute:
                abort(429)

            request_counts[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# ==================== API KEY CHECK ====================
def check_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key != SERVER_API_KEY:
            abort(401)
        return f(*args, **kwargs)
    return wrapper

# ==================== PROMPTS ====================
system_prompt = "You are a professional medicine assistant. Give accurate, safe, and simple medical info."

# ==================== GEMINI FUNCTION ====================
def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {str(e)}")
        return "Error generating response"

# ==================== ROUTES ====================
def init_db():
    try:
        conn = sqlite3.connect('medicine_cache.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS medicine_cache (
                        medicine_name TEXT PRIMARY KEY,
                        reply TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

init_db()

def get_medicine_reply(medicine_name):
    try:
        conn = sqlite3.connect('medicine_cache.db')
        c = conn.cursor()
        c.execute("SELECT reply FROM medicine_cache WHERE medicine_name COLLATE NOCASE = ?", (medicine_name,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"DB Error getting cache: {e}")
        return None

def upsert_medicine_reply(medicine_name, reply):
    try:
        conn = sqlite3.connect('medicine_cache.db')
        c = conn.cursor()
        c.execute('''INSERT INTO medicine_cache (medicine_name, reply, updated_at) 
                     VALUES (?, ?, datetime('now')) 
                     ON CONFLICT(medicine_name) DO UPDATE SET reply=excluded.reply, updated_at=datetime('now')''', 
                  (medicine_name, reply))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error upserting cache: {e}")


@app.route("/medicine_details", methods=["POST"])
@check_api_key
@rate_limit()
def medicine_details():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")

        if not user_prompt:
            return jsonify({"status": "error", "message": "user_prompt required"}), 400

        logger.info(f"medicine_details: {user_prompt}")

        # CACHE CHECK
        cached = get_medicine_reply(user_prompt)
        if cached:
            return jsonify({"status": "success", "reply": cached, "source": "cache"})

        # GEMINI CALL
        full_prompt = f"{system_prompt}\nUser: {user_prompt}"
        answer = ask_gemini(full_prompt)

        upsert_medicine_reply(user_prompt, answer)

        return jsonify({"status": "success", "reply": answer, "source": "gemini"})

    except Exception as e:
        logger.error(str(e))
        return abort(500)

# ==================== ADDITIONAL ROUTES ====================
@app.route("/ai_explain", methods=["POST"])
@check_api_key
@rate_limit()
def ai_explain():
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    full_prompt = f"Explain this medicine simply: {user_prompt}"
    answer = ask_gemini(full_prompt)
    return jsonify({"status": "success", "reply": answer})

@app.route("/similar_medicine", methods=["POST"])
@check_api_key
@rate_limit()
def similar_medicine():
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    full_prompt = f"Find similar alternatives to this medicine: {user_prompt}"
    answer = ask_gemini(full_prompt)
    return jsonify({"status": "success", "reply": answer})

@app.route("/medicine_links", methods=["POST"])
@check_api_key
@rate_limit()
def medicine_links():
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    full_prompt = f"Give quick tips for taking or buying this medicine safely: {user_prompt}"
    answer = ask_gemini(full_prompt)
    med_q = user_prompt.strip().lower().replace(" ", "+")
    links = {
        "online_pharmacies": [
            {"name": "1mg", "url": f"https://www.1mg.com/search?q={med_q}"},
            {"name": "PharmEasy", "url": f"https://www.pharmeasy.in/search/medicine?name={med_q}"},
            {"name": "Amazon", "url": f"https://www.amazon.in/s?k={med_q}+medicine"}
        ],
        "medical_info": [
            {"name": "Mayo Clinic", "url": f"https://www.mayoclinic.org/search/search-results?q={med_q}"},
            {"name": "WebMD", "url": f"https://www.webmd.com/search?query={med_q}"}
        ]
    }
    return jsonify({"status": "success", "ai_suggestions": answer, "links": links})

@app.route("/generate_text", methods=["POST"])
@check_api_key
@rate_limit()
def generate_text():
    data = request.get_json()
    answer = ask_gemini(f"Write informative text about: {data.get('user_prompt', '')}")
    return jsonify({"status": "success", "reply": answer})

@app.route("/summarize", methods=["POST"])
@check_api_key
@rate_limit()
def summarize():
    data = request.get_json()
    answer = ask_gemini(f"Summarize the following text: {data.get('user_prompt', '')}")
    return jsonify({"status": "success", "reply": answer})

@app.route("/analyze", methods=["POST"])
@check_api_key
@rate_limit()
def analyze():
    data = request.get_json()
    answer = ask_gemini(f"Analyze the following content: {data.get('user_prompt', '')}")
    return jsonify({"status": "success", "reply": answer})

# ==================== NEARBY HEALTHCARE ====================
@app.route("/nearby_healthcare", methods=["POST"])
@check_api_key
def nearby_healthcare():
    try:
        data = request.get_json()
        location = data.get("location")
        place_type = data.get("type")

        if not location or not place_type:
            return jsonify({"status": "error", "message": "location and type required"}), 400

        GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            "location": location,
            "radius": 3000,
            "type": place_type,
            "key": GOOGLE_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        places = []
        for place in data.get("results", [])[:5]:
            places.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "N/A")
            })

        return jsonify({"status": "success", "places": places})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
