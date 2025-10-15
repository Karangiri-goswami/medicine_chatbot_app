from flask import Flask, request, jsonify, abort
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()
app = Flask(__name__)

limiter = Limiter(app=app, key_func=get_remote_address,   
default_limits=["2 per minute"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
server_api_key = os.getenv("SERVER_API_KEY")

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

system_prompt = (
            '''You are a medicine assistant. The user will ask information about a medicine.
            Your reply must be in the below format:

            **[Medicine Name]**

            **Use:** [Details of use]
            **Side Effect:** [Details of side effects]

            If you get any input other than a medicine name, reply with: "Please write a medicine name."
            ''' )

ai_explain_prompt = (
            '''You are a medicine assistant. The user will ask information about a medicine.
            Your reply must be in the below format:

            **[Medicine Name]**

            **Dosage and Instructions:** [Dosage and instructions for the medicine]
            **When and how to take:** [When and how to take]
            ''' )

similar_medicine_prompt = (
            '''You are a medicine assistant. The user will ask information about a medicine.
            Your reply must be in the below format:

            [Medicine Name]

            Similar Medicine: [Similar medicine name]

            Difference: [How is it different from the medicine?]
         ''')

generate_text_prompt = ( 
        '''You are a AI assistant. The user will provide you with input.   
            You need to generate a short story based on the input.
            Your reply must be in the below format:
            Text: [story based on the input]
            '''
)

summarize_prompt = ( 
        '''You are a AI assistant. The user will provide you with input.
           You should summareized the input in less than 100 words. 
            Your reply must be in the below format:
            [Summary]: [Summary of the input text] 
            [Title]: [A title for the summary]
            '''
)

analyze_prompt = ( 
        '''You are a AI assistant. The user will provide you with input.
            You need to analyze the input and provide details of the input and it's intent.
            Your response should be less than 100 words.
            Your reply must be in the below format:
             [Details of the input and it's intent]
            '''
)

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

@app.before_request
def check_key():
    open_routes = ['home', 'generate_text','summarize' ,'analyze']
    if request.endpoint not in open_routes:
        key = request.headers.get("api_key")
        if not key or key != server_api_key:  
            abort(401)


@app.route('/home', methods = ['GET'])
def home():
    return f"Welcome to medicine chatbot"

@app.route('/medicine_details', methods = ['POST'])
def details():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    full_prompt = f"{system_prompt}\nUser: {user_prompt}\nAssistant"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/ai_explain', methods =['POST'])
def explain():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    full_prompt = f"{ai_explain_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/similar_medicine', methods =['POST'])
def similar():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    full_prompt = f"{similar_medicine_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/generate_text', methods =['POST'])
@limiter.limit("1 per minute")
def gen_text():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        abort(400)
    logging.info(f"Endpoint name: /generate_text | Prompt: {user_prompt}")
    full_prompt = f"{generate_text_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/summarize', methods =['POST'])
def summarize_text():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        abort(400)
    logging.info(f"Endpoint name: /summarize | Prompt: {user_prompt}")
    full_prompt = f"{summarize_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/analyze', methods =['POST'])
def analyze():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        abort(400)
    logging.info(f"Endpoint name: /analyze | Prompt: {user_prompt}")
    full_prompt = f"{analyze_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})


if __name__ == "__main__":
    app.run(debug=True)