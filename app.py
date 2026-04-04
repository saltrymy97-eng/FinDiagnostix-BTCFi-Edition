import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Salem Al-Tamimi", layout="wide")

# Custom Professional UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #4285f4; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #4285f4; }
    .stButton>button { background-color: #4285f4; color: white; font-weight: bold; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# Secure API Connection
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key Missing! Please add 'GEMINI_API_KEY' to your Streamlit Secrets.")
    st.stop()

# --- MODEL UPGRADE ---
# Using the most advanced reasoning model to avoid 404/Unsupported errors
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

def generate_voice(text):
    """Converts the AI response to Arabic Audio."""
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception as e:
        return None

# --- 2. MAIN INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence | Developed by Salem Al-Tamimi")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# PHASE 1: DIGITAL AUDIT
st.header("Phase 1: Digital Document Audit")
uploaded_file = st.file_uploader("Upload Invoice or Financial Statement", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        img = Image.open(uploaded_file)
        st.image(img, caption="Target Document")
        
        if st.button("EXECUTE PRO AI AUDIT"):
            try:
                with st.spinner("Analyzing document with Gemini 1.5 Pro..."):
                    # High-precision auditing prompt
                    prompt = """Analyze this financial document as a Senior Auditor. 
                    1. Extract data into a Journal Entry Table (Debit/Credit).
                    2. Provide a professional accounting explanation in Arabic.
                    3. State an Audit Risk Verdict in Arabic based on IFRS standards."""
                    
                    # Passing prompt and image as a list (Latest API Standard)
                    response = model.generate_content([prompt, img])
                    st.session_state.audit_report = response.text
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# PHASE 2: ACADEMIC DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Voice Advisory")
    
    query = st.chat_input("Ask the Professor about this report...")
    
    if query:
        with st.spinner("The Professor is formulating a response..."):
            chat_context = f"Context: {st.session_state.audit_report}\n\nUser Question: {query}"
            chat_prompt = f"{chat_context}\n\nRespond as a professional male Accounting Professor in Arabic."
            
            res = model.generate_content(chat_prompt)
            answer = res.text
            
            with st.chat_message("assistant"):
                st.markdown(answer)
                voice_data = generate_voice(answer)
                if voice_data:
                    st.audio(voice_data, format='audio/mp3')

st.sidebar.info("System Status: LIVE | Engine: Gemini 1.5 Pro")
