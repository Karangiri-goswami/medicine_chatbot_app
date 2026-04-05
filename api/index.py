from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
import logging
from functools import wraps
import time
import requests
import os
import tempfile

BACKEND_URL = os.getenv("BACKEND_URL", "https://medicine-chatbot-app.vercel.app/")
DB_PATH = "/tmp/medicine_cache.db" if os.path.exists("/tmp") else "medicine_cache.db"

DDGS_AVAILABLE = False

load_dotenv()

app = Flask(__name__)

# ==================== LOGGING ====================
import sys
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== API KEYS ====================
SERVER_API_KEY = os.getenv("SERVER_API_KEY", "your-secret-api-key-here")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==================== GEMINI CLIENT (REST API) ====================
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# Using requests directly instead of GenAI SDK to avoid OS Segfaults/Lambda size issues.

# ==================== RATE LIMIT ====================
# FIX: In-memory rate limiter (works for single-process; swap for Redis in multi-worker prod)
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
                logger.warning(f"Rate limit hit for IP: {ip}")
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
system_prompt = """You are 'Meddy', an elite medical AI. 
Do NOT act like a standard conversational AI or Google Search. Your primary logic is to output visually stunning, engaging health insights broken into strict structured data chunks.
You MUST always format your response into TWO distinct parts, separated exactly by this line: [SPLIT]

PART 1: The Vital Signs Dashboard
Output a highly visual markdown dashboard:

**🩺 Vital Signs Dashboard:**
- 💊 **Category:** (e.g., Painkiller, Antibiotic)
- 🛒 **Availability:** (Over-the-counter or Prescription)
- ⭐ **Safety Rating:** (Rate out of 10 with a brief reason)

**🦸 The Secret Superpower:**
(One highly engaging sentence explaining how it acts inside the body like magic)

**⚖️ The Ultimate Trade-off:**
- ✅ **Best used for:** (1-2 points)
- ⚠️ **Do NOT use if:** (1-2 crucial warnings)

**🕵️ Biggest Myth Shattered:**
- ❌ **Myth:** (Common misconception)
- ✅ **Fact:** (The precise truth)

[SPLIT]

PART 2: The Deep Science (For 'Read More')
Provide a highly structured breakdown:
- 🚦 Traffic Light Interactions: List what is 🔴 Danger to mix with, 🟡 Caution, and 🟢 Safe.
- 🧪 The Geek-Out Chemistry: How it works at a cellular level.
- 💊 Crucial Side-Effects & Alternatives.
Use rich markdown, elegant tables, and bullet points. Never break this structure!"""

# ==================== GEMINI FUNCTION ====================
def ask_gemini(prompt):
    if not GEMINI_API_KEY:
        return "ERROR: GEMINI_API_KEY is missing or invalid on the Vercel Server."
    try:
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        }
        res = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", json=payload, headers={'Content-Type': 'application/json'}, timeout=20)
        if res.status_code == 200:
            result = res.json()
            try:
                answer = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return answer.strip() if answer else "Empty response from AI"
            except (IndexError, KeyError):
                logger.error(f"Failed to parse Gemini response: {result}")
                return "ERROR: Malformed AI response structure."
        else:
            logger.error(f"Gemini API Error: {res.status_code} - {res.text}")
            return f"Gemini API Error: {res.status_code}"
    except Exception as e:
        logger.error(f"Gemini API Exception: {e}")
        return f"ERROR: Failed to connect to Gemini API. {str(e)}"

# ==================== DATABASE ====================
def init_db():
    try:
        # FIX: check_same_thread=False for Flask concurrent requests
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()

        try:
            c.execute("ALTER TABLE medicine_cache RENAME TO medicine_cache_backup")
        except Exception:
            pass

        c.execute('''CREATE TABLE IF NOT EXISTS db_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feature TEXT NOT NULL,
                        medicine_name TEXT NOT NULL,
                        language TEXT NOT NULL,
                        reply TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(feature, medicine_name, language)
                    )''')

        try:
            c.execute("""INSERT OR IGNORE INTO db_cache (feature, medicine_name, language, reply, updated_at)
                         SELECT 'Medicine Info', medicine_name, 'English', reply, updated_at
                         FROM medicine_cache_backup""")
        except Exception:
            pass

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

# init_db() global removed


def get_medicine_reply(feature, medicine_name, language):
    return None
def _ignore_get_medicine_reply(feature, medicine_name, language):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute(
            "SELECT reply FROM db_cache WHERE feature = ? AND medicine_name COLLATE NOCASE = ? AND language COLLATE NOCASE = ?",
            (feature, medicine_name, language)
        )
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"DB Error getting cache: {e}")
        return None


