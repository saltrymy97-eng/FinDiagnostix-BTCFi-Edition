import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
try:
    from groq import Groq
except ImportError:
    st.error("Missing dependency: Please add 'groq' to your requirements.txt")

# --- 1. Enterprise UI Configuration ---
st.set_page_config(page_title="FinDiagnostix AI | Enterprise Auditor", layout="wide")

# Custom Professional CSS (Deep Dark Theme)
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .audit-box { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 20px; border-radius: 5px; margin: 10px 0; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI Engine Setup (Groq) ---
# FIXED: This now reads directly from your Streamlit Secrets "safe"
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key not found in Secrets. Please check your Streamlit App Settings.")

def ai_accounting_auditor(user_input):
    """Calls Groq AI to act as a Professor and Auditor"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior University Accounting Professor and expert Auditor. "
                               "Analyze the user's transaction. Provide: 1. A formal Journal Entry (DR/CR). "
                               "2. Academic explanation of the logic. 3. Audit verdict on potential 'False Profit' or risks."
                },
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192",
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 3. Main Interface ---
st.title("⚖️ FIN-DIAGNOSTIX: AI AUDIT SYSTEM")
st.caption("Strategic Financial Intelligence Platform | Developed by Salem Al-Tamimi")
st.write("---")

# Sidebar for Inputs
st.sidebar.header("📥 Data Entry")
uploaded_file = st.sidebar.file_uploader("Upload Transaction Document", type=["jpg", "png", "jpeg"])
manual_input = st.sidebar.text_area("Transaction Narrative", placeholder="e.g., Purchased fuel for 50,000 YR")

if st.sidebar.button("RUN AI ANALYSIS"):
    if manual_input or uploaded_file:
        with st.spinner("AI Auditor is processing..."):
            doc_name = uploaded_file.name if uploaded_file else "None"
            full_context = f"File: {doc_name}. Context: {manual_input}"
            
            report = ai_accounting_auditor(full_context)
            
            st.subheader("🔍 PROFESSOR'S AUDIT REPORT")
            st.markdown(f"<div class='audit-box'>{report}</div>", unsafe_allow_html=True)
            
            if uploaded_file:
                st.sidebar.image(Image.open(uploaded_file), caption="Processed Document", use_container_width=True)
    else:
        st.sidebar.warning("Please provide input data.")

# --- 4. System Integrity Metrics ---
st.write("---")
col1, col2, col3 = st.columns(3)
col1.metric("Engine", "Groq Llama-3", "Active")
col2.metric("Audit Status", "Real-time", "Secure")
col3.metric("System Risk", "Monitored", "0.0%")
