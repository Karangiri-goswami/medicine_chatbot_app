# 🏥 Medical Care AI - Advanced Medicine Chatbot

<div align="center">

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-API_Backend-black?style=for-the-badge&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite)

**A highly sophisticated, premium AI chatbot ecosystem for medicine information**

</div>

---

## ✨ Features

- **🚀 Unified Medicine Dashboard**: Enter a medicine name once and Instantly fetch **Details**, **AI Explanations**, **Alternatives**, and **Pharmacy Links** directly within a multi-tab view perfectly organized.
- **🖼️ Smart Visuals**: Automatic integration with **DuckDuckGo Image Search** and Wikipedia to fetch precise visual references of the prescribed drugs.
- **🔊 Text-to-Speech (TTS)**: Built-in voice generation using `gTTS` to read the AI explanation of your medications out loud.
- **🌍 Multi-Lingual**: Supports complex queries in exactly 6 languages: English, Gujarati, Hindi, Spanish, French, and German.
- **🏥 Nearby Healthcare Engine**: Auto-detects user boundaries via IP-based Geocoding and surfaces nearby hospitals and pharmacies using **Google Maps Network** with highly reliable **OpenStreetMap (OSM)** failover servers.
- **⚡ Supercharged Cache DB**: An advanced **SQLite** caching mechanism on the Backend to instantly return responses, massively saving API tokens, while accelerating load speed! Includes a specialized **Admin Dashboard** in the app to visually edit and manipulate cached data using Pandas.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit 
- **Backend**: Flask
- **Database**: SQLite3
- **AI Core**: Google GenAI (`gemini-2.5-flash`)
- **Modules**: `requests`, `geocoder`, `gTTS`, `duckduckgo-search`, `pandas`

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. Install the components using:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment `.env`
Create a `.env` file securely inside your project root and configure it:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SERVER_API_KEY=your_secret_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here # Optional (Has automatic OpenStreetMap fallback)
```

### 3. Run the Application Ecosystem
This application uses a sophisticated standard decoupled paradigm (Client + Server). **You must run BOTH processes in two separate terminals.**

**Terminal 1 (Backend Server):**
```bash
python app.py
```
> The Flask database & secure AI proxy boots up dynamically at `http://127.0.0.1:5000`.

**Terminal 2 (Frontend UI):**
```bash
streamlit run streamlit.py
```
> The sleek UI automatically launches in your browser (typically `http://localhost:8501`).

---

## 📁 Project Architecture

```text
medicine_chatbot/
│
├── app.py                # Heavy-lifting Flask API Endpoint & Cache server
├── streamlit.py          # Unified Streamlit graphical frontend interface
├── medicine_cache.db     # Invisible auto-generated blazing fast SQLite DB
├── requirements.txt      # Strictly defined project dependencies
├── .env                  # Configured environment keys 
└── logs/                 # Security logs and diagnostics
```

---

## 🔒 Security Measures

- **Decoupled Architecture**: Exposes zero API keys to the browser GUI. 
- **Internal Cross-Validation**: Flask backend endpoints forcefully apply rate-limiting to prevent web abuse.
- **Key-Locked Server**: All Streamlit queries require custom internal headers (`X-API-Key`) verified strictly by the local firewall.
- **Password Auth**: Admin Dashboard cached access protected dynamically via credential vaults.

---

## ⚠️ Disclaimer

**Important**: This software framework uses Large Language Models designed strictly for informational and experimental purposes and is NOT a replacement for qualified professional medical diagnoses. Always consult a licensed healthcare provider before adapting to specific treatments.

---

**Built beautifully for Advanced Medical Query Solving. Happy Coding! 🚀**
