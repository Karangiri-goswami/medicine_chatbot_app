# Medicine Chatbot

This is a Flask based Medicine Assistant built using the Gemini API (Google Generative AI).
It provides detailed information about medicines such as uses, side effects, dosage instructions, 
and similar medicines.The chatbot interacts through well-defined endpoints to deliver AI-generated 
responses based on the user’s query.

 ## Features
* @app.route("/home") [GET] Returns a welcome message confirming that the API is running.
    Response: "Welcome to medicine chatbot"

* @app.route("/medicine_details") [POST]
    Provides the uses and side effects of a given medicine.
* Response Format:
    **Paracetamol**

    **Use:** Used to reduce fever and relieve pain.  
    **Side Effect:** May cause nausea or allergic reactions in rare cases.

* @app.route("/ai_explain") [POST]
    Explains the dosage and instructions for a particular medicine.
* Response Format:

    **Dosage and Instructions:** Take one tablet every 8 hours with water.  
    **When and how to take:** Preferably after meals for better absorption.

* @app.route("/similar_medicine") [POST]
    Suggests similar medicines and explains differences between them.
* Response Format:

    **Similar Medicine:** Dolo 650  
    **Difference:** Dolo 650 has a slightly higher dosage of paracetamol and provides longer lasting relief.

* Error Handling
    Custom error responses are implemented for better debugging:
1. 400 (Bad Request): Invalid or missing JSON data.
2. 401 (Unauthorized): Missing or incorrect API key.
3. 429 (Too Many Requests): Rate limit exceeded.

## Technologies Used

* Flask: creating RESTful APIs
* Google Generative AI (Gemini 2.5 Flash): generating intelligent for medicine related responses
* dotenv: managing API keys securely
* Python: backend logic and integration
* Streamlit UI

### Setup Instructions

* Clone the repository and navigate to the project directory.
* Create a .env file and add your Gemini API key:
* GEMINI_API_KEY=your_api_key_here

* Install dependencies:
> pip install flask python-dotenv google-generativeai
    
     Run the Flask application: python app.py
     
     streamlit run streamlit.py
* or access endpoints using tools like Postman.

### Example Use Case
1. Instantly fetch medicine information
2. Provide safe usage instructions to patients
3. Suggest alternative medicines based on user queries
4. Curated only for medicine related queries

### Sample Output:

![alt text](images/output.jpg)
