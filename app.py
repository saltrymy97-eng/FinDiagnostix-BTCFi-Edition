import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_config_title="FinDiagnostix AI - Accounting Workshop", layout="wide")

# Header Section
st.title("🚀 FinDiagnostix AI: Smart Accounting & Audit System")
st.markdown("### Developed & Coordinated by: **Salem Al-Tamimi** | Accounting Department")
st.write("---")

# 1. Session State Initialization
if 'ledger' not in st.session_state:
    st.session_state.ledger = []

# 2. The AI Logic Engine (Pattern Recognition)
def analyze_transaction_ai(text):
    text = text.lower()
    # Extract numbers for the amount
    amount = "".join(filter(str.isdigit, text))
    
    # AI Logic: Identifying Accounts based on keywords
    if any(word in text for word in ["buy", "purchase", "diesel", "fuel"]):
        return {"debit": "Purchases (Fuel/Operating)", "credit": "Cash Account", "amount": amount}
    elif any(word in text for word in ["sell", "sales", "revenue", "received"]):
        return {"debit": "Cash Account", "credit": "Sales Revenue", "amount": amount}
    elif any(word in text for word in ["salary", "wage", "pay"]):
        return {"debit": "Salary Expense", "credit": "Cash Account", "amount": amount}
    else:
        return None

# 3. Sidebar: Input Section
st.sidebar.header("📥 Transaction Entry")
st.sidebar.info("Type a natural sentence (e.g., 'Purchase diesel for 50000')")
user_input = st.sidebar.text_input("Describe the transaction:")

if st.sidebar.button("Analyze with AI"):
    result = analyze_transaction_ai(user_input)
    if result and result['amount']:
        entry = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Description": user_input,
            "Debit (DR)": result['debit'],
            "Credit (CR)": result['credit'],
            "Amount": float(result['amount']),
            "Status": "✅ Validated"
        }
        st.session_state.ledger.append(entry)
        st.sidebar.success("AI Analysis Complete: Entry Generated!")
    else:
        st.sidebar.error("AI could not interpret. Please check the keywords.")

# 4. Audit Radar & Fraud Detection (The "Magic" Part)
st.header("🔍 Intelligent Audit Radar")

df = pd.DataFrame(st.session_state.ledger)

def fraud_detection_alerts(data):
    alerts = []
    if not data.empty:
        # Check for unusually high amounts (Threshold: 100,000)
        high_risk = data[data['Amount'] > 100000]
        if not high_risk.empty:
            alerts.append(f"🔴 **High Risk Alert:** {len(high_risk)} transaction(s) exceed standard limits. Manual audit required.")
            
        # Check for duplicate amounts (Potential False Profit/Fraud)
        duplicates = data.duplicated(subset=['Amount'], keep=False)
        if duplicates.any():
            alerts.append("🟡 **Anomaly Detected:** Identical amounts found in multiple entries. Potential duplicate or 'False Profit' manipulation.")
            
    return alerts

# Display Alerts
alerts = fraud_detection_alerts(df)
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("Audit Radar: All clear. No anomalies detected yet.")

# 5. Smart Digital Ledger
st.header("📑 Automated Digital Ledger")
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Financial Analytics (Metrics)
    st.write("---")
    m1, m2, m3 = st.columns(3)
    total_expenses = df[df['Debit (DR)'].str.contains("Expense|Purchases", na=False)]['Amount'].sum()
    total_revenue = df[df['Credit (CR)'].str.contains("Sales", na=False)]['Amount'].sum()
    net_position = total_revenue - total_expenses
    
    m1.metric("Total Expenses", f"{total_expenses:,.0f} YR")
    m2.metric("Total Revenue", f"{total_revenue:,.0f} YR")
    m3.metric("Net Cash Position", f"{net_position:,.0f} YR", delta=net_position)
else:
    st.info("Waiting for first entry to initialize ledger analysis...")

# 6. Workshop Footer
st.sidebar.write("---")
st.sidebar.markdown("""
**Workshop Vision:** Bridging the gap between traditional Accounting and Modern AI tools.  
*Target: 100% Accuracy & Real-time Fraud Prevention.*
""")
        
