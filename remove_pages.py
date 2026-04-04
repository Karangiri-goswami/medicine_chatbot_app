with open("streamlit.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip = False
for line in lines:
    if line.strip() in ['{nav_item("AI Explain")}', '{nav_item("Alternatives")}', '{nav_item("Pharmacy Links")}']:
        continue
    
    if line.startswith('elif page == "AI Explain":'):
        skip = True
    elif line.startswith('elif page == "Generate Text":'):
        skip = False
        
    if not skip:
        out.append(line)

with open("streamlit.py", "w", encoding="utf-8") as f:
    f.writelines(out)