def upsert_medicine_reply(feature, medicine_name, language, reply):
    pass
def _ignore_upsert(feature, medicine_name, language, reply):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute(
            '''INSERT INTO db_cache (feature, medicine_name, language, reply, updated_at)
               VALUES (?, ?, ?, ?, datetime('now'))
               ON CONFLICT(feature, medicine_name, language)
               DO UPDATE SET reply=excluded.reply, updated_at=datetime('now')''',
            (feature, medicine_name, language, reply)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error upserting cache: {e}")


# ==================== ROUTES ====================

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "message": "Medicine Chatbot API Backend is running perfectly on Vercel!",
        "endpoints": ["/medicine_details", "/ai_explain", "/similar_medicine", "/get_image", "/nearby_healthcare"]
    }), 200

@app.route("/medicine_details", methods=["POST"])
@check_api_key
@rate_limit()
def medicine_details():
    init_db()
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        language = data.get("language", "English")

        if not user_prompt:
            return jsonify({"status": "error", "message": "user_prompt required"}), 400

        logger.info(f"medicine_details: {user_prompt} | Lang: {language}")

        cached = get_medicine_reply("Medicine Info", user_prompt, language)
        if cached:
            return jsonify({"status": "success", "reply": cached, "source": "cache"})

        full_prompt = f"""Explain this medicine clearly:

Medicine: {user_prompt}
Language: {language}

Give:
- Uses
- How it works
- Side effects
- Alternatives

Keep it simple and structured."""

        answer = ask_gemini(full_prompt)
        upsert_medicine_reply("Medicine Info", user_prompt, language, answer)
        return jsonify({"status": "success", "reply": answer, "source": "gemini"})

    except Exception as e:
        logger.error(str(e))
        abort(500)


@app.route("/ai_explain", methods=["POST"])
@check_api_key
@rate_limit()
def ai_explain():
    init_db()
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    # FIX: Cache ai_explain responses to avoid redundant Gemini calls
    cached = get_medicine_reply("Explain", user_prompt, language)
    if cached:
        return jsonify({"status": "success", "reply": cached, "source": "cache"})

    full_prompt = f"{system_prompt}\n\nPlease respond exactly in this language: {language}\nExplain this medicine simply to a layman: {user_prompt}"
    answer = ask_gemini(full_prompt)
    upsert_medicine_reply("Explain", user_prompt, language, answer)
    return jsonify({"status": "success", "reply": answer, "source": "gemini"})


@app.route("/similar_medicine", methods=["POST"])
@check_api_key
@rate_limit()
def similar_medicine():
    init_db()
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    cached = get_medicine_reply("Alternatives", user_prompt, language)
    if cached:
        return jsonify({"status": "success", "reply": cached, "source": "cache"})

    full_prompt = f"{system_prompt}\n\nPlease respond exactly in this language: {language}\nFind safe and effective similar alternatives to this medicine: {user_prompt}"
    answer = ask_gemini(full_prompt)
    upsert_medicine_reply("Alternatives", user_prompt, language, answer)
    return jsonify({"status": "success", "reply": answer, "source": "gemini"})


@app.route("/medicine_links", methods=["POST"])
@check_api_key
@rate_limit()
def medicine_links():
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    full_prompt = f"{system_prompt}\n\nPlease respond exactly in this language: {language}\nGive quick tips for taking or buying this medicine safely: {user_prompt}"
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
    init_db()
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    # FIX: Cache generate_text responses
    cached = get_medicine_reply("GenerateText", user_prompt, language)
    if cached:
        return jsonify({"status": "success", "reply": cached, "source": "cache"})

    # FIX: No medicine system_prompt for generic text generation
    answer = ask_gemini(f"Please respond exactly in this language: {language}\nWrite informative text about: {user_prompt}")
    upsert_medicine_reply("GenerateText", user_prompt, language, answer)
    return jsonify({"status": "success", "reply": answer, "source": "gemini"})


@app.route("/summarize", methods=["POST"])
@check_api_key
@rate_limit()
def summarize():
    init_db()
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    cached = get_medicine_reply("Summarize", user_prompt, language)
    if cached:
        return jsonify({"status": "success", "reply": cached, "source": "cache"})

    # FIX: No medicine system_prompt for generic summarization
    answer = ask_gemini(f"Please respond exactly in this language: {language}\nSummarize the following text: {user_prompt}")
    upsert_medicine_reply("Summarize", user_prompt, language, answer)
    return jsonify({"status": "success", "reply": answer, "source": "gemini"})


