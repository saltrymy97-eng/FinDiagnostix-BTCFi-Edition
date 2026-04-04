import streamlit as st
from groq import Groq
from PIL import Image
import io
import base64
from gtts import gTTS

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Vision Auditor", layout="wide")

# Professional Dark UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# API Connectivity
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. CORE FUNCTIONS ---
def process_image(image_file):
    """Optimizes image for high-speed AI analysis."""
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((1024, 1024))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_voice(text):
    """Converts the Professor's response to Arabic Audio."""
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 3. MAIN WORKSHOP INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence Platform | Developed by Salem Al-Tamimi")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# STEP 1: IMAGE UPLOAD & ANALYSIS
st.header("Phase 1: Digital Document Audit")
uploaded_file = st.file_uploader("Upload Invoice or Receipt", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, caption="Target Document")
        if st.button("RUN AI AUDIT"):
            try:
                with st.spinner("Analyzing document structure..."):
                    img_b64 = process_image(uploaded_file)
                    
                    # Using the latest stable vision model
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview", 
                        messages=[{
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": "Analyze this invoice. Provide: 1. A Journal Entry Table (DR/CR). 2. Professional Accounting Explanation in Arabic. 3. Audit Risk Verdict in Arabic."
                                },
                                {
                                    "type": "image_url", 
                                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                                }
                            ]
                        }]
                    )
                    st.session_state.audit_report = response.choices[0].message.content
            except Exception as e:
                st.error(f"System Update in progress. Please retry in 1 minute. ({str(e)})")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# STEP 2: VOICE INTERACTION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Discussion")
    
    query = st.chat_input("Ask the Professor... (e.g., Is this transaction high risk?)")
    
    if query:
        with st.spinner("Generating expert response..."):
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional male Accounting Professor. Respond briefly in Arabic with authority and clarity."},
                    {"role": "assistant", "content": st.session_state.audit_report},
                    {"role": "user", "content": query}
                ]
            )
            answer = res.choices[0].message.content
            
            # Show response in chat format
            with st.chat_message("assistant"):
                st.markdown(answer)
                # Auto-play Professor's Voice
                st.audio(generate_voice(answer), format='audio/mp3')

st.sidebar.info("Workshop Mode: Active\nEngine: Llama 3.2 Vision")
