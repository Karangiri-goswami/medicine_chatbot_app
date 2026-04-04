import streamlit as st
import requests
import os
import geocoder
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Medical Care AI",
    page_icon="logo.png",
    layout="wide"
)

query_params = st.query_params
page = query_params.get("page", "Home")


# ==================== STYLE ====================
st.markdown("""
<style>
/* ==================== ULTRA-MODERN HEALTHCARE THEME ==================== */

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* BACKGROUND & TYPOGRAPHY */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1551076805-e1869043e560?auto=format&fit=crop&w=2000&q=80") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}
[data-testid="stAppViewContainer"] {
    background: rgba(240, 244, 248, 0.92) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
h1, h2, h3 {
    color: #0F172A !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}
p, span, label, div[data-testid="stMarkdownContainer"] {
    color: #334155 !important;
    font-size: 16px;
}

/* NAVBAR (Floating Glass Card) */
.navbar {
    width: 100%;
    background: #FFFFFF;
    padding: 15px 30px;
    margin-top: -40px;
    margin-bottom: 40px;
    display: flex;
    gap: 15px;
    overflow-x: auto;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.04);
    scrollbar-width: none;
    align-items: center;
}
.navbar::-webkit-scrollbar { display: none; }

.nav-item {
    text-decoration: none !important;
    color: #64748B;
    font-size: 15px;
    font-weight: 700;
    padding: 10px 24px;
    border-radius: 50px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
}
.nav-item:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}
.nav-item.active {
    background: linear-gradient(135deg, #0EA5E9, #2563EB);
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
}

/* TITLE GRADIENT */
.title {
    font-size: 58px;
    font-weight: 900;
    background: -webkit-linear-gradient(45deg, #0EA5E9, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: -10px;
}

/* PILL BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #10B981, #059669) !important;
    color: #ffffff !important;
    border-radius: 50px !important;
    padding: 12px 32px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border: none !important;
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.25) !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(16, 185, 129, 0.35) !important;
}

/* INPUT FIELDS */
div[data-baseweb="input"] > div, textarea {
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
    padding: 4px 8px;
    transition: all 0.3s ease;
}
div[data-baseweb="input"] > div:focus-within, textarea:focus {
    border: 1px solid #0EA5E9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
}

/* METRICS UI for VITAL SIGNS */
div[data-testid="stMetricValue"] {
    color: #0EA5E9 !important;
    font-weight: 900 !important;
    font-size: 2.2rem !important;
}
div[data-testid="stMetricLabel"] p {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #64748B !important;
}

/* EXPANDER CARDS */
div[data-testid="stExpander"] {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    overflow: hidden;
}

/* GENERAL BLOCKS */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* ANIMATION */
.stApp { animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* RESPONSIVE GRID SYSTEM (FOR MOBILE/TABLET) */
@media screen and (max-width: 900px) {
    /* Navbar Flex Grid */
    .navbar {
        padding: 10px;
        flex-wrap: nowrap;
        border-radius: 10px;
        gap: 10px;
        margin-top:-20px;
    }
    .nav-item { padding: 6px 12px; font-size: 13px; }
    
    /* Auto Stack Columns using CSS Grid overrides */
    div[data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
        margin-bottom: 25px;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: row"] {
        flex-direction: column !important;
    }
    
    .title { font-size: 30px !important; margin-top: 10px !important; line-height: 1.2; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    .stImage > img { width: 100% !important; max-width: 100% !important;}
    div[data-baseweb="input"] > div { width: 100% !important; max-width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# ==================== NAVBAR ====================
def nav_item(name):
    active_class = "active" if page == name else ""
    return f'<a class="nav-item {active_class}" href="?page={name}" target="_self">{name}</a>'

st.markdown(f"""
<div class="navbar">
{nav_item("Home")}
{nav_item("Medicine Info")}
{nav_item("AI Explain")}
{nav_item("Alternatives")}
{nav_item("Pharmacy Links")}
{nav_item("Generate Text")}
{nav_item("Summarize")}
{nav_item("Analyze")}
{nav_item("Nearby Healthcare")}
{nav_item("Admin Dashboard")}
</div>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
col1, col2 = st.columns([1,6])

with col1:
    import os
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966481.png", width=110)

with col2:
    st.markdown('<div class="title">Medical Care AI</div>', unsafe_allow_html=True)
    st.caption("Professional Healthcare Assistant")

st.divider()

# ==================== CONFIG ====================
API_KEY = os.getenv("SERVER_API_KEY", "your-secret-api-key-here")
BASE_URL = "http://127.0.0.1:5000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# ==================== LANGUAGE SIDEBAR ====================
st.sidebar.title("🌍 Preferences")
selected_lang = st.sidebar.selectbox(
    "Select Language", 
    ["English", "Gujarati", "Hindi", "Spanish", "French", "German"]
)

def text_to_speech(text):
    try:
        from gtts import gTTS
    except ImportError:
        st.warning("🔊 Voice feature offline: 'gTTS' is not installed in this environment. (Run `pip install gTTS` to enable)")
        return
        
    import base64
    import os
    
    # Map to official gTTS language codes
    code_map = {"English": "en", "Gujarati": "gu", "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de"}
    code = code_map.get(selected_lang, "en")
    
    try:
        # Generate perfect local MP3 using Google TTS
        clean = text.replace('\n', ' ').replace('*', '').strip()
        tts = gTTS(text=clean, lang=code, slow=False)
        tts.save("tts_audio.mp3")
        
        with open("tts_audio.mp3", "rb") as f:
            audio_bytes = f.read()
            
        b64 = base64.b64encode(audio_bytes).decode()
        
        # Display an elegant audio player matching the theme
        audio_html = f'''
        <div style="background: white; padding: 10px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 15px;">
            <div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: white;">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M11.536 14.01A8.473 8.473 0 0 0 14.026 8a8.473 8.473 0 0 0-2.49-6.01l-.708.707A7.476 7.476 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303l.708.707z"/><path d="M10.121 12.596A6.479 6.479 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.483 5.483 0 0 1 11.025 8a5.483 5.483 0 0 1-1.61 3.89l.706.706z"/><path d="M8.707 11.182A4.486 4.486 0 0 0 10.025 8a4.486 4.486 0 0 0-1.318-3.182L8 5.525A3.489 3.489 0 0 1 9.025 8 3.49 3.49 0 0 1 8 10.475l.707.707zM6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06z"/></svg>
            </div>
            <strong style="color: #0f172a;">Listen:</strong>
            <audio controls autoplay style="height: 40px; flex-grow: 1;">
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        </div>
        '''
        st.markdown(audio_html, unsafe_allow_html=True)
        if os.path.exists("tts_audio.mp3"):
            os.remove("tts_audio.mp3")
    except Exception as e:
        st.error(f"TTS Error: {e}")

def display_ai_response(text):
    if not text:
        st.markdown("No response generated.")
        return
        
    # Generate TTS purely from first 300 plain text characters
    import re
    clean_speech = re.sub(r'[^\w\s.,!?:]', '', text[:350]).replace('\n', ' ')
    text_to_speech(clean_speech)

    # Revert to Bulletproof Split Method!
    if "[SPLIT]" in text:
        parts = [p.strip() for p in text.split("[SPLIT]") if p.strip()]
        if len(parts) >= 1:
            st.info(parts[0])
        if len(parts) > 1:
            with st.expander("📖 Read More (Deep Dive)"):
                st.markdown("\n\n".join(parts[1:]))
    else:
        st.info(text)


# ==================== HOME ====================
if page == "Home":

    st.subheader("Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.markdown('<div class="box green">✔ Medicine Info</div>', unsafe_allow_html=True)
    col2.markdown('<div class="box blue">🤖 AI Powered</div>', unsafe_allow_html=True)
    col3.markdown('<div class="box lightgreen">🟢 System Active</div>', unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Services")
        st.write("""
        • Medicine details  
        • Side effects  
        • AI explanations  
        • Alternatives  
        """)

    with col2:
        st.markdown("### Instructions")
        st.markdown("""
        <div class="instructions-text">
        1. Select feature<br>
        2. Enter input<br>
        3. Click button<br>
        4. View results
        </div>
        """, unsafe_allow_html=True)

    st.warning("⚠ This system is for guidance only. Consult a doctor.")

# ==================== MEDICINE ====================
elif page == "Medicine Info":

    st.subheader("Medicine Details")

    med = st.text_input("Enter Medicine Name")

    if st.button("Search"): 
        if med:
            with st.spinner("Fetching..."):
                try:
                    response = requests.post(
                        f"{BASE_URL}/medicine_details",
                        json={"language": selected_lang, "user_prompt": med},
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success("Result Ready")
                        
                        # Image fetching logic with robust placeholder fallback
                        try:
                            img_response = requests.post(f"{BASE_URL}/get_image", json={"medicine_name": med}, headers=headers, timeout=8)
                            if img_response.status_code == 200:
                                img_url = img_response.json().get("image_url")
                                if img_url:
                                    st.image(img_url, width=350, caption=f"Reference Visual for {med}")
                                else:
                                    st.image("https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500", width=350, caption="Placeholder Reference")
                            else:
                                st.image("https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500", width=350, caption="Placeholder Reference")
                        except Exception:
                            st.image("https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500", width=350, caption="Placeholder Reference")
                            
                        display_ai_response(response.json().get("reply"))
                    else:
                        st.error("Error fetching data")
                except Exception as e:
                    import traceback
                    st.error(f"Render Error: {e}")
                    st.code(traceback.format_exc())
        else:
            st.warning("Enter medicine name")

elif page == "AI Explain":

    st.subheader("AI Explain Medicine")

    med = st.text_input("Enter Medicine Name")

    if st.button("Explain"):
        if med:
            try:
                response = requests.post(
                    f"{BASE_URL}/ai_explain",
                    json={"language": selected_lang, "user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Explanation Ready")
                    display_ai_response(response.json().get("reply"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Alternatives":

    st.subheader("Find Alternative Medicines")

    med = st.text_input("Enter Medicine Name")

    if st.button("Find Alternatives"):
        if med:
            try:
                response = requests.post(
                    f"{BASE_URL}/similar_medicine",
                    json={"language": selected_lang, "user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Alternatives Found")
                    display_ai_response(response.json().get("reply"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Pharmacy Links":

    st.subheader("Medicine Purchase Links")

    med = st.text_input("Enter Medicine Name")

    if st.button("Get Links"):
        if med:
            try:
                response = requests.post(
                    f"{BASE_URL}/medicine_links",
                    json={"language": selected_lang, "user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Links Generated")

                    st.markdown("### 🤖 AI Suggestions")
                    display_ai_response(data.get("ai_suggestions"))

                    st.markdown("### 🛒 Online Pharmacies")
                    for item in data["links"]["online_pharmacies"]:
                        st.markdown(f"- [{item['name']}]({item['url']})")

                    st.markdown("### 📘 Medical Info")
                    for item in data["links"]["medical_info"]:
                        st.markdown(f"- [{item['name']}]({item['url']})")

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Generate Text":

    st.subheader("Generate Text")

    topic = st.text_input("Enter Topic")

    if st.button("Generate"):
        if topic:
            try:
                response = requests.post(
                    f"{BASE_URL}/generate_text",
                    json={"language": selected_lang, "user_prompt": topic},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Text Generated")
                    display_ai_response(response.json().get("reply"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Summarize":

    st.subheader("Summarize Text")

    text = st.text_area("Enter Text")

    if st.button("Summarize"):
        if text:
            try:
                response = requests.post(
                    f"{BASE_URL}/summarize",
                    json={"language": selected_lang, "user_prompt": text},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Summary Ready")
                    display_ai_response(response.json().get("reply"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Analyze":

    st.subheader("Analyze Text")

    text = st.text_area("Enter Content")

    if st.button("Analyze"):
        if text:
            try:
                response = requests.post(
                    f"{BASE_URL}/analyze",
                    json={"language": selected_lang, "user_prompt": text},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Analysis Ready")
                    display_ai_response(response.json().get("reply"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(str(e))

elif page == "Nearby Healthcare":

    st.subheader("Nearby Healthcare Finder 🏥")

    import geocoder

    place_type = st.selectbox(
        "Select Type",
        ["hospital", "pharmacy", "clinic"]
    )

    if st.button("Use My Location 📍"):

        g = geocoder.ip('me')
        lat, lng = g.latlng

        st.success(f"Detected Location: {lat}, {lng}")

        try:
            response = requests.post(
                f"{BASE_URL}/nearby_healthcare",
                json={
                    "location": f"{lat},{lng}",   # 🔥 IMPORTANT
                    "type": place_type
                },
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()

                st.success("Nearby places found!")

                for place in data["places"]:
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={place['name']}"

                    st.markdown(f"""
                    **{place['name']}**  
                    📍 {place['address']}  
                    ⭐ Rating: {place['rating']}  
                    [Open in Maps]({maps_url})
                    """)
                    st.divider()

            else:
                st.error(response.text)
                

        except Exception as e:
            st.error(str(e))    
        
elif page == "Admin Dashboard":

    st.subheader("Admin Dashboard 🔒")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.write("Please log in to view the database.")
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        st.success("Welcome, Admin!")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        st.write("### 🗄️ Cached Medicine Data (Edit / Delete)")
        try:
            import sqlite3
            import pandas as pd
            conn = sqlite3.connect("medicine_cache.db")
            
            # Read from the new table
            df = pd.read_sql_query("SELECT id, feature, medicine_name, language, reply, updated_at FROM db_cache", conn)
            
            if not df.empty:
                # Use data_editor to allow adding, editing, deleting rows
                edited_df = st.data_editor(
                    df, 
                    num_rows="dynamic", 
                    use_container_width=True,
                    key="admin_editor"
                )
                
                if st.button("💾 Save Database Changes"):
                    with st.spinner("Saving..."):
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM db_cache")  # Wipe existing
                        
                        for _, row in edited_df.iterrows():
                            # If it's a completely new row added by user, id might be NaN
                            if pd.isna(row.get('id')):
                                cursor.execute('''INSERT INTO db_cache (feature, medicine_name, language, reply, updated_at) 
                                                  VALUES (?, ?, ?, ?, ?)''', 
                                              (row.get('feature', 'Medicine Info'), row.get('medicine_name', ''), 
                                               row.get('language', 'English'), row.get('reply', ''), row.get('updated_at', '')))
                            else:
                                cursor.execute('''INSERT INTO db_cache (id, feature, medicine_name, language, reply, updated_at) 
                                                  VALUES (?, ?, ?, ?, ?, ?)''', 
                                              (row['id'], row['feature'], row['medicine_name'], row['language'], row['reply'], row['updated_at']))
                        conn.commit()
                        st.session_state["cache_saved"] = True
                        st.success("✅ Database updated successfully!")
                        st.rerun()
            else:
                st.info("The medicine cache database is empty.")
                
            conn.close()
        except Exception as e:
            st.error(f"Error loading database. Make sure you fetch info at least once. Details: {str(e)}")

# ==================== FOOTER ====================
st.divider()
st.caption("🏥 Medical Care AI • Professional Assistant")
st.caption("⚠ Not a substitute for medical advice")