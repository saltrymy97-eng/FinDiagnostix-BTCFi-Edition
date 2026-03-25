import streamlit as st
import sqlite3
import os
import pandas as pd
import plotly.express as px
from groq import Groq
from fpdf import FPDF
from cryptography.fernet import Fernet

# =========================
# Page Setup
# =========================
st.set_page_config(page_title="Smart Liquidity AI – Dashboard", layout="wide")
st.title("🏦 Smart Liquidity AI – Secure Dashboard")
st.subheader("Detect Fake Profit + Loan Simulation + AI Recommendation + Encrypted Approval + PDF Report")

# =========================
# Groq AI setup
# =========================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# AES Encryption setup (Fernet)
# =========================
key_file = "secret.key"
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
else:
    with open(key_file, "rb") as f:
        key = f.read()
fernet = Fernet(key)

# =========================
# Database setup
# =========================
conn = sqlite3.connect("companies.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS companies
             (id INTEGER PRIMARY KEY, name TEXT, revenue REAL, expenses REAL, cash_flow REAL, debt REAL, approval TEXT)''')
conn.commit()

# =========================
# Company Data Input
# =========================
st.sidebar.header("📝 Company Data")
company_name = st.sidebar.text_input("Company Name", "Sample Company")
revenue = st.sidebar.number_input("Revenue", value=100000)
expenses = st.sidebar.number_input("Expenses", value=80000)
cash_flow = st.sidebar.number_input("Cash Flow", value=-5000)
debt = st.sidebar.number_input("Debt", value=20000)

if st.sidebar.button("💾 Save Company"):
    encrypted_approval = fernet.encrypt("Not Approved".encode()).decode()
    c.execute("INSERT INTO companies (name, revenue, expenses, cash_flow, debt, approval) VALUES (?,?,?,?,?,?)",
              (company_name, revenue, expenses, cash_flow, debt, encrypted_approval))
    conn.commit()
    st.sidebar.success("✅ Company saved with encrypted approval")

# =========================
# Basic Analysis
# =========================
st.header("📈 Basic Financial Analysis")
profit = revenue - expenses
st.write(f"Accounting Profit: {profit}")
st.write(f"Cash Flow: {cash_flow}")

fake_profit = False
if profit > 0 and cash_flow < 0:
    fake_profit = True
    st.error("⚠️ Fake Profit Detected: Positive profit but negative cash flow")
else:
    st.success("✅ Financial status is balanced")

# =========================
# Risk Score Calculation
# =========================
st.header("⚖️ Risk Assessment")
risk_score = 0
if fake_profit:
    risk_score += 50
if cash_flow < 0:
    risk_score += 30
if debt > revenue * 0.5:
    risk_score += 20

risk_color = "green" if risk_score < 30 else "orange" if risk_score < 70 else "red"
st.markdown(f"<h3 style='color:{risk_color}'>Risk Score: {risk_score}/100</h3>", unsafe_allow_html=True)

# =========================
# Loan Simulation
# =========================
st.header("💰 Loan What-If Simulation")
loan_amounts = st.multiselect("Select Loan Amounts", [10000,20000,30000,50000], default=[20000])
interest_rate = st.slider("Interest Rate (%)", 0, 50, 10) / 100
months = st.slider("Loan Duration (Months)", 1, 60, 12)

simulation_results = []
for loan in loan_amounts:
    new_cash = cash_flow + loan
    monthly_payment = (loan * (1 + interest_rate)) / months
    status = "✅ Beneficial" if new_cash > 0 and monthly_payment < (revenue*0.3) else "⚠️ Risky"
    simulation_results.append({"Loan": loan, "New Cash": new_cash, "Monthly Payment": monthly_payment, "Status": status})

sim_df = pd.DataFrame(simulation_results)
st.dataframe(sim_df)

# =========================
# Loan Chart
# =========================
st.header("📊 Loan Impact Chart")
fig = px.bar(sim_df, x="Loan", y="New Cash", color="Status", text="Monthly Payment",
             color_discrete_map={"✅ Beneficial":"green","⚠️ Risky":"red"}, title="Loan Impact on Cash Flow")
st.plotly_chart(fig)

# =========================
# AI Recommendation
# =========================
st.header("🤖 AI Recommendation")
if st.button("Run AI"):
    prompt = f"""
    Company Analysis:
    Name: {company_name}
    Revenue: {revenue}
    Expenses: {expenses}
    Cash Flow: {cash_flow}
    Debt: {debt}

    1. Detect Fake Profit?
    2. Risk Score?
    3. Does the company need a loan?
    4. Loan simulation: {loan_amounts}
    5. Provide short recommendation for each loan
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )
        result = response.choices[0].message.content
        st.write(result)

        # Encrypt approval based on AI recommendation
        approval_text = "Approved" if "✅ Beneficial" in result else "Not Approved"
        encrypted_approval = fernet.encrypt(approval_text.encode()).decode()
        c.execute("UPDATE companies SET approval=? WHERE name=?", (encrypted_approval, company_name))
        conn.commit()
        st.success("🔒 Loan approval updated and encrypted in database")
    except Exception as e:
        st.error("❌ AI connection error")
        st.write(e)

# =========================
# PDF Report
# =========================
st.header("📄 Download PDF Report")
if st.button("Generate PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Company Report: {company_name}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Accounting Profit: {profit}", ln=True)
    pdf.cell(200, 10, txt=f"Cash Flow: {cash_flow}", ln=True)
    pdf.cell(200, 10, txt=f"Risk Score: {risk_score}/100", ln=True)

    pdf.cell(200, 10, txt="Loan Simulation Results:", ln=True)
    for index, row in sim_df.iterrows():
        pdf.cell(200, 10, txt=f"Loan: {row['Loan']}, New Cash: {row['New Cash']}, Monthly Payment: {row['Monthly Payment']:.2f}, Status: {row['Status']}", ln=True)
    
    # Include encrypted approval
    st_c = c.execute("SELECT approval FROM companies WHERE name=?", (company_name,)).fetchone()[0]
    pdf.cell(200, 10, txt=f"Encrypted Approval: {st_c}", ln=True)
    
    pdf.output("Company_Report_Secure.pdf")
    st.success("✅ PDF Report generated with encrypted approval: Company_Report_Secure.pdf")

# =========================
# Display Saved Companies
# =========================
st.header("🏢 Saved Companies")
df = pd.read_sql_query("SELECT * FROM companies", conn)
st.dataframe(df)
