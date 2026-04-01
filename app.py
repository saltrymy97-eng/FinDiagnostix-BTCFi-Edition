import streamlit as st import pandas as pd from datetime import datetime

-------------------------

Page Config

-------------------------

st.set_page_config( page_title="Simple Fintech Pipeline", page_icon="💳", layout="wide" )

-------------------------

UI Style (Simple & Clean)

-------------------------

st.markdown("""

<style>
.block-container {
    padding: 2rem;
}
.card {
    background-color: #111827;
    padding: 18px;
    border-radius: 12px;
    color: white;
    margin-bottom: 12px;
    border: 1px solid #1f2937;
}
.title {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 5px;
}
.subtitle {
    color: #9ca3af;
    margin-bottom: 20px;
}
.section {
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: 600;
}
</style>""", unsafe_allow_html=True)

-------------------------

Sidebar Navigation (3 Layers)

-------------------------

step = st.sidebar.radio( "Pipeline Steps", ["1 - Upload Report", "2 - Classify Clients", "3 - Alerts & Insights", "4 - Recommendations", "5 - Budget"] )

-------------------------

Dummy Data

-------------------------

clients = pd.DataFrame({ "Name": ["Ali", "Sara", "Mohammed", "Lina"], "Balance": [5000, -1200, 300, -4500] })

-------------------------

Step 1: Upload Report

-------------------------

if step == "1 - Upload Report": st.markdown("<div class='title'>Upload Financial Report</div>", unsafe_allow_html=True)

file = st.file_uploader("Upload CSV Report")

if file:
    st.success("File uploaded successfully")
    st.dataframe(pd.read_csv(file))
else:
    st.info("Upload a file to start the pipeline")

-------------------------

Step 2: Client Classification

-------------------------

elif step == "2 - Classify Clients": st.markdown("<div class='title'>Client Classification</div>", unsafe_allow_html=True)

st.markdown("### Simple Segmentation")

good = clients[clients["Balance"] >= 0]
bad = clients[clients["Balance"] < 0]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='card'>🟢 Good Clients</div>", unsafe_allow_html=True)
    st.dataframe(good)

with col2:
    st.markdown("<div class='card'>🔴 Risk Clients</div>", unsafe_allow_html=True)
    st.dataframe(bad)

with col3:
    st.markdown("<div class='card'>⚪ Neutral</div>")
    st.write("No data")

-------------------------

Step 3: Alerts

-------------------------

elif step == "3 - Alerts & Insights": st.markdown("<div class='title'>Alerts</div>", unsafe_allow_html=True)

st.warning("⚠ High risk clients detected")
st.error("❌ Negative balances increasing")
st.info("📊 Cash flow stable in good clients")

-------------------------

Step 4: Recommendations

-------------------------

elif step == "4 - Recommendations": st.markdown("<div class='title'>Recommendations</div>", unsafe_allow_html=True)

st.markdown("""
<div class='card'>
1. Reduce exposure to high-risk clients
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='card'>
2. Improve collection process for debts
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='card'>
3. Increase credit control policies
</div>
""", unsafe_allow_html=True)

-------------------------

Step 5: Budget

-------------------------

elif step == "5 - Budget": st.markdown("<div class='title'>Budget Overview</div>", unsafe_allow_html=True)

income = 50000
expenses = 32000
balance = income - expenses

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Income", income)
with col2:
    st.metric("Expenses", expenses)
with col3:
    st.metric("Balance", balance)

st.progress(balance / income)
