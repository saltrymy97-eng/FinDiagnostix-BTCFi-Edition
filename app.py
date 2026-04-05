import streamlit as st
from groq import Groq
from PIL import Image
import easyocr
import numpy as np
from gtts import gTTS
import speech_recognition as sr
import os

client = Groq(api_key="YOUR_API_KEY")
reader = easyocr.Reader(['en', 'ar'])

# 📷 OCR
def extract_text(image):
    image = np.array(image)
    return "\n".join(reader.readtext(image, detail=0))

# 🤖 AI accounting
def analyze(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an accounting teacher. Extract journal entries and explain briefly."
            },
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# 🎤 voice to text
def voice_to_text(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    return r.recognize_google(audio)

# 🔊 text to voice
def text_to_voice(text):
    tts = gTTS(text)
    tts.save("voice.mp3")
    return "voice.mp3"


# 🎯 UI
st.title("FIN-DIAGNOSTIX AI")

# 📷 Image part
file = st.file_uploader("Upload Image")

if file:
    img = Image.open(file)
    st.image(img)

    text = extract_text(img)
    st.text_area("Extracted Text", text)

    if st.button("Generate Accounting Entries"):
        result = analyze(text)
        st.write(result)

        audio = text_to_voice(result)
        st.audio(audio)

# 🎤 Voice input
audio_file = st.file_uploader("Upload Voice", type=["wav"])

if audio_file:
    text = voice_to_text(audio_file)
    st.write("You said:", text)

    if st.button("Answer"):
        result = analyze(text)
        st.write(result)

        audio = text_to_voice(result)
        st.audio(audio)
