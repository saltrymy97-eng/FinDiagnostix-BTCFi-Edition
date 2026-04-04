import streamlit as st
from groq import Groq
from PIL import Image
import io, base64
from gtts import gTTS

# --- 1. THEME & PAGE CONFIG ---
st.set_page_config(page_title="FinDiagnostix AI | Professional Auditor", layout="wide")

# Professional Dark UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Segoe UI', Tahoma, sans-serif; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; border: none; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# Secure API Connection
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add 'GROQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. CORE UTILITIES ---
def process_image(image_file):
    """Prepares the image for high-speed AI processing."""
    img = Image.open(image_file).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_voice(text):
    """Converts the AI response into Arabic Audio."""
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 3. MAIN APPLICATION INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence Platform | Stable Production Release")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# PHASE 1: DIGITAL DOCUMENT AUDIT
st.header("Phase 1: Digital Document Audit")
uploaded_file = st.file_uploader("Upload Invoice, Receipt, or Financial Statement", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, caption="Input Data")
        if st.button("EXECUTE AI AUDIT"):
            try:
                with st.spinner("Scanning through available AI engines..."):
                    img_b64 = process_image(uploaded_file)
                    
                    # SMART MODEL FALLBACK SYSTEM
                    # This list ensures that if one model is down, the code tries the next one automatically
                    model_pool = [
                        "llama-3.2-11b-vision-instant",
                        "llama-3.2-90b-vision-instant",
                        "llama-3.2-11b-vision-preview",
                        "llama-3.2-90b-vision-preview"
                    ]
                    
                    audit_response = None
                    for engine in model_pool:
                        try:
                            audit_response = client.chat.completions.create(
                                model=engine,
                                messages=[{
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Analyze this document. Create a Journal Entry (DR/CR) Table. Provide a brief Accounting Explanation and Audit Verdict in Arabic."},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                                    ]
                                }]
                            )
                            if audit_response: break
                        except:
                            continue
                    
                    if audit_response:
                        st.session_state.audit_report = audit_response.choices[0].message.content
                    else:
                        st.error("Global maintenance detected. Please refresh the page in 30 seconds.")
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# PHASE 2: ACADEMIC DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Voice Advisory")
    
    query = st.chat_input("Consult the Professor (e.g., Explain the risks...)")
    
    if query:
        with st.spinner("The Professor is formulating a response..."):
            # Using the latest 70B flagship model for high-quality logic
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a professional male Accounting Professor. Respond briefly in Arabic with authority and clarity."},
                        {"role": "assistant", "content": st.session_state.audit_report},
                        {"role": "user", "content": query}
                    ]
                )
                answer = res.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    # Voice Output
                    st.audio(generate_voice(answer), format='audio/mp3')
            except:
                st.error("Discussion engine is currently updating. Please try again.")

st.sidebar.info("Workshop Status: LIVE\nSystem: Self-Healing AI Engine")
    
