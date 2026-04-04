import streamlit as st
from groq import Groq
from PIL import Image
import io
import base64
from gtts import gTTS

# --- 1. SETUP ---
st.set_page_config(page_title="FinDiagnostix AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_image(image_file):
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((800, 800))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

uploaded_file = st.file_uploader("Upload Invoice", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file)
        if st.button("RUN AI AUDIT"):
            try:
                with st.spinner("Connecting to Secure Server..."):
                    img_b64 = process_image(uploaded_file)
                    
                    # TRIAL 1: THE NEW STABLE MODEL
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-instant", 
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analyze invoice: Create DR/CR Table. Arabic Explanation. Arabic Verdict."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}]
                    )
                    st.session_state.audit_report = response.choices[0].message.content
            except Exception:
                try:
                    # FALLBACK: IF FIRST ONE FAILS, TRY THE LARGER MODEL
                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-instant",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analyze invoice: Create DR/CR Table. Arabic Explanation. Arabic Verdict."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}]
                    )
                    st.session_state.audit_report = response.choices[0].message.content
                except Exception as final_e:
                    st.error("Server maintenance in progress. Please try again in 30 seconds.")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### Audit Report\n{st.session_state.audit_report}")

# --- 3. VOICE DISCUSSION ---
if st.session_state.audit_report:
    st.write("---")
    query = st.chat_input("Ask the Professor...")
    if query:
        # Using the absolute latest chat model
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a male Accounting Professor. Respond briefly in Arabic."},
                {"role": "assistant", "content": st.session_state.audit_report},
                {"role": "user", "content": query}
            ]
        )
        ans = res.choices[0].message.content
        st.chat_message("assistant").write(ans)
        st.audio(generate_voice(ans))
                    
