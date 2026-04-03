from flask import Flask, request, jsonify, abort
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from functools import wraps
import time
import re
from data_store import init_db, get_medicine_reply, upsert_medicine_reply


load_dotenv()

app = Flask(__name__)
init_db()

# Configure logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# API Key authentication
SERVER_API_KEY = os.getenv("SERVER_API_KEY", "your-secret-api-key-here")

# Rate limiter dictionary (simple implementation)
request_counts = {}

def rate_limit(requests_per_minute=1):
    """Rate limiter decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            if client_ip in request_counts:
                request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < 60]
            else:
                request_counts[client_ip] = []
            
            # Check rate limit
            if len(request_counts[client_ip]) >= requests_per_minute:
                abort(429)
            
            request_counts[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_api_key(f):
    """API Key authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != SERVER_API_KEY:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

def log_request(endpoint, user_prompt):
    """Log incoming requests"""
    logger.info(f"Endpoint: {endpoint} | User Prompt: {user_prompt}")

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# ==================== PROMPTS ====================
system_prompt = (
    '''You are a professional medicine assistant. The user will ask information about a medicine.
    Your reply must be in the below format:

    **[Medicine Name]** 
    
    **Use:** [Details of use]
    
    **Side Effect:** [Details of side effects]
    
    **Warnings:** [Any important warnings]

    If you get any input other than a medicine name, reply with: "Please write a medicine name."
    ''' )

ai_explain_prompt = (
    '''You are a professional medicine assistant. The user will ask information about a medicine.
    Your reply must be in the below format:

    **[Medicine Name]**

    **Dosage and Instructions:** [Dosage and instructions for the medicine]
    **When and how to take:** [When and how to take]
    **Food Interactions:** [Any food interactions]
    ''' )

similar_medicine_prompt = (
    '''You are a professional medicine assistant. The user will ask information about a medicine.
    Your reply must be in the below format:

    **[Medicine Name]**

    **Similar Medicine:** [Similar medicine name]

    **Difference:** [How is it different from the medicine?]
    
    **When to use alternative:** [When should patient use the alternative]
    ''')

medicine_links_prompt = (
    '''You are a helpful assistant that provides relevant links and resources for medicines.
    Given a medicine name, suggest useful links to:
    1. Online pharmacies (Amazon Pharmacy, 1mg, PharmEasy, Flipkart Health, etc)
    2. Medical information sites (Mayo Clinic, MedicineNet, etc)
    3. Local pharmacy recommendations
    
    Format your response as:
    **Medicine: [Name]**
    
    **Online Pharmacies:**
    - [Pharmacy Name]: [Link or search query]
    
    **Medical Information:**
    - [Resource Name]: [Brief description]
    
    **Tips:** [Any buying tips]
    ''' )

generate_text_prompt = (
    '''You are a text generation assistant. The user will give you a topic.
    Your task is to generate a well-structured paragraph about that topic.
    The paragraph should be informative and easy to understand.
    ''' )

summarize_prompt = (
    '''You are a summarization assistant. The user will provide you with an article or text.
    Your task is to summarize it into key points and a brief summary.
    Make sure the summary is concise but captures all important information.
    ''' )

analyze_prompt = (
    '''You are an analysis assistant. The user will provide you with text or content.
    Your task is to analyze it and determine:
    1. The intent/purpose of the text
    2. Key themes
    3. Sentiment (positive/negative/neutral)
    4. Recommended action (if any)
    ''' )

# ==================== ERROR HANDLERS ====================
@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        "status": "error",
        "code": 400,
        "message": "Bad Request. Please check your input or JSON format."
    }), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({
        "status": "error",
        "code": 401,
        "message": "Unauthorized. Invalid or missing API key."
    }), 401

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        "status": "error",
        "code": 429,
        "message": "Too Many Requests. Please try again after some time."
    }), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        "status": "error",
        "code": 500,
        "message": "Internal Server Error. Please try again later."
    }), 500

# ==================== ROUTES ====================

@app.route('/home', methods=['GET'])
def home():
    logger.info("Home page accessed")
    return jsonify({
        "status": "success",
        "message": "Welcome to Professional Medicine Chatbot API",
        "version": "2.0",
        "available_endpoints": [
            "/medicine_details",
            "/ai_explain",
            "/similar_medicine",
            "/medicine_links",
            "/generate_text",
            "/summarize",
            "/analyze"
        ]
    })

