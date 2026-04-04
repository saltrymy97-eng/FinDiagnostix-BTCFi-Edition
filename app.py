import streamlit as st
from groq import Groq
from PIL import Image
import io, base64
from gtts import gTTS

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Salem Al-Tamimi", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 25px; border-radius: 15px; }
    h1, h2 { color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_image(image_file):
    img = Image.open(image_file).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence Platform | Stable 2026 Edition")
st.write("---")

if "audit_report" not in st.session_state: st.session_state.audit_report = ""

# STEP 1: VISION AUDIT
st.header("Step 1: Digital Document Audit")
uploaded_file = st.file_uploader("Upload Financial Document", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, caption="Input Document")
        if st.button("EXECUTE STABLE AUDIT"):
            try:
                with st.spinner("Analyzing via Llama 3.2 Stable..."):
                    img_b64 = process_image(uploaded_file)
                    # USING THE NEW STABLE PRODUCTION MODEL NAME
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-instant", 
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Extract data. Create DR/CR Table. Professional Arabic Explanation."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}]
                    )
                    st.session_state.audit_report = response.choices[0].message.content
            except Exception as e:
                st.error(f"Maintenance in progress. Try again in 10 seconds. (Error: {e})")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# STEP 2: VOICE CONSULTATION
if st.session_state.audit_report:
    st.write("---")
    st.header("Step 2: Academic Voice Discussion")
    query = st.chat_input("Consult the Professor...")
    if query:
        # USING THE NEW STABLE 70B VERSATILE MODEL
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Professional male Accounting Professor. Brief Arabic advice."},
                {"role": "assistant", "content": st.session_state.audit_report},
                {"role": "user", "content": query}
            ]
        )
        ans = res.choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(ans)
            st.audio(generate_voice(ans))
    
