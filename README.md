 # Medicine Chatbot & Other AI Tasks

This is a medicine chatbot built using Flask, Streamlit and Gemini API. It helps in educating people about medicines and also perform other AI tasks.

Features
system_prompt: Prompt to generate the use and side effects of the medicine
ai_explain_prompt: Promot to get a summarize details of the medicine
similar_medicine: Prompt to get an alternative medicine details
generate_text_prompt: Prompt to generate paragraph
summarize_prompt:Prompt to summarize the paragraph
analyze_prompt: Prompt to analyze
@app.before_request def check_key(): For API key authentication.
Logging:
To log each incoming request for tracking. All the files are stored in logs/app.log. Timestamp, Endpoint name and User prompt will be returned.

Limiter:
For controlled access and restricting the number of requests.

Error Handlers:
400 Bad Request: When the input format is incorrect. 401 Unauthorized: When the API key is missing/invalid. 429 Too Many Requests: When too many requests are sent.

API KEYS:
GEMINI_API_KEY: For accessing Gemini features.
SERVER_API_KEY: To authenticate request of API.
API endpoints
/home GET: a welcome page
/medicine_details POST: Use and side effect of medicine
/ai_explain POST: Dosage, Instructions and timing
/similar_medicine: similar medicine name, use and difference
/generate_text: To generate a paragraph using a text input
/summarize: To summarize the given article
/analyze: To analyze and return the intent of the article
Technologies used
Flask
Gemini API (gemini-2.5-flash)
Streamlit
1. Medicine details:
alt text

2. AI explain mode:
alt text

3. Alternative:
alt text

4. Generate Text:
alt text

5. Summarize:
alt text

6. Analyze:
alt text

7. Limit request: When more than 1 request is made within 1 min:
as generate_text limit is set to (@limiter.limit("1 per minute"))

alt text

8. When request is made with incorrect API key:
alt text