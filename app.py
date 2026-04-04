import streamlit as st
from groq import Groq
from PIL import Image
import io
import base64
from gtts import gTTS

# --- 1. INITIALIZATION ---
st.set_page_config(page_title="FinDiagnostix AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def encode_image(image_file):
    # Resize and optimize image quality for API
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    img.thumbnail((800, 800))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def play_voice(text):
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")

if "context" not in st.session_state:
    st.session_state.context = ""

uploaded_file = st.file_uploader("Upload Invoice", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file)
        if st.button("RUN AI ANALYSIS"):
            try:
                with st.spinner("Professor is analyzing..."):
                    base64_image = encode_image(uploaded_file)
                    # Correct Payload Structure for Llama 3.2 Vision
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this invoice. Create a DR/CR Table. Provide a brief accounting explanation and audit verdict in Arabic."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        temperature=0.1 # Lower temperature for accuracy
                    )
                    st.session_state.context = response.choices[0].message.content
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

    if st.session_state.context:
        with col2:
            st.markdown(f"### Audit Result\n{st.session_state.context}")

# --- 3. VOICE DISCUSSION ---
if st.session_state.context:
    st.write("---")
    query = st.chat_input("Ask the Professor about this invoice...")
    if query:
        with st.spinner("Professor is responding..."):
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional male Accounting Professor. Give brief strategic advice in Arabic based on the provided audit context."},
                    {"role": "assistant", "content": st.session_state.context},
                    {"role": "user", "content": query}
                ]
            )
            ans = res.choices[0].message.content
            st.chat_message("assistant").write(ans)
            st.audio(play_voice(ans))
