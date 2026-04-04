import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from gtts import gTTS

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Salem Al-Tamimi", layout="wide")

# Modern Dark UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #4285f4; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #4285f4; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #4285f4; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# SAFE API CONNECTION (Fetches from Secrets)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Error: GEMINI_API_KEY not found in Secrets. Please add it to Streamlit Settings.")
    st.stop()

# Using Gemini 1.5 Flash - The fastest stable vision engine
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_voice(text):
    """Converts Professor's response to Arabic Audio."""
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# --- 2. MAIN INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence Platform | Powered by Google Gemini")
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
        if st.button("EXECUTE AI AUDIT"):
            try:
                with st.spinner("Gemini is analyzing the financial structure..."):
                    # The prompt is sent directly with the image
                    prompt = """Analyze this invoice/document. Provide: 
                    1. A Journal Entry Table (DR/CR) in English. 
                    2. A professional accounting explanation in Arabic. 
                    3. An Audit Risk Verdict in Arabic."""
                    
                    response = model.generate_content([prompt, img])
                    st.session_state.audit_report = response.text
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# PHASE 2: ACADEMIC DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Voice Advisory")
    
    query = st.chat_input("Ask the Professor about this report...")
    
    if query:
        with st.spinner("The Professor is thinking..."):
            chat_context = f"Context: {st.session_state.audit_report}\n\nUser Question: {query}"
            chat_prompt = f"{chat_context}\n\nRespond as a professional male Accounting Professor. Be brief and speak in Arabic."
            
            res = model.generate_content(chat_prompt)
            answer = res.text
            
            with st.chat_message("assistant"):
                st.markdown(answer)
                voice_data = generate_voice(answer)
                if voice_data:
                    st.audio(voice_data, format='audio/mp3')

st.sidebar.info("System Status: SECURE\nEngine: Google Gemini 1.5 Flash")
