import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
from gtts import gTTS

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI | Groq Edition", layout="wide")

# Professional Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #f55036; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #f55036; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #f55036; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Secure API Connection using Streamlit Secrets
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Missing! Please add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

# --- HELPER FUNCTIONS ---
def encode_image(image):
    """Encodes PIL image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_voice(text):
    """Converts AI text to Arabic speech."""
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# --- 2. SESSION STATE MANAGEMENT ---
if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""
if "uploaded_img" not in st.session_state:
    st.session_state.uploaded_img = None

# --- 3. MAIN UI ---
st.title("⚖️ FIN-DIAGNOSTIX: PRO AUDITOR")
st.caption("High-Speed Financial Intelligence | Engine: Llama 3.2 Vision")
st.write("---")

# File Uploader
file = st.file_uploader("Upload Financial Document (Invoice/Statement)", type=["jpg", "png", "jpeg"], key="doc_audit")

if file is not None:
    st.session_state.uploaded_img = Image.open(file)

# Execution Logic
if st.session_state.uploaded_img:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(st.session_state.uploaded_img, caption="Document Source", use_column_width=True)
        
        if st.button("EXECUTE AI AUDIT"):
            try:
                with st.spinner("Analyzing with Llama 3.2 Vision..."):
                    base64_image = encode_image(st.session_state.uploaded_img)
                    
                    # Groq Vision API Call
                    completion = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this document as an auditor. 1. Journal Entry Table. 2. Risk Audit in Arabic. 3. Audit Verdict in Arabic."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        temperature=0.1
                    )
                    st.session_state.audit_report = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# --- 4. PROFESSOR ADVISORY (VOICE) ---
if st.session_state.audit_report:
    st.write("---")
    st.header("Academic Consultation")
    user_query = st.chat_input("Ask the Professor about the findings...")
    
    if user_query:
        with st.spinner("Professor is responding..."):
            # Submitting to a text model for faster discussion
            chat_res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional Accounting Professor. Answer in Arabic."},
                    {"role": "user", "content": f"Report: {st.session_state.audit_report}\n\nQuestion: {user_query}"}
                ]
            )
            ans = chat_res.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(ans)
                audio_stream = generate_voice(ans)
                if audio_stream:
                    st.audio(audio_stream, format='audio/mp3')

st.sidebar.success("System Status: Operational")
st.sidebar.info("Developed by Salem Al-Tamimi")
    