@app.route('/medicine_details', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=10)
def details():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("medicine_details", user_prompt)

        # 1) Check database cache
        cached_reply = get_medicine_reply(user_prompt)
        if cached_reply:
            return jsonify({
                "status": "success",
                "reply": cached_reply,
                "source": "database"
            })

        # 2) Not in DB -> call API
        full_prompt = f"{system_prompt}\nUser: {user_prompt}\nAssistant:"
        response = model.generate_content(full_prompt)
        answer = response.text

        # 3) Store fresh response for next request
        upsert_medicine_reply(user_prompt, answer)
        
        return jsonify({
            "status": "success",
            "reply": answer,
            "source": "api"
        })
    except Exception as e:
        logger.error(f"Error in medicine_details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/ai_explain', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=10)
def explain():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("ai_explain", user_prompt)
        
        full_prompt = f"{ai_explain_prompt}\nUser: {user_prompt}\nAssistant:"
        response = model.generate_content(full_prompt)
        answer = response.text
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
    except Exception as e:
        logger.error(f"Error in ai_explain: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/similar_medicine', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=10)
def similar():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("similar_medicine", user_prompt)
        
        full_prompt = f"{similar_medicine_prompt}\nUser: {user_prompt}\nAssistant:"
        response = model.generate_content(full_prompt)
        answer = response.text
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
    except Exception as e:
        logger.error(f"Error in similar_medicine: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/medicine_links', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=10)
def medicine_links():
    """Get relevant links and resources for a medicine"""
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("medicine_links", user_prompt)
        
        # Clean medicine name for URLs
        medicine_name = user_prompt.strip().lower().replace(" ", "+")
        
        # Generate AI suggestions
        full_prompt = f"{medicine_links_prompt}\nMedicine: {user_prompt}\nLinks and Resources:"
        response = model.generate_content(full_prompt)
        ai_suggestions = response.text
        
        # Build useful links
        links = {
            "online_pharmacies": [
                {
                    "name": "1mg",
                    "url": f"https://www.1mg.com/search?q={medicine_name}",
                    "description": "India's leading online pharmacy"
                },
                {
                    "name": "PharmEasy",
                    "url": f"https://www.pharmeasy.in/search/medicine?name={medicine_name}",
                    "description": "Quick medicine delivery"
                },
                {
                    "name": "Amazon Pharmacy",
                    "url": f"https://www.amazon.in/s?k={medicine_name}+medicine",
                    "description": "Medicines with trusted delivery"
                },
                {
                    "name": "NetMeds",
                    "url": f"https://www.netmeds.com/search?q={medicine_name}",
                    "description": "Prescription and OTC medicines"
                },
                {
                    "name": "Flipkart Health",
                    "url": f"https://www.flipkart.com/search?q={medicine_name}",
                    "description": "Health products marketplace"
                }
            ],
            "medical_info": [
                {
                    "name": "Mayo Clinic",
                    "url": f"https://www.mayoclinic.org/search/search-results?q={medicine_name}",
                    "description": "Trusted medical information"
                },
                {
                    "name": "MedicineNet",
                    "url": f"https://www.medicinenet.com/",
                    "description": "Comprehensive drug information"
                },
                {
                    "name": "WebMD",
                    "url": f"https://www.webmd.com/search?query={medicine_name}",
                    "description": "Medical encyclopedia and health guides"
                },
                {
                    "name": "Drugs.com",
                    "url": f"https://www.drugs.com/search?q={medicine_name}",
                    "description": "Drug information and side effects"
                }
            ],
            "local_help": [
                {
                    "name": "Find Nearby Pharmacy",
                    "url": "https://www.google.com/maps/search/pharmacy/",
                    "description": "Use Google Maps to find local pharmacies"
                },
                {
                    "name": "Swasth India",
                    "url": "https://www.swasth.app/",
                    "description": "Find verified local healthcare providers"
                }
            ]
        }
        
        return jsonify({
            "status": "success",
            "medicine": user_prompt,
            "ai_suggestions": ai_suggestions,
            "links": links
        })
    except Exception as e:
        logger.error(f"Error in medicine_links: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/generate_text', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=1)
def generate_text():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("generate_text", user_prompt)
        
        full_prompt = f"{generate_text_prompt}\nTopic: {user_prompt}\nGenerated Text:"
        response = model.generate_content(full_prompt)
        answer = response.text
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
    except Exception as e:
        logger.error(f"Error in generate_text: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/summarize', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=5)
def summarize():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("summarize", user_prompt)
        
        full_prompt = f"{summarize_prompt}\nText to summarize:\n{user_prompt}\n\nSummary:"
        response = model.generate_content(full_prompt)
        answer = response.text
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
    except Exception as e:
        logger.error(f"Error in summarize: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
@check_api_key
@rate_limit(requests_per_minute=5)
def analyze():
    try:
        data = request.get_json()
        user_prompt = data.get("user_prompt")
        
        if not user_prompt:
            return jsonify({
                "status": "error",
                "message": "user_prompt is required"
            }), 400
        
        log_request("analyze", user_prompt)
        
        full_prompt = f"{analyze_prompt}\nContent to analyze:\n{user_prompt}\n\nAnalysis:"
        response = model.generate_content(full_prompt)
        answer = response.text
        
        return jsonify({
            "status": "success",
            "reply": answer
        })
    except Exception as e:
        logger.error(f"Error in analyze: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
@app.route('/nearby_healthcare', methods=['POST'])
@check_api_key
def nearby_healthcare():
    try:
        data = request.get_json()
        location = data.get("location")
        place_type = data.get("type")

        if not location or not place_type:
            return jsonify({
                "status": "error",
                "message": "location and type required"
            }), 400

        GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

        if not GOOGLE_API_KEY:
            return jsonify({
                "status": "error",
                "message": "Google API key missing"
            }), 500

        import requests

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            "location": location,   # lat,lng
            "radius": 3000,
            "type": place_type,
            "key": GOOGLE_API_KEY
        }

        response = requests.get(url, params=params)
        results = response.json().get("results", [])

        places = []

        for place in results[:5]:
            places.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating", "N/A")
            })

        return jsonify({
            "status": "success",
            "places": places
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    logger.info("Application started")
    app.run(debug=True, host='127.0.0.1', port=5000)
