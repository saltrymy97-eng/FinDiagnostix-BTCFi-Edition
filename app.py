import streamlit as st
import anthropic
import base64
import io
from PIL import Image
from gtts import gTTS

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="FinDiagnostix AI | Claude Edition", layout="wide")

# Professional Dark UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #d97757; padding: 25px; border-radius: 15px; }
    h1, h2, h3 { color: #d97757; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #d97757; color: white; border-radius: 8px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Secure API Connection (Anthropic)
if "ANTHROPIC_API_KEY" in st.secrets:
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
else:
    st.error("API Key Missing! Please add 'ANTHROPIC_API_KEY' to your Streamlit Secrets.")
    st.stop()

# --- UTILITY FUNCTIONS ---
def encode_image(image):
    """Converts PIL image to base64 for Claude's Vision API."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_voice(text):
    """Converts the Professor's response to Arabic Audio."""
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# --- 2. SESSION STATE MANAGEMENT ---
# Prevents losing the image and report when the app reruns
if "uploaded_img" not in st.session_state:
    st.session_state.uploaded_img = None
if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

# --- 3. MAIN INTERFACE ---
st.title("⚖️ FIN-DIAGNOSTIX: CLAUDE VISION")
st.caption("Advanced Financial Auditing | Developed by Salem Al-Tamimi")
st.write("---")

# File Uploader with a unique key
uploaded_file = st.file_uploader("Upload Invoice or Financial Statement", type=["jpg", "png", "jpeg"], key="audit_uploader")

if uploaded_file is not None:
    # Save to session state immediately
    st.session_state.uploaded_img = Image.open(uploaded_file)

# Only show the logic if an image exists in the session
if st.session_state.uploaded_img:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(st.session_state.uploaded_img, caption="Loaded Document", use_column_width=True)
        
        if st.button("EXECUTE CLAUDE AUDIT", key="run_audit"):
            try:
                with st.spinner("Claude 3.5 Sonnet is analyzing financial logic..."):
                    img_base64 = encode_image(st.session_state.uploaded_img)
                    
                    # Anthropic Vision API Call
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20240620",
                        max_tokens=2048,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "image/png",
                                            "data": img_base64,
                                        },
                                    },
                                    {
                                        "type": "text", 
                                        "text": "Analyze this financial document as a professional auditor. 1. Provide a Journal Entry Table. 2. Identify potential liquidity risks in Arabic. 3. Provide an Audit Verdict in Arabic."
                                    }
                                ],
                            }
                        ],
                    )
                    st.session_state.audit_report = response.content[0].text
            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")

    if st.session_state.audit_report:
        with col2:
            st.markdown(f"### 📊 Audit Intelligence Report\n<div class='report-card'>{st.session_state.audit_report}</div>", unsafe_allow_html=True)

# PHASE 2: ACADEMIC DISCUSSION
if st.session_state.audit_report:
    st.write("---")
    st.header("Phase 2: Academic Advisory")
    
    query = st.chat_input("Ask the Professor about this report...")
    
    if query:
        with st.spinner("The Professor is formulating a response..."):
            res = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": f"Context: {st.session_state.audit_report}\n\nQuestion: {query}. Respond in professional academic Arabic."}
                ]
            )
            answer = res.content[0].text
            
            with st.chat_message("assistant"):
                st.markdown(answer)
                voice_data = generate_voice(answer)
                if voice_data:
                    st.audio(voice_data, format='audio/mp3')

st.sidebar.info("Status: Engine Switched to Claude 3.5 Sonnet")
    
