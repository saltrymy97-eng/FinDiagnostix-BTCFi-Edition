# smart_financial_ai_full.py

import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
from groq import Groq
import plotly.express as px
from fpdf import FPDF
from cryptography.fernet import Fernet

# -------------------------
# 1️⃣ Groq API
# -------------------------
API_KEY = "PUT_YOUR_KEY_HERE"  # ضع مفتاح Groq هنا
client = Groq(api_key=API_KEY)

# -------------------------
# 2️⃣ Encryption Key for Sensitive Data
# -------------------------
fernet_key = Fernet.generate_key()
cipher = Fernet(fernet_key)

# -------------------------
# Streamlit Page Setup
# -------------------------
st.set_page_config(page_title="Smart Financial AI", layout="wide")
st.title("💡 Smart Financial AI - Profit & Loan")
st.write("Simple interface: upload report → AI analysis → loan suggestion → what-if simulation → PDF report")

# -------------------------
# 3️⃣ Upload Report
# -------------------------
st.header("1️⃣ Upload Your Company Report")
uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])
uploaded_image = st.file_uploader("Or Upload an Image", type=["png","jpg","jpeg"])
df = None
extracted_text = ""

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("Report Loaded!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")

if uploaded_image:
    try:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        extracted_text = pytesseract.image_to_string(image)
        st.text_area("Extracted Text", extracted_text, height=200)
    except Exception as e:
        st.error(f"Error processing image: {e}")

# -------------------------
# 4️⃣ AI Analysis
# -------------------------
st.header("2️⃣ AI Profit Analysis")
ai_output_text = ""
if st.button("Analyze Profit"):
    try:
        input_text = "Analyze the company financial report for fake profit and missing data."
        if df is not None:
            input_text += f" Data sample: {df.head().to_dict()}"
        if uploaded_image:
            input_text += f" Extracted text: {extracted_text}"
        
        response = client.responses.create(
            model="groq/compound",
            input=input_text
        )
        ai_output_text = response.output_text
        st.subheader("AI Recommendations")
        st.write(ai_output_text)
    except Exception as e:
        st.error(f"AI Error: {e}")

# -------------------------
# 5️⃣ Loan Suggestion
# -------------------------
st.header("3️⃣ Loan Suggestion")
suggested_loan = 0
if st.button("Suggest Loan"):
    cash_flow = 0
    if df is not None and 'Cash Flow' in df.columns:
        cash_flow = df['Cash Flow'].sum()
    elif "negative cash flow" in ai_output_text.lower():
        cash_flow = -10000  # Default example
    
    if cash_flow < 0:
        suggested_loan = abs(cash_flow)*2
        st.success(f"Suggested Loan Amount: ${suggested_loan}")
    else:
        st.info("No loan needed, cash flow is positive.")

# -------------------------
# 6️⃣ What-If Loan Simulator
# -------------------------
st.header("4️⃣ What-If Loan Simulator")
loan_input = st.number_input("Enter Loan Amount", min_value=0)
interest = st.number_input("Interest Rate (%)", min_value=0.0)
months = st.number_input("Repayment Months", min_value=1)
if st.button("Simulate Loan"):
    monthly_payment = loan_input * (1 + interest/100) / months
    st.write(f"Monthly Payment: ${monthly_payment:.2f}")
    # Plot simple bar chart
    fig = px.bar(x=["Monthly Payment"], y=[monthly_payment], labels={"x":"Parameter","y":"Amount"})
    st.plotly_chart(fig)

# -------------------------
# 7️⃣ Download PDF Report
# -------------------------
st.header("5️⃣ Download PDF Report")
if st.button("Generate PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Smart Financial AI Report", ln=True, align='C')
    pdf.ln(10)
    if df is not None:
        pdf.multi_cell(0, 8, txt=f"Report Data Sample:\n{df.head().to_string()}")
    if ai_output_text:
        pdf.ln(5)
        pdf.multi_cell(0, 8, txt=f"AI Analysis:\n{ai_output_text}")
    if suggested_loan:
        pdf.ln(5)
        pdf.cell(0, 8, txt=f"Suggested Loan: ${suggested_loan}", ln=True)
    pdf_output_path = "financial_report.pdf"
    pdf.output(pdf_output_path)
    with open(pdf_output_path, "rb") as f:
        st.download_button("Download PDF", f, file_name="financial_report.pdf")
