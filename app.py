import streamlit as st
from groq import Groq
from PIL import Image
import pytesseract

# ---------------------------
# 1. PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="FIN-DIAGNOSTIX AI | WORKSHOP", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #c9d1d9; }
.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #f55036;
}
h1 { color: #f55036; }
.stButton>button {
    background-color: #f55036;
    color: white;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 2. GROQ API
# ---------------------------
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key missing!")
    st.stop()

# ---------------------------
# 3. OCR FUNCTION
# ---------------------------
def extract_text(image):
    return pytesseract.image_to_string(image, lang="eng+ara")

# ---------------------------
# 4. SESSION STATE
# ---------------------------
if "report" not in st.session_state:
    st.session_state.report = ""

# ---------------------------
# 5. UI
# ---------------------------
st.title("⚖️ FIN-DIAGNOSTIX AI (WORKSHOP MODE)")
st.write("---")

file = st.file_uploader("Upload Financial Document", type=["jpg", "png", "jpeg"])

if file:
    image = Image.open(file)
    st.image(image, caption="Uploaded Document")

    if st.button("RUN ANALYSIS"):
        with st.spinner("Extracting text & analyzing..."):

            # 1. OCR
            text = extract_text(image)

            # 2. AI Analysis
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional CPA financial auditor. Answer in Arabic."
                    },
                    {
                        "role": "user",
                        "content": f"""
Analyze this accounting text:

{text}

Provide:
- Journal Entries
- Errors
- Risk Analysis
- Fraud Detection
- Recommendations
"""
                    }
                ],
                temperature=0.2
            )

            st.session_state.report = response.choices[0].message.content

# ---------------------------
# 6. OUTPUT
# ---------------------------
if st.session_state.report:
    st.markdown("## 📊 Audit Report")
    st.markdown(f"<div class='card'>{st.session_state.report}</div>", unsafe_allow_html=True)

    st.download_button(
        "Download Report",
        st.session_state.report,
        file_name="audit_report.txt"
            )
