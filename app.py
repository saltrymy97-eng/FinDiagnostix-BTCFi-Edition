# advanced_financial_ai.py
import streamlit as st
import os
import pandas as pd
import plotly.express as px
from groq import Groq
from cryptography.fernet import Fernet
from PIL import Image
import pytesseract
from fpdf import FPDF

# -------------------------
# 1️⃣ Groq API Key
# -------------------------
API_KEY = os.getenv("GROQ_API_KEY", "PUT_YOUR_KEY_HERE")
client = Groq(api_key=API_KEY)

# -------------------------
# 2️⃣ Page setup
# -------------------------
st.set_page_config(page_title="Smart Financial AI", layout="wide")
st.title("💡 Smart Financial AI - Profit Checker & Loan Simulator")

# -------------------------
# 3️⃣ Tabs
# -------------------------
tabs = st.tabs(["📄 Upload Report", "📊 Analysis & AI", "💰 Loan Simulator", "🔒 Encrypt Data", "📄 PDF Report"])

# -------------------------
# Tab 1: Upload Data
# -------------------------
with tabs[0]:
    st.header("Upload Company Financial Report")
    uploaded_file = st.file_uploader("Upload CSV/Excel file", type=["csv", "xlsx"])
    uploaded_image = st.file_uploader("Or Upload an Image of the Report", type=["png","jpg","jpeg"])
    
    df = None
    extracted_text = ""
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File loaded successfully!")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    if uploaded_image:
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Report", use_column_width=True)
            extracted_text = pytesseract.image_to_string(image)
            st.text_area("Extracted Text from Image", extracted_text, height=200)
        except Exception as e:
            st.error(f"Error processing image: {e}")

# -------------------------
# Tab 2: Profit Analysis + AI
# -------------------------
with tabs[1]:
    st.header("🚀 AI Profit Analysis & Recommendations")
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
            st.subheader("AI Recommendations")
            st.write(response.output_text)
            
            # Plot example chart
            if df is not None and 'Revenue' in df.columns and 'Expenses' in df.columns:
                fig = px.bar(df, x=df.index, y=['Revenue', 'Expenses'], title="Revenue vs Expenses")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"AI Error: {e}")

# -------------------------
# Tab 3: Loan Simulator
# -------------------------
with tabs[2]:
    st.header("💰 Loan Simulator")
    loan_amount = st.number_input("Loan Amount", min_value=0)
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0)
    months = st.number_input("Repayment Months", min_value=1)
    
    if st.button("Simulate Loan"):
        monthly_payment = loan_amount * (1 + interest_rate/100) / months
        st.write(f"Monthly Payment: {monthly_payment:.2f}")
        # Optional: simple chart
        fig = px.line(x=list(range(1, months+1)), y=[monthly_payment]*months, labels={'x':'Month','y':'Payment'}, title="Loan Payment Schedule")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Tab 4: Encrypt Data
# -------------------------
with tabs[3]:
    st.header("🔒 Encrypt Sensitive Data")
    key = Fernet.generate_key()
    fernet = Fernet(key)
    sample_text = st.text_area("Enter text to encrypt")
    if st.button("Encrypt"):
        if sample_text:
            encrypted = fernet.encrypt(sample_text.encode())
            st.write(encrypted)
        else:
            st.warning("Enter text first.")

# -------------------------
# Tab 5: Generate PDF Report
# -------------------------
with tabs[4]:
    st.header("📄 PDF Report")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Smart Financial AI Report", ln=True, align="C")
        pdf.ln(10)
        if df is not None:
            pdf.multi_cell(0, 8, df.head().to_string())
        if uploaded_image:
            pdf.ln(5)
            pdf.multi_cell(0, 8, "Extracted Text from Image:")
            pdf.multi_cell(0, 8, extracted_text)
        pdf_file = "financial_report.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, file_name="financial_report.pdf")
