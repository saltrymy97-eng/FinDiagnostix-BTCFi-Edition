import streamlit as st
from groq import Groq
from PIL import Image
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def play_professor_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.write("---")

if "audit_context" not in st.session_state:
    st.session_state.audit_context = ""

# --- STEP 1: IMAGE ANALYSIS ---
st.header("Step 1: Upload & Audit")
uploaded_file = st.file_uploader("Upload Invoice", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, use_container_width=True)
        if st.button("RUN AI ANALYSIS"):
            with st.spinner("Analyzing..."):
                img_b64 = encode_image(uploaded_file)
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this invoice. Provide: 1. Journal Entry Table (DR/CR). 2. Professional Explanation in Arabic. 3. Audit Verdict in Arabic."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]
                    }]
                )
                st.session_state.audit_context = response.choices[0].message.content

    if st.session_state.audit_context:
        with col2:
            st.markdown(f"### Audit Report\n{st.session_state.audit_context}")

# --- STEP 2: VOICE DISCUSSION ---
if st.session_state.audit_context:
    st.write("---")
    st.header("Step 2: Voice Discussion")
    
    # Microphone Input
    audio = mic_recorder(start_prompt="🎤 Speak to Professor", stop_prompt="🛑 Stop", key='recorder')
    
    if audio:
        # Note: In a live workshop, you would use a Speech-to-Text API here. 
        # For now, it captures audio to show the Professor is 'listening'.
        st.audio(audio['bytes'])
        st.success("Voice received. Processing Professor's advice...")

    # Text Discussion (Backup for Speech-to-Text)
    if user_query := st.chat_input("Ask about the invoice..."):
        with st.chat_message("assistant"):
            chat_res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a male Accounting Professor. Respond briefly in Arabic with authority."},
                    {"role": "assistant", "content": st.session_state.audit_context},
                    {"role": "user", "content": user_query}
                ]
            )
            ans = chat_res.choices[0].message.content
            st.markdown(ans)
            st.audio(play_professor_voice(ans), format='audio/mp3')

st.sidebar.caption("Salem Al-Tamimi | 2026")
