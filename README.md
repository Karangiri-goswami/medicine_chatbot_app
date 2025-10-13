# Medicine Chatbot

This is a medicine chatbot built using Flask, Streamlit and Gemini API.
It helps in educating people about medicines.

## Features 

* system_prompt: Prompt to generate the use and side effects of the medicine
* ai_explain_prompt: Promot to get a summarize details of the medicine
* similar_medicine: Prompt to get an alternative medicine details

## API endpoints

* /home GET: a welcome page
* /medicine_details POST: Use and side effect of medicine
* /ai_explain POST: Dosage, Instructions and timing
* /similar_medicine: similar medicine name, use and difference


## Technologies used

* Flask
* Gemini API (gemini-2.5-flash)
* Streamlit

### 1. Medicine details:

![alt text](images/medicine_details.png)

### 2. AI explain mode:

![alt text](images/ai_explain.png)

### 3. Alternative:

![alt text](images/alternative.png)