import streamlit as st
import subprocess

st.set_page_config(page_title="Peak Automation Chatbot", page_icon="🤖")

st.title("🤖 Peak Automation Chatbot")

# Date range input
date_from = st.text_input("📅 Enter FROM date (dd/mm/yyyy)", "01/10/2025")
date_to = st.text_input("📅 Enter TO date (dd/mm/yyyy)", "31/10/2025")

# Task selection
task = st.selectbox("🧭 Select task to run", [
    "E-stamp downloader",
    "Receipt downloader",
    "Merge files",
    "Run ALL"
])

if st.button("🚀 Run Task"):
    try:
        if task == "E-stamp downloader":
            subprocess.run(["python", "download_estamp_v1.05.py", date_from, date_to])
        elif task == "Receipt downloader":
            subprocess.run(["python", "download_receipt_v1.05.py"])
        elif task == "Merge files":
            subprocess.run(["python", "merge_files_v1.02.py"])
        elif task == "Run ALL":
            subprocess.run(["python", "download_estamp_v1.05.py", date_from, date_to])
            subprocess.run(["python", "download_receipt_v1.05.py"])
            subprocess.run(["python", "merge_files_v1.02.py"]) 
        st.success(f"✅ {task} completed.")
    except Exception as e:
        st.error(f"❌ Error running {task}: {e}")