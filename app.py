import streamlit as st
from groq import Groq
from PIL import Image
import io, base64
from gtts import gTTS

# --- 1. GLOBAL SETTINGS ---
st.set_page_config(page_title="FinDiagnostix AI | Salem Al-Tamimi", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_image(image_file):
    img = Image.open(image_file).convert("RGB")
    img.thumbnail((1024, 1024))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. PROFESSIONAL UI ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Advanced Financial AI Platform | Stable Production Edition")
st.write("---")

if "audit_report" not in st.session_state: st.session_state.audit_report = ""

# PHASE 1: VISION
st.header("Phase 1: Digital Audit Engine")
uploaded_file = st.file_uploader("Upload Financial Document", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, caption="Input Data")
        if st.button("EXECUTE AI AUDIT"):
            try:
                with st.spinner("Processing through Llama 3.2 Stable Vision..."):
                    img_b64 = process_image(uploaded_file)
                    # USING THE NEW PRODUCTION NAME
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-instant", 
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Identify data. Create Journal Entry Table. Arabic Verdict."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}]
                    )
                    st.session_state.audit_report = response.choices[0].message.content
            except Exception as e:
                st.error(f"Maintenance detected. Please refresh. Code: {e}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### Audit Findings\n{st.session_state.audit_report}")

# PHASE 2: VOICE
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Voice Advisory")
    query = st.chat_input("Consult the Professor...")
    if query:
        # USING THE LATEST FLAGSHIP MODEL
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Professional male Accounting Professor. Brief Arabic advice."},
                {"role": "assistant", "content": st.session_state.audit_report},
                {"role": "user", "content": query}
            ]
        )
        answer = res.choices[0].message.content
        with st.chat_message("assistant"):
            st.write(answer)
            st.audio(generate_voice(answer))
