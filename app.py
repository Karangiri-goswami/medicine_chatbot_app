from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging

load_dotenv

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

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
def gen_text():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        return jsonify({
            "status": "error",
            "message": "Please enter a text"
        }), 400
    logging.info(f"Endpoint name: /generate_text | Prompt: {user_prompt}")
    full_prompt = f"{generate_text_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})

@app.route('/summarize', methods =['POST'])
def summarize():
    data = request.get_json()
    user_prompt = data.get("user_prompt")
    if not user_prompt:
        return jsonify({
            "status": "error",
            "message": "Please enter an article"
        }), 400
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
        return jsonify({
            "status": "error",
            "message": "Please enter an article"
        }), 400
    logging.info(f"Endpoint name: /analyze | Prompt: {user_prompt}")
    full_prompt = f"{analyze_prompt}\nUser: {user_prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    answer = response.text
    return jsonify({"reply":answer})


if __name__ == "__main__":
    app.run(debug=True)