from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv

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

            [Medicine Name]

            Similar Medicine: [Similar medicine name]

            Difference: [How is it different from the medicine?]
         ''')

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