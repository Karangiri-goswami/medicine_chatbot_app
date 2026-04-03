import streamlit as st
import requests
import os
import geocoder
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="Medical Care AI",
    page_icon="🏥",
    layout="wide"
)

query_params = st.query_params
page = query_params.get("page", "Home")


# ==================== STYLE ====================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background-color: #eaf2f8;
}

/* TEXT */
body, p, span, label {
    color: #000000 !important;
}

/* NAVBAR */
.navbar {
    width: 100%;
    background: linear-gradient(to right, #dbeafe, #bfdbfe);
    padding: 12px 30px;
    margin-bottom: 25px;
    display: flex;
    gap: 20px;
    overflow-x: auto;
    scrollbar-width: none;
}

.navbar::-webkit-scrollbar {
    display: none;
}

/* NAV ITEMS */
.nav-item {
    text-decoration: none !important;
    color: #0f172a;
    font-size: 17px;
    font-weight: 600;
    padding: 8px 14px;
    border-radius: 8px;
    transition: all 0.3s ease;
    white-space: nowrap;
    position: relative;
}

/* HOVER ANIMATION */
.nav-item:hover {
    background-color: #60a5fa;
    color: white;
    transform: translateY(-2px);
}

/* ACTIVE TAB */
.nav-item.active {
    background-color: #2563eb;
    color: white !important;
}

/* ACTIVE UNDERLINE */
.nav-item::after {
    content: "";
    position: absolute;
    bottom: -4px;
    left: 0;
    width: 0%;
    height: 3px;
    background: #2563eb;
    transition: width 0.3s ease;
}

.nav-item:hover::after {
    width: 100%;
}

.nav-item.active::after {
    width: 100%;
}

/* TITLE */
.title {
    font-size: 55px;
    font-weight: bold;
    color: #111827;
}

/* INPUT */
div[data-baseweb="input"] {
    max-width: 450px;
}

/* BUTTON */
.stButton > button {
    background-color: #e5e7eb !important;   /* light grey */
    color: #ffffff !important;              /* 🔥 white text */
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    border: none;
}


/* WARNING */
div[data-testid="stAlert"] {
    color: black !important;
}

/* DASHBOARD CARDS */
.box {
    padding: 15px;
    border-radius: 10px;
    color: #1f2937 !important;
    font-weight: 700;
    font-size: 18px;
}

.green { background-color: #d4efdf; }
.blue { background-color: #d6eaf8; }
.lightgreen { background-color: #d5f5e3; }

/* INSTRUCTIONS TEXT */
.instructions-text {
    color: #111827 !important;
    font-size: 18px;
    font-weight: 500;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .title {
        font-size: 32px !important;
    }

    div[data-baseweb="input"] {
        max-width: 100% !important;
    }
}

/* ANIMATIONS */
.stApp {
    animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

.box {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.box:hover {
    transform: translateY(-5px);
    box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
}
            
/* ==================== INPUT BOX BORDER FIX ==================== */

/* TEXT INPUT */
div[data-baseweb="input"] > div {
    border: 2px solid #9ca3af !important;   /* grey border */
    border-radius: 8px;
    background-color: #ffffff !important;
}

/* FOCUS EFFECT */
div[data-baseweb="input"] > div:focus-within {
    border: 2px solid #2563eb !important;   /* blue border */
    box-shadow: 0 0 6px rgba(37, 99, 235, 0.4);
}

/* TEXT AREA (Summarize / Analyze mate) */
textarea {
    border: 2px solid #9ca3af !important;
    border-radius: 8px;
    background-color: #ffffff !important;
}

/* TEXT AREA FOCUS */
textarea:focus {
    border: 2px solid #2563eb !important;
    outline: none;
    box-shadow: 0 0 6px rgba(37, 99, 235, 0.4);
}

.stButton > button {
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.05);
    background-color: #ffffff !important;
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
</div>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
col1, col2 = st.columns([1,6])

with col1:
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
                        json={"user_prompt": med},
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success("Result Ready")
                        st.write(response.json().get("reply"))
                    else:
                        st.error("Error fetching data")
                except:
                    st.error("Server not running")
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
                    json={"user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Explanation Ready")
                    st.write(response.json().get("reply"))
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
                    json={"user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Alternatives Found")
                    st.write(response.json().get("reply"))
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
                    json={"user_prompt": med},
                    headers=headers
                )

                if response.status_code == 200:
                    data = response.json()

                    st.success("Links Generated")

                    st.markdown("### 🤖 AI Suggestions")
                    st.write(data.get("ai_suggestions"))

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
                    json={"user_prompt": topic},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Text Generated")
                    st.write(response.json().get("reply"))
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
                    json={"user_prompt": text},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Summary Ready")
                    st.write(response.json().get("reply"))
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
                    json={"user_prompt": text},
                    headers=headers
                )

                if response.status_code == 200:
                    st.success("Analysis Ready")
                    st.write(response.json().get("reply"))
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

        
else:
            st.warning("Enter location")

# ==================== FOOTER ====================
st.divider()
st.caption("🏥 Medical Care AI • Professional Assistant")
st.caption("⚠ Not a substitute for medical advice")
