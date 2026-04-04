import streamlit as st
from groq import Groq
from PIL import Image
from gtts import gTTS
import io
import base64

# --- 1. SETTINGS ---
st.set_page_config(page_title="FinDiagnostix AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_and_encode(image_file):
    # Resize image to prevent BadRequestError
    img = Image.open(image_file)
    img.thumbnail((800, 800)) 
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def play_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION AUDITOR")
st.write("---")

if "context" not in st.session_state: st.session_state.context = ""

# STEP 1: UPLOAD
uploaded_file = st.file_uploader("Upload Invoice Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file)
        if st.button("RUN ANALYSIS"):
            try:
                with st.spinner("Analyzing..."):
                    img_b64 = process_and_encode(uploaded_file)
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analyze this. Provide: 1. DR/CR Table. 2. Arabic Explanation. 3. Arabic Verdict."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}]
                    )
                    st.session_state.context = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.context:
        with col2:
            st.markdown(st.session_state.context)

# STEP 2: CHAT & VOICE
if st.session_state.context:
    st.write("---")
    query = st.chat_input("Ask the Professor...")
    if query:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a male Accounting Professor. Respond briefly in Arabic."},
                {"role": "assistant", "content": st.session_state.context},
                {"role": "user", "content": query}
            ]
        )
        ans = res.choices[0].message.content
        st.write(ans)
        st.audio(play_voice(ans))
