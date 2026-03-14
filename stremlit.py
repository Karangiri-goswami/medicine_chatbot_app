import streamlit as st
import requests

st.title("Medicine Chatbot")

user_input = st.text_input("Enter medicine name:")

if st.button("Check Use and Side effect"):
    if not user_input:
        st.warning("Medicine name missing")
    else:
        response = requests.post("http://127.0.0.1:5000/medicine_details",json={"user_prompt": user_input})
        if response.status_code == 200:
            reply = response.json().get("reply", "")
            st.markdown(f"\n{reply}")
        else:
            st.error(f"Error {response.status_code}: {response.text}")

if st.button("Explain:AI mode"):
            response = requests.post("http://127.0.0.1:5000/ai_explain",json={"user_prompt": user_input})
            if response.status_code == 200:
                reply = response.json().get("reply", "")
                st.markdown(f"\n{reply}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")

if st.button("Similar medicine"):
            if not user_input:
                st.warning("Medicine name missing")
            else:
                response = requests.post("http://127.0.0.1:5000/similar_medicine",json={"user_prompt": user_input})
            if response.status_code == 200:
                reply = response.json().get("reply", "")
                st.markdown(f"\n{reply}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
