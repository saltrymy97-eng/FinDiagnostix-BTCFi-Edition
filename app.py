import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
from gtts import gTTS

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="FinDiagnostix AI | Groq Edition", layout="wide")

# Secure API Connection (Groq)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Missing! Please add 'GROQ_API_KEY' to Streamlit Secrets.")
    st.stop()

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Session State for stability
if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

st.title("⚡ FIN-DIAGNOSTIX: ULTRA-FAST AUDIT")
st.caption("Powered by Llama 3.2 Vision via Groq | Global Access Edition")

uploaded_file = st.file_uploader("Upload Document", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=400)
    
    if st.button("EXECUTE FAST AUDIT"):
        try:
            with st.spinner("Groq is processing at light speed..."):
                base64_image = encode_image(img)
                
                # Using Llama 3.2 11B Vision - High accuracy for OCR and Finance
                completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this financial document. 1. Journal Entry. 2. Risk Audit in Arabic."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    temperature=0.1 # Low temperature for financial accuracy
                )
                st.session_state.audit_report = completion.choices[0].message.content
                st.markdown(st.session_state.audit_report)
        except Exception as e:
            st.error(f"Error: {e}")

# Discussion remains the same
if st.session_state.audit_report:
    query = st.chat_input("Ask the Professor...")
    if query:
        # Voice generation logic here...
        st.write("Professor is responding...")
