import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI | PRO", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { 
        background-color: #161b22; 
        border-left: 5px solid #f55036; 
        padding: 20px; 
        border-radius: 10px; 
    }
    h1, h3 { color: #f55036; }
    .stButton>button { background-color: #f55036; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API SETUP ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing GROQ_API_KEY in secrets!")
    st.stop()

# --- 3. CORE UTILITIES ---
def encode_image(image):
    """Optimizes and converts image to Base64 for the Vision API."""
    buffer = io.BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.thumbnail((1000, 1000))
    image.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def text_to_speech(text):
    """Converts the Arabic response to an audio stream."""
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

def speech_to_text(audio_bytes):
    """Transcribes user voice to text using Whisper."""
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "input.wav"
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-large-v3-turbo",
        language="ar"
    )
    return transcription.text

# --- 4. MAIN USER INTERFACE ---
st.title("⚖️ FinDiagnostix AI: Professional Edition")
st.write("Upload a document for instant accounting analysis and voice interaction.")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# File Upload Section
uploaded_file = st.file_uploader("Upload Financial Document (JPG/PNG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.image(img, caption="Original Document", use_container_width=True)
    
    # Automatic Analysis triggered by upload
    if st.session_state.analysis_results is None:
        with st.spinner("AI Professor is analyzing using the latest model..."):
            try:
                base64_image = encode_image(img)
                
                # Using your specified model: openai/gpt-oss-120b
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract journal entries and provide a brief educational explanation in Arabic."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                st.session_state.analysis_results = response.choices[0].message.content
            except Exception as e:
                st.error(f"Model Error: {str(e)}")

    with col2:
        if st.session_state.analysis_results:
            st.markdown("### 📊 Accounting Journal & Explanation")
            st.markdown(f"<div class='report-card'>{st.session_state.analysis_results}</div>", unsafe_allow_html=True)

# --- 5. VOICE INTERACTION SECTION ---
if st.session_state.analysis_results:
    st.write("---")
    st.subheader("🎙️ Voice Chat with the Professor")
    
    # Mic Recording Component
    audio_record = mic_recorder(
        start_prompt="Click to Speak", 
        stop_prompt="Stop & Send", 
        key='recorder'
    )

    if audio_record:
        with st.spinner("Professor is listening..."):
            user_text = speech_to_text(audio_record['bytes'])
            st.info(f"You asked: {user_text}")

            # Chat with context
            res = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a professional Accounting Professor. Answer questions based on the previous analysis in Arabic. Be concise."},
                    {"role": "assistant", "content": st.session_state.analysis_results},
                    {"role": "user", "content": user_text}
                ]
            )
            professor_answer = res.choices[0].message.content
            st.success(f"Professor's Answer: {professor_answer}")

            # Automatic Voice Playback
            voice_output = text_to_speech(professor_answer)
            st.audio(voice_output, format='audio/mp3', autoplay=True)
    
