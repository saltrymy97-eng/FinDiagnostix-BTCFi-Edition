import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
import speech_recognition as sr
import asyncio
import edge_tts
import os

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="FIN-DIAGNOSTIX AI PRO", layout="wide")

st.title("⚖️ FIN-DIAGNOSTIX AI PRO (VISION + VOICE)")

# -----------------------------
# GROQ CLIENT
# -----------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# -----------------------------
# IMAGE PREP
# -----------------------------
def prepare_image(image):
    image = image.convert("RGB")
    image.thumbnail((600, 600))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=50)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()

    return img_b64

# -----------------------------
# VOICE TO TEXT
# -----------------------------
def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except:
        return "Could not understand audio"

# -----------------------------
# TEXT TO MALE VOICE (EDGE TTS)
# -----------------------------
async def text_to_speech(text, filename="voice.mp3"):
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")  # 👈 Male Voice
    await communicate.save(filename)
    return filename

def speak(text):
    file = "voice.mp3"
    asyncio.run(text_to_speech(text, file))
    return file

# -----------------------------
# IMAGE UPLOAD
# -----------------------------
file = st.file_uploader("Upload Financial Document", type=["jpg","png","jpeg"])

img_b64 = None

if file:
    image = Image.open(file)
    st.image(image, caption="Uploaded Document")

    img_b64 = prepare_image(image)

# -----------------------------
# VISION ANALYSIS
# -----------------------------
if img_b64 and st.button("Analyze Document"):
    with st.spinner("AI Vision analyzing..."):

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": "Analyze this financial document. Give journal entries, errors, risk analysis and fraud detection in Arabic."},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }],
            temperature=0.1
        )

        result = response.choices[0].message.content
        st.session_state["result"] = result

        st.success("Analysis Completed")
        st.write(result)

        # voice output
        audio_file = speak(result)
        st.audio(audio_file)

# -----------------------------
# CHAT SECTION
# -----------------------------
if "result" in st.session_state:

    st.write("---")
    st.subheader("💬 Chat with AI Professor")

    user_input = st.text_input("Ask a question")

    if user_input:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a professional accounting professor. Answer in Arabic."},
                {"role": "user", "content": f"Context:\n{st.session_state['result']}\n\nQuestion:{user_input}"}
            ]
        )

        answer = response.choices[0].message.content

        st.write(answer)

        audio = speak(answer)
        st.audio(audio)

# -----------------------------
# VOICE INPUT
# -----------------------------
st.write("---")
st.subheader("🎤 Voice Input (Upload Audio)")

audio_input = st.file_uploader("Upload WAV Audio", type=["wav"])

if audio_input:
    with open("input.wav", "wb") as f:
        f.write(audio_input.read())

    text = speech_to_text("input.wav")

    st.write("You said:", text)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )

    answer = response.choices[0].message.content

    st.write(answer)

    audio = speak(answer)
    st.audio(audio)
