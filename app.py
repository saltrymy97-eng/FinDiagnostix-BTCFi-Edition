# simple_financial_ai.py
import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
from groq import Groq

# -------------------------
# 1️⃣ Groq API
# -------------------------
API_KEY = "PUT_YOUR_KEY_HERE"
client = Groq(api_key=API_KEY)

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(page_title="Smart Financial AI", layout="wide")
st.title("💡 Smart Financial AI - Profit & Loan")

# -------------------------
# 2️⃣ Upload Report
# -------------------------
st.header("1️⃣ Upload Your Company Report")
uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])
uploaded_image = st.file_uploader("Or Upload an Image", type=["png","jpg","jpeg"])
df = None
extracted_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("Report Loaded!")
    st.dataframe(df.head())

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    extracted_text = pytesseract.image_to_string(image)
    st.text_area("Extracted Text", extracted_text, height=200)

# -------------------------
# 3️⃣ AI Analysis
# -------------------------
st.header("2️⃣ AI Profit Analysis")
if st.button("Analyze Profit"):
    input_text = "Analyze company report for fake profit and missing data."
    if df is not None:
        input_text += f" Data sample: {df.head().to_dict()}"
    if uploaded_image:
        input_text += f" Extracted text: {extracted_text}"
    
    response = client.responses.create(
        model="groq/compound",
        input=input_text
    )
    st.subheader("AI Recommendations")
    st.write(response.output_text)

# -------------------------
# 4️⃣ Loan Suggestion
# -------------------------
st.header("3️⃣ Loan Suggestion")
if st.button("Suggest Loan"):
    # Simple logic: if Cash Flow negative, suggest loan = 2*abs(Cash Flow)
    cash_flow = 0
    if df is not None and 'Cash Flow' in df.columns:
        cash_flow = df['Cash Flow'].sum()
    elif "negative cash flow" in response.output_text.lower():
        cash_flow = -10000  # default example
    if cash_flow < 0:
        suggested_loan = abs(cash_flow)*2
        st.success(f"Suggested Loan Amount: ${suggested_loan}")
    else:
        st.info("No loan needed, cash flow is positive.")

# -------------------------
# 5️⃣ What-If Loan Simulator
# -------------------------
st.header("4️⃣ What-If Loan Simulator")
loan_input = st.number_input("Enter Loan Amount", min_value=0)
interest = st.number_input("Interest Rate (%)", min_value=0.0)
months = st.number_input("Repayment Months", min_value=1)
if st.button("Simulate Loan"):
    monthly_payment = loan_input * (1 + interest/100)/months
    st.write(f"Monthly Payment: ${monthly_payment:.2f}")
