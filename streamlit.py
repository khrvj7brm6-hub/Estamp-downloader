import streamlit as st
import subprocess
from pathlib import Path
import os

st.set_page_config(page_title="Accounting Automation", page_icon="🤖")
st.title("🤖 Accounting Automation")

# Initialize session state
if "process" not in st.session_state:
    st.session_state.process = None

# Date range input
date_from = st.text_input("📅 Enter FROM date (dd/mm/yyyy)", "01/10/2025")
date_to = st.text_input("📅 Enter TO date (dd/mm/yyyy)", "31/10/2025")

# Folder selection
folder_name = st.text_input("Enter folder name for saving files")
if folder_name:
    save_dir = Path("downloads") / folder_name
    save_dir.mkdir(parents=True, exist_ok=True)
    st.success(f"Files will be saved to: {save_dir}")

# Task selection
task = st.selectbox("🧭 Select task to run", [
    "E-stamp downloader",
    "Receipt downloader",
    "Merge files",
    "Run ALL"
])

# Run Task
if st.button("🚀 Run Task"):
    try:
        with st.status(f"Running {task}...", expanded=True) as status:
            if task == "E-stamp downloader":
                st.session_state.process = subprocess.Popen(
                    ["python", "download_estamp_v1.05.py", date_from, date_to],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            elif task == "Receipt downloader":
                st.session_state.process = subprocess.Popen(
                    ["python", "download_receipt_v1.05.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            elif task == "Merge files":
                st.session_state.process = subprocess.Popen(
                    ["python", "merge_files_v1.02.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            elif task == "Run ALL":
                st.session_state.process = subprocess.Popen(
                    ["python", "run_all.py", date_from, date_to],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

            for line in st.session_state.process.stdout:
                st.write(line.strip())
            st.session_state.process.wait()
            status.update(label=f" {task} completed.", state="complete")
            st.session_state.process = None

    except Exception as e:
        st.error(f"Error running {task}: {e}")
        st.session_state.process = None

# Cancel Task
if st.button("Cancel Task"):
    if st.session_state.process:
        st.session_state.process.terminate()
        st.success("Task cancelled.")
        st.session_state.process = None