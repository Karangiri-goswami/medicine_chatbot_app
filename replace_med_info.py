import sys

with open("streamlit.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_medicine_info = """elif page == "Medicine Info":

    st.subheader("Comprehensive Medicine Dashboard")

    current_med = st.query_params.get("med", "")
    med = st.text_input("Enter Medicine Name", value=current_med)
    if med != current_med:
        st.query_params["med"] = med
        st.rerun()

    if st.button("Generate Comprehensive Report"): 
        if med:
            with st.spinner("Analyzing and fetching all data... This may take a few seconds."):
                
                # Fetch visual reference
                img_url = "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500"
                try:
                    img_response = requests.post(f"{BASE_URL}/get_image", json={"medicine_name": med}, headers=headers, timeout=8)
                    if img_response.status_code == 200:
                        fetched_url = img_response.json().get("image_url")
                        if fetched_url:
                            img_url = fetched_url
                except Exception:
                    pass
                    
                st.image(img_url, width=350, caption=f"Reference Visual for {med}")
                
                # Fetch all data sequentially
                res_details = requests.post(f"{BASE_URL}/medicine_details", json={"language": selected_lang, "user_prompt": med}, headers=headers).json()
                res_explain = requests.post(f"{BASE_URL}/ai_explain", json={"language": selected_lang, "user_prompt": med}, headers=headers).json()
                res_alt = requests.post(f"{BASE_URL}/similar_medicine", json={"language": selected_lang, "user_prompt": med}, headers=headers).json()
                res_links = requests.post(f"{BASE_URL}/medicine_links", json={"language": selected_lang, "user_prompt": med}, headers=headers).json()

                # Build Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Details", "🧠 AI Explain", "🔄 Alternatives", "🛒 Pharmacy Links"])

                with tab1:
                    if res_details.get("status") == "success":
                        display_ai_response(res_details.get("reply"))
                    else:
                        st.error("Error fetching medicine details.")
                
                with tab2:
                    if res_explain.get("status") == "success":
                        display_ai_response(res_explain.get("reply"))
                    else:
                        st.error("Error fetching AI explanation.")
                
                with tab3:
                    if res_alt.get("status") == "success":
                        display_ai_response(res_alt.get("reply"))
                    else:
                        st.error("Error fetching alternatives.")
                        
                with tab4:
                    if res_links.get("status") == "success":
                        st.markdown("### 🤖 Tips")
                        display_ai_response(res_links.get("ai_suggestions"))

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("### 🛒 Online Pharmacies")
                            for item in res_links.get("links", {}).get("online_pharmacies", []):
                                st.markdown(f"- [{item['name']}]({item['url']})")
                        with col2:
                            st.markdown("### 📘 Medical Info")
                            for item in res_links.get("links", {}).get("medical_info", []):
                                st.markdown(f"- [{item['name']}]({item['url']})")
                    else:
                        st.error("Error fetching pharmacy links.")
        else:
            st.warning("Enter medicine name")

"""

out = []
skip = False
for line in lines:
    if line.startswith('elif page == "Medicine Info":'):
        out.append(new_medicine_info)
        skip = True
        continue
    elif line.startswith('elif page == "Generate Text":'):
        skip = False
        
    if not skip:
        out.append(line)

with open("streamlit.py", "w", encoding="utf-8") as f:
    f.writelines(out)

