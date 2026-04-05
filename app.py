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
    st.error("Missing API Key!")
    st.stop()

# ---------------------------
# 3. AUTO CROP + COMPRESS
# ---------------------------
def prepare_image(image):
    width, height = image.size

    # Crop center (reduce useless parts)
    left = width * 0.1
    right = width * 0.9
    top = height * 0.2
    bottom = height * 0.8

    image = image.crop((left, top, right, bottom))

    # Resize small
    image.thumbnail((500, 300))

    # Compress strongly
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=40, optimize=True)

    # Convert to Base64
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Limit size (VERY IMPORTANT)
    return img_b64[:4000]

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

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a professional financial auditor."
                            },
                            {
                                "role": "user",
                                "content": f"""
Analyze this financial document image.

Provide:
- Journal Entries
- Errors
- Risk Analysis
- Fraud Detection
- Recommendations

Answer in Arabic.

Image Data:
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
# 8. AI CHAT
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
