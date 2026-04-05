import streamlit as st
from groq import Groq
import base64
import io
from PIL import Image
from gtts import gTTS

# ---------------------------
# 1. PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="FinDiagnostix AI | PRO", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .report-card { background-color: #161b22; border-left: 5px solid #f55036; padding: 20px; border-radius: 10px; }
    h1, h2 { color: #f55036; }
    .stButton>button { background-color: #f55036; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------
# 2. API SETUP
# ---------------------------
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing API Key! Add GROQ_API_KEY in Streamlit secrets.")
    st.stop()

# ---------------------------
# 3. IMAGE PROCESSING
# ---------------------------
def prepare_image(image):
    max_size = (1280, 720)
    image.thumbnail(max_size)

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)

    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# ---------------------------
# 4. TEXT TO SPEECH
# ---------------------------
def generate_voice(text):
    try:
        tts = gTTS(text=text, lang='ar')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

# ---------------------------
# 5. SESSION STATE
# ---------------------------
if "audit_report" not in st.session_state:
    st.session_state.audit_report = ""

if "current_img" not in st.session_state:
    st.session_state.current_img = None

# ---------------------------
# 6. MAIN UI
# ---------------------------
st.title("⚖️ FIN-DIAGNOSTIX AI (GLOBAL PRO)")
st.write("---")

file = st.file_uploader("Upload Financial Document", type=["jpg", "png", "jpeg"])

if file:
    st.session_state.current_img = Image.open(file)

if st.session_state.current_img:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(st.session_state.current_img, caption="Document Loaded")

        if st.button("RUN FULL AUDIT"):
            try:
                with st.spinner("AI is analyzing..."):

                    img_b64 = prepare_image(st.session_state.current_img)

                    # IMPORTANT: Using latest stable model
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a world-class financial auditor AI."
                            },
                            {
                                "role": "user",
                                "content": f"""
Analyze this financial document and provide:

1. Journal Entries
2. Financial Errors (if any)
3. Risk Analysis
4. Fraud Detection
5. Professional Recommendations

Answer in Arabic.

Encoded Image:
{img_b64}
"""
                            }
                        ],
                        temperature=0.1
                    )

                    st.session_state.audit_report = response.choices[0].message.content

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # ---------------------------
    # 7. REPORT DISPLAY
    # ---------------------------
    if st.session_state.audit_report:
        with col2:
            st.markdown(
                f"### 📊 Final Audit Report\n<div class='report-card'>{st.session_state.audit_report}</div>",
                unsafe_allow_html=True
            )

# ---------------------------
# 8. AI PROFESSOR CHAT
# ---------------------------
if st.session_state.audit_report:
    st.write("---")

    query = st.chat_input("Ask the AI Professor...")

    if query:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a professional Accounting Professor. Answer in Arabic."},
                {"role": "user", "content": f"Context:\n{st.session_state.audit_report}\n\nQuestion: {query}"}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content

        with st.chat_message("assistant"):
            st.write(answer)

            audio = generate_voice(answer)
            if audio:
                st.audio(audio)
