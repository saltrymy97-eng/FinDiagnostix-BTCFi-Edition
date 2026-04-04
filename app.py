import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="FinDiagnostix AI", page_icon="🚀", layout="wide")

# --- Custom CSS for Professional Look ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- Header Section ---
st.title("🚀 FinDiagnostix AI: Smart Accounting System")
st.markdown(f"### Coordinator: **Salem Al-Tamimi** | Accounting Dept. | {datetime.now().strftime('%Y-%m-%d')}")
st.write("---")

# --- 1. Session State Initialization ---
if 'ledger' not in st.session_state:
    st.session_state.ledger = []

# --- 2. AI Logic Engine ---
def analyze_transaction(text):
    text = text.lower()
    # Extract numeric amount
    amount = "".join(filter(str.isdigit, text))
    
    if any(word in text for word in ["buy", "purchase", "diesel", "fuel", "pay"]):
        return {"dr": "Purchases/Expenses", "cr": "Cash Account", "amt": amount}
    elif any(word in text for word in ["sell", "sales", "revenue", "receive"]):
        return {"dr": "Cash Account", "cr": "Sales Revenue", "amt": amount}
    else:
        return None

# --- 3. Sidebar Input ---
st.sidebar.header("📥 New Transaction")
st.sidebar.info("Example: 'Purchase diesel for 45000'")
user_input = st.sidebar.text_input("Describe the transaction:")

if st.sidebar.button("Analyze & Generate Entry"):
    result = analyze_transaction(user_input)
    if result and result['amt']:
        entry = {
            "Date": datetime.now().strftime("%H:%M:%S"),
            "Description": user_input,
            "Debit (DR)": result['dr'],
            "Credit (CR)": result['cr'],
            "Amount": float(result['amt']),
            "Status": "✅ Verified"
        }
        st.session_state.ledger.append(entry)
        st.sidebar.success("Entry Added Successfully!")
    else:
        st.sidebar.error("Could not interpret transaction. Try keywords like 'Buy' or 'Sell'.")

# --- 4. Audit & Fraud Detection (The Innovation) ---
st.header("🔍 Intelligent Audit Radar")
df = pd.DataFrame(st.session_state.ledger)

if not df.empty:
    # Anomaly Detection Logic
    if df['Amount'].max() > 100000:
        st.warning("⚠️ **High Risk Alert:** Large transaction detected (>100k). Verification required.")
    
    if df.duplicated(subset=['Amount']).any():
        st.info("💡 **Anomaly Detected:** Duplicate amounts found. Check for 'False Profit' manipulation.")

    # --- 5. Automated Ledger Display ---
    st.header("📑 Automated Digital Ledger")
    st.dataframe(df, use_container_width=True)

    # --- 6. Real-time Financial Metrics ---
    st.write("---")
    c1, c2, c3 = st.columns(3)
    total_exp = df[df['Debit (DR)'] == "Purchases/Expenses"]['Amount'].sum()
    total_rev = df[df['Debit (DR)'] == "Cash Account"]['Amount'].sum()
    balance = total_rev - total_exp
    
    c1.metric("Total Expenses", f"{total_exp:,.0f} YR")
    c2.metric("Total Revenue", f"{total_rev:,.0f} YR")
    c3.metric("Net Cash Position", f"{balance:,.0f} YR", delta=float(balance))
else:
    st.info("System Ready. Please enter a transaction in the sidebar to start analysis.")

# --- Footer ---
st.sidebar.write("---")
st.sidebar.caption("FinDiagnostix AI v1.0 | Supporting Vision 2026")
                