@app.route("/analyze", methods=["POST"])
@check_api_key
@rate_limit()
def analyze():
    init_db()
    data = request.get_json()
    user_prompt = data.get("user_prompt", "")
    language = data.get("language", "English")

    cached = get_medicine_reply("Analyze", user_prompt, language)
    if cached:
        return jsonify({"status": "success", "reply": cached, "source": "cache"})

    # FIX: No medicine system_prompt for generic analysis
    # FIX: Removed duplicate return statement
    answer = ask_gemini(f"Please respond exactly in this language: {language}\nAnalyze the following content: {user_prompt}")
    upsert_medicine_reply("Analyze", user_prompt, language, answer)
    return jsonify({"status": "success", "reply": answer, "source": "gemini"})


# ==================== FETCH IMAGE ====================
@app.route("/get_image", methods=["POST"])
@check_api_key
@rate_limit()  # FIX: Added missing rate limit
def get_image():
    data = request.get_json()
    med_name = data.get("medicine_name")
    if not med_name:
        return jsonify({"status": "error", "message": "medicine_name required"}), 400

    if not DDGS_AVAILABLE:
        return jsonify({"status": "error", "message": "duckduckgo-search not installed"}), 500

    # DuckDuckGo attempt
    try:
        results = DDGS().images(keywords=f"{med_name} medicine tablet", max_results=1)
        if not results:
            results = DDGS().images(keywords=f"{med_name} medicine", max_results=1)
        if results:
            image_url = results[0].get("image")
            if image_url:
                return jsonify({"status": "success", "image_url": image_url})
    except Exception as e:
        logger.warning(f"DDGS failed, falling back to Wikipedia: {e}")

    try:
        # Wikipedia fallback
        wiki_url = (
            f"https://en.wikipedia.org/w/api.php?action=query&titles={med_name}"
            f"&prop=pageimages&format=json&pithumbsize=500"
        )
        headers = {'User-Agent': 'MedicineChatbot/1.0 (https://localhost)'}
        res = requests.get(wiki_url, headers=headers).json()
        pages = res.get("query", {}).get("pages", {})
        for page_id, pdata in pages.items():
            if "thumbnail" in pdata:
                return jsonify({"status": "success", "image_url": pdata["thumbnail"]["source"]})

        return jsonify({"status": "error", "message": "No image found"}), 404

    except Exception as e:
        logger.error(f"get_image fallback error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== NEARBY HEALTHCARE ====================
@app.route("/nearby_healthcare", methods=["POST"])
@check_api_key
@rate_limit()
def nearby_healthcare():
    try:
        data = request.get_json()
        location = data.get("location")
        place_type = data.get("type")

        if not location or not place_type:
            return jsonify({"status": "error", "message": "location and type required"}), 400

        GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
        
        # Google Maps attempt
        if GOOGLE_API_KEY:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": location,
                "radius": 3000,
                "type": place_type,
                "key": GOOGLE_API_KEY
            }

            response = requests.get(url, params=params)
            result = response.json()

            places = []
            for place in result.get("results", [])[:5]:
                places.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "rating": place.get("rating", "N/A"),
                    "lat": place.get("geometry", {}).get("location", {}).get("lat", ""),
                    "lng": place.get("geometry", {}).get("location", {}).get("lng", "")
                })

            return jsonify({"status": "success", "places": places})

        # Fallback to OpenStreetMap (Overpass API)
        try:
            lat, lng = location.split(',')
            # Map type to OSM tags
            osm_type = "hospital"
            if place_type == "pharmacy":
                osm_type = "pharmacy"
            elif place_type == "clinic":
                osm_type = "clinic"

            overpass_url = "http://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json];
            node
              ["amenity"="{osm_type}"]
              (around:5000,{lat},{lng});
            out 5;
            """
            
            headers = {"User-Agent": "MedicineChatbot/1.0"}
            response = requests.post(overpass_url, data=overpass_query, headers=headers, timeout=10)
            res_json = response.json()
            
            places = []
            for node in res_json.get("elements", []):
                tags = node.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                address = tags.get("addr:full", tags.get("addr:street", "Address not available"))
                places.append({
                    "name": name,
                    "address": address,
                    "rating": "N/A",
                    "lat": node.get("lat", lat),
                    "lng": node.get("lon", lng)
                })
            
            if places:
                return jsonify({"status": "success", "places": places})
            else:
                return jsonify({"status": "error", "message": "No places found nearby"}), 404
                
        except Exception as osm_e:
            logger.error(f"OSM Fallback error: {osm_e}")
            return jsonify({"status": "error", "message": "GOOGLE_MAPS_API_KEY not configured and fallback failed"}), 500

    except Exception as e:
        logger.error(f"nearby_healthcare error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ==================== RUN ====================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)