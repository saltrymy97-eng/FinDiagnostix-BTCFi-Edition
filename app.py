import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Pro Edition", layout="wide")

# Custom CSS for Professional Dark UI
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #00d4ff; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #00d4ff; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #00d4ff; color: #0d1117; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Secure API Connection
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

# Using Gemini 1.5 Pro - The most advanced reasoning model for accounting
generation_config = {
    "temperature": 0.1, # Low temperature for high financial precision
    "top_p": 0.95,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    generation_config=generation_config
)

def generate_voice(text):
    """Converts text to Arabic audio stream."""
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

# --- 2. MAIN INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: PRO AUDITOR")
st.caption("Advanced Financial Intelligence | Engine: Gemini 1.5 Pro")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# PHASE 1: DIGITAL AUDIT
st.header("Phase 1: High-Precision Document Scan")
uploaded_file = st.file_uploader("Upload Financial Document (Invoice/Statement)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="Target Document")
        if st.button("EXECUTE PRO AUDIT"):
            try:
                with st.spinner("Analyzing with Gemini 1.5 Pro..."):
                    # Strict prompt for accounting accuracy
                    prompt = """
                    Analyze this document as a professional auditor:
                    1. Create a Journal Entry table (Debit/Credit).
                    2. Identify financial risks or errors in Arabic.
                    3. Provide a final Audit Verdict in Arabic based on IFRS.
                    """
                    response = model.generate_content([prompt, img])
                    st.session_state.audit_report = response.text
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# PHASE 2: ACADEMIC DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Voice Advisory")
    query = st.chat_input("Ask the Professor about the findings...")
    
    if query:
        with st.spinner("Formulating expert response..."):
            context = f"Report: {st.session_state.audit_report}\nUser: {query}"
            prompt = f"{context}\nAnswer as a professional Accounting Professor in Arabic."
            
            res = model.generate_content(prompt)
            answer = res.text
            
            with st.chat_message("assistant"):
                st.markdown(answer)
                audio_fp = generate_voice(answer)
                if audio_fp:
                    st.audio(audio_fp, format='audio/mp3')
