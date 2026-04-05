import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI | PRO", layout="wide")

# Custom CSS for Professional Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { 
        background-color: #161b22; 
        border-left: 5px solid #f55036; 
        padding: 20px; 
        border-radius: 10px; 
        line-height: 1.6;
    }
    h1, h3 { color: #f55036; }
    .stButton>button { background-color: #f55036; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API INITIALIZATION ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Error: Please add your GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

# --- 3. CORE UTILITIES ---
def encode_image(image):
    """Optimizes and encodes image to Base64 for Vision API."""
    buffer = io.BytesIO()
    image.thumbnail((1000, 1000))
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def text_to_speech(text):
    """Converts AI response to Arabic audio stream."""
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

def speech_to_text(audio_bytes):
    """Transcribes user voice using Whisper-Large-V3-Turbo."""
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "input.wav"
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo",
        language="ar"
    )
    return transcription.text

# --- 4. MAIN INTERFACE ---
st.title("⚖️ FinDiagnostix AI: The Accounting Professor")
st.write("Upload a document, get the entries, and start a voice conversation.")

# Session State for Analysis Persistence
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# File Upload Section
uploaded_file = st.file_uploader("Upload Financial Document (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.image(img, caption="Document Preview", use_container_width=True)
    
    # Trigger AI Analysis only once upon upload
    if st.session_state.analysis_results is None:
        with st.spinner("Professor is analyzing the document..."):
            img_b64 = encode_image(img)
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional Accounting Professor. Analyze the image, extract Journal Entries, and explain them briefly in ARABIC."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this document and provide accounting entries with a short explanation in Arabic."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]
                    }
                ]
            )
            st.session_state.analysis_results = response.choices[0].message.content

    with col2:
        st.markdown("### 📊 Analysis & Journal Entries")
        st.markdown(f"<div class='report-card'>{st.session_state.analysis_results}</div>", unsafe_allow_html=True)

# --- 5. INTERACTIVE VOICE CHAT ---
if st.session_state.analysis_results:
    st.write("---")
    st.subheader("🎙️ Ask the Professor via Voice")
    
    # Mic Component
    audio_record = mic_recorder(
        start_prompt="Click to Speak", 
        stop_prompt="Stop & Send", 
        key='recorder'
    )

    if audio_record:
        # Step A: Voice to Text
        with st.spinner("Listening..."):
            user_text = speech_to_text(audio_record['bytes'])
            st.info(f"You said: {user_text}")

        # Step B: Chat with Context
        with st.spinner("The Professor is responding..."):
            res = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful Accounting Professor. Answer questions based on the previous analysis in ARABIC. Be concise."},
                    {"role": "assistant", "content": st.session_state.analysis_results},
                    {"role": "user", "content": user_text}
                ]
            )
            professor_answer = res.choices[0].message.content
            st.success(f"Professor: {professor_answer}")

            # Step C: Text to Voice (Autoplay)
            voice_output = text_to_speech(professor_answer)
            st.audio(voice_output, format='audio/mp3', autoplay=True)
    
