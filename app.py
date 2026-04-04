import streamlit as st
from groq import Groq
from PIL import Image
import io
import base64
from gtts import gTTS

# --- 1. INITIALIZATION & STYLING ---
st.set_page_config(page_title="FinDiagnostix AI | Vision Auditor", layout="wide")

# Professional Dark Theme
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #58a6ff; padding: 25px; border-radius: 15px; }
    h1, h2 { color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# Connection to Groq
if "GROQ_API_KEY" not in st.secrets:
    st.error("Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_image(image_file):
    """Resizes and optimizes the image for the Vision API."""
    img = Image.open(image_file)
    if img.mode in ("RGBA", "P"): 
        img = img.convert("RGB")
    img.thumbnail((1024, 1024)) # Optimize resolution
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_voice(text):
    """Converts text to Arabic voice."""
    tts = gTTS(text=text, lang='ar')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 2. MAIN INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: VISION & VOICE AUDITOR")
st.caption("Strategic Financial Intelligence Platform | Developed by Salem Al-Tamimi")
st.write("---")

if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# STEP 1: IMAGE UPLOAD
st.header("Step 1: Upload & Analyze Invoice")
uploaded_file = st.file_uploader("Upload an invoice or receipt image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(uploaded_file, caption="Uploaded Document")
        if st.button("RUN AI AUDIT"):
            try:
                with st.spinner("Analyzing the document..."):
                    img_b64 = process_image(uploaded_file)
                    
                    # Using the most stable Vision model
                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this invoice. Provide: 1. A Journal Entry Table (DR/CR). 2. Professional Accounting Explanation in Arabic. 3. Audit Verdict in Arabic."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                                ]
                            }
                        ],
                        temperature=0.1
                    )
                    st.session_state.audit_report = response.choices[0].message.content
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# STEP 2: VOICE DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Step 2: Voice Discussion with the Professor")
    
    query = st.chat_input("Ask the Professor... (e.g., هل القيد صحيح؟)")
    
    if query:
        with st.spinner("Professor is thinking..."):
            chat_res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional male Accounting Professor. Use the context of the analyzed invoice. Respond briefly in Arabic with authority."},
                    {"role": "assistant", "content": st.session_state.audit_report},
                    {"role": "user", "content": query}
                ]
            )
            answer = chat_res.choices[0].message.content
            
            # Display Answer
            with st.chat_message("assistant"):
                st.markdown(answer)
                # Output Voice
                st.audio(generate_voice(answer), format='audio/mp3')
    
