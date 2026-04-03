from flask import Flask, request, jsonify, abort
import google.generativeai as genai
from dotenv import load_dotenv  
import os

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


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

            **[Medicine Name]**

            **Similar Medicine:** [Similar medicine name]

            **Difference:** [How is it different from the medicine?]
            ''')


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

if __name__ == "__main__":
    app.run(debug=True)
