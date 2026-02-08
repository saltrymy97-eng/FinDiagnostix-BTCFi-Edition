# FinDiagnostix-BTCFi-Edition
FinDiagnostix is a Python/Streamlit MVP that detects the "Paper Profit Trap" in BTC treasuries. It uses a Prescriptive AI Engine to calculate Cash Runway and triggers automated BTCFi actions (like Lightning settlements) based on real-time liquidity risk simulation.


import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="FinDiagnostix | Bitcoin AI CFO", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM STYLING (Added Bitcoin Orange Accent) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #f7931a; padding: 15px; border-radius: 10px; }
    .action-card { background-color: #1c2128; border-left: 5px solid #f7931a; padding: 20px; border-radius: 8px; margin: 10px 0; }
    .warning-card { background-color: #1c2128; border-left: 5px solid #da3633; padding: 20px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: BTCFi DATA INPUT ---
st.sidebar.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png", width=80)
st.sidebar.title("BTCFi Treasury Input")
st.sidebar.info("Simulate your Bitcoin-native company's financials.")

# Inputs are now in BTC for the theme, with USD conversion logic
btc_price = 45000  # Mock BTC Price for conversion
revenue_btc = st.sidebar.number_input("Monthly Revenue (BTC)", value=2.5)
cash_btc = st.sidebar.number_input("Current BTC Holdings", value=0.4)
receivables_btc = st.sidebar.number_input("Accounts Receivable (BTC)", value=1.6)
payables_btc = st.sidebar.number_input("Accounts Payable (BTC)", value=1.2)
burn_rate_btc = st.sidebar.number_input("Monthly Burn Rate (BTC)", value=0.5)

# --- LOGIC: BTCFi DIAGNOSTIC ENGINE ---
paper_profit_gap = receivables_btc - payables_btc
cash_runway = round(cash_btc / (burn_rate_btc / 30)) if burn_rate_btc > 0 else 999
is_risky = cash_btc < payables_btc

# --- MAIN INTERFACE ---
st.title("📊 FinDiagnostix [BTCFi Edition]")
st.markdown("*Bridging the Gap between Bitcoin Liquidity and Business Survival*")
st.write("---")

# 1. THE PULSE (Bitcoin Metrics)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total BTC Liquidity", f"₿ {cash_btc:.4f}", delta=f"${(cash_btc * btc_price):,.0f} USD")
with col2:
    st.metric("BTC Cash Runway", f"{cash_runway} Days", delta="CRITICAL" if cash_runway < 30 else "STABLE", delta_color="inverse" if cash_runway < 30 else "normal")
with col3:
    st.metric("Paper Profit Gap", f"₿ {paper_profit_gap:.4f}", help="BTC earned on paper but not yet in your wallet.")

st.write("### 🧠 AI Diagnostic Lab (Bitcoin Intelligence)")

if is_risky:
    st.markdown(f"""
    <div class="warning-card">
        <h3 style='color:#da3633;'>⚠️ Alert: Bitcoin Liquidity Gap Detected</h3>
        <p>Your treasury holds <b>₿ {cash_btc:.4f}</b>, but you have <b>₿ {payables_btc:.4f}</b> in obligations due. You are facing a 'Paper Profit Trap'.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("#### ⚡ Automated Action (BTCFi Strategy)")
    st.markdown("""
    <div class="action-card">
        <p><b>BTC-Backed Liquidity Injection:</b> Instead of selling your BTC, leverage your ₿ 1.6 in receivables as collateral to secure an instant <b>Lightning Network Loan</b> of ₿ 0.8. This extends your runway by 45 days without losing Bitcoin upside exposure.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Alternative BTC Strategies"):
        st.write("1. **Lightning Settlements:** Offer a 2% discount for invoices paid via Lightning Network to settle receivables 10x faster.")
        st.write("2. **Stablecoin Hedging:** Convert 10% of payables to BTC-backed stablecoins to mitigate short-term volatility risk.")
else:
    st.success("Your BTC Treasury is healthy. AI suggests increasing Bitcoin allocation.")

# 2. THE SIMULATOR (Sats version)
st.write("---")
st.write("### 🧪 BTC Efficiency Simulator")
boost = st.slider("Improve Collection via Lightning Network (%)", 0, 100, 30)
simulated_cash = cash_btc + (receivables_btc * (boost / 100))
st.info(f"By accelerating collections via Lightning, your liquid BTC position grows to **₿ {simulated_cash:.4f}**")

# 3. PITCH MODE (Adapted for btc/acc)
if st.checkbox("Show btc/acc Pitch Points"):
    st.write("---")
    st.subheader("🎤 Pitching for the Bitcoin Accelerator")
    st.write("**The BTC Hook:** 'SMEs in the Bitcoin ecosystem don't die from low BTC prices; they die from poor liquidity management.'")
    st.write("**The BTCFi Solution:** 'FinDiagnostix is the AI CFO that manages BTC treasury and solves the Paper Profit Trap using Bitcoin-native actions.'")
    st.write("**Innovation:** 'We turn static Bitcoin balances into active business intelligence.'")
    
