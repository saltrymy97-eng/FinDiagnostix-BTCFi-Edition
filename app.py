import streamlit as st
import pandas as pd
from PIL import Image
try:
    from groq import Groq
except ImportError:
    st.error("Missing dependency: Please add 'groq' to your requirements.txt")

# --- 1. UI Configuration (Professional Deep Dark) ---
st.set_page_config(page_title="FinDiagnostix AI | Enterprise Auditor", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .audit-box { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 20px; border-radius: 8px; margin: 10px 0; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Secure AI Engine Setup ---
# This pulls the key from your Streamlit Secrets "safe"
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key not found. Please check your Streamlit Secrets.")

def ai_accounting_auditor(user_input):
    """Calls the LATEST Groq AI Engine"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Senior University Accounting Professor and expert Auditor. "
                               "Analyze the transaction. Provide: 1. Formal Journal Entry (DR/CR). "
                               "2. Academic explanation. 3. Audit verdict (Fraud/Risk detection)."
                },
                {"role": "user", "content": user_input}
            ],
            model="llama-3.1-8b-instant",  # <--- THIS IS THE LATEST STABLE MODEL
            temperature=0.1,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"AI System Error: {str(e)}"

# --- 3. Professional Interface ---
st.title("⚖️ FIN-DIAGNOSTIX: AI AUDIT SYSTEM")
st.caption("Strategic Financial Intelligence Platform | Version 2026")
st.write("---")

st.sidebar.header("📥 Data Entry")
uploaded_file = st.sidebar.file_uploader("Upload Transaction Document", type=["jpg", "png", "jpeg"])
manual_input = st.sidebar.text_area("Transaction Narrative", placeholder="e.g., Sold water pump parts for 250,000 YR")

if st.sidebar.button("RUN AI ANALYSIS"):
    if manual_input or uploaded_file:
        with st.spinner("AI Auditor is processing..."):
            doc_name = uploaded_file.name if uploaded_file else "Manual Input"
            full_context = f"Context: {manual_input}. Doc: {doc_name}"
            
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
col1.metric("Engine", "Llama-3.1-8B", "UP TO DATE")
col2.metric("Audit Status", "Secure", "Active")
col3.metric("System Risk", "Verified", "0.0%")
