import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI", layout="wide")

# Secure API Key Retrieval
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- UI INTERFACE ---
st.title("⚖️ Professional Audit System")
st.write("---")

uploaded_file = st.file_uploader("Upload Document", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=400)
    
    if st.button("RUN AI AUDIT"):
        try:
            with st.spinner("Analyzing using Recommended Models..."):
                base_64_img = encode_image(img)
                
                # Using Llama 3.2 11B Vision (The recommended replacement in your screenshots)
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Perform a financial audit. Provide Journal Entries and Risk Analysis in Arabic."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_64_img}"}}
                            ]
                        }
                    ]
                )
                st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error: {e}")
