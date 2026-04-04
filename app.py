import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
from gtts import gTTS
import io

# --- 1. Page Configuration (Enterprise Look) ---
st.set_page_config(page_title="FinDiagnostix AI | Auditor & Voice Advisor", layout="wide")

# Custom Professional CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .audit-box { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 20px; border-radius: 8px; margin: 10px 0; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Secure Engine Setup ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("API Key not found. Please check Streamlit Secrets.")

# Voice Function (Arabic TTS)
def play_arabic_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 3. Main Interface ---
st.title("⚖️ FIN-DIAGNOSTIX: AI AUDIT SYSTEM")
st.caption("Strategic Financial Intelligence Platform | Developed by Salem Al-Tamimi")
st.write("---")

# Sidebar for Invoice Auditing
st.sidebar.header("📥 Data Entry")
uploaded_file = st.sidebar.file_uploader("Upload Transaction Document", type=["jpg", "png", "jpeg"])
manual_input = st.sidebar.text_area("Transaction Narrative", placeholder="e.g., Purchased goods on credit for 500,000 YR")

if st.sidebar.button("RUN AI ANALYSIS"):
    if manual_input or uploaded_file:
        with st.spinner("Analyzing..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a Senior Auditor. Analyze the transaction. Provide Journal Entry (DR/CR) and Audit Verdict."},
                    {"role": "user", "content": manual_input}
                ]
            )
            report = completion.choices[0].message.content
            st.subheader("🔍 PROFESSOR'S AUDIT REPORT")
            st.markdown(f"<div class='audit-box'>{report}</div>", unsafe_allow_html=True)
            if uploaded_file:
                st.sidebar.image(Image.open(uploaded_file), use_container_width=True)

# --- 4. Interactive Chat & Arabic Voice Advisor ---
st.subheader("👨‍🏫 Academic & Voice Advisor")
st.info("Ask the Professor about the transaction in Arabic (e.g., هل اشترينا بالأجل؟)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input (Arabic/English supported)
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("The Professor is thinking..."):
            chat_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a Senior Accounting Professor. Respond in Arabic. Provide professional audit advice."},
                    *st.session_state.messages
                ]
            )
            response_text = chat_response.choices[0].message.content
            st.markdown(response_text)
            
            # Generate and Play Voice
            audio_fp = play_arabic_voice(response_text)
            st.audio(audio_fp, format='audio/mp3')
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- 5. System Status ---
st.write("---")
col1, col2, col3 = st.columns(3)
col1.metric("Engine", "Llama-3.1-8B", "Active")
col2.metric("Voice System", "Arabic (gTTS)", "Ready")
col3.metric("System Risk", "Monitored", "0.0%")
            
