import streamlit as st
import pandas as pd
import numpy as np
import re

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Smart Budget AI",
    layout="wide",
    page_icon="💳"
)

# ================== STRIPE STYLE UI ==================
st.markdown("""
<style>

body {
    background-color: #0a0f1c;
}

.main {
    background-color: #0a0f1c;
}

.title {
    font-size: 40px;
    font-weight: 700;
    color: #60a5fa;
}

.subtitle {
    color: #94a3b8;
    margin-bottom: 20px;
}

.card {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

.metric-box {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown('<div class="title">💳 Smart Budget AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Stripe-style Financial Intelligence Dashboard</div>', unsafe_allow_html=True)

# ================== INPUT ==================
col1, col2 = st.columns([2,1])

with col1:
    text = st.text_area("Project Description", height=150)

with col2:
    budget = st.number_input("Total Budget ($)", value=10000)

# ================== LAYER 1 ==================
def layer_1(text):
    numbers = list(map(int, re.findall(r'\d+', text)))
    complexity = len(numbers)

    keywords = ["debt", "owed", "credit", "receivable", "clients", "due"]
    receivable_flag = any(k in text.lower() for k in keywords)

    return numbers, complexity, receivable_flag

# ================== LAYER 2 ==================
def layer_2(budget, complexity, receivable_flag):

    risks = []

    if budget < 5000:
        risks.append("Low Budget Risk")

    if complexity > 8:
        risks.append("High Complexity Risk")

    if receivable_flag:
        risks.append("Cashflow / Receivables Risk")

    return risks

# ================== LAYER 3 ==================
def layer_3(budget, receivable_flag):

    categories = {
        "Operations": 0.35,
        "Marketing": 0.20,
        "Development": 0.25,
        "Emergency": 0.10,
        "Buffer": 0.10
    }

    df = pd.DataFrame({
        "Category": categories.keys(),
        "Allocation": categories.values()
    })

    df["Amount"] = df["Allocation"] * budget

    forecast = budget * np.random.uniform(1.2, 1.8)

    receivables = pd.DataFrame()

    if receivable_flag:
        receivables = pd.DataFrame([
            ["Client A", budget*0.10, "Pending"],
            ["Client B", budget*0.06, "Overdue"],
            ["Client C", budget*0.04, "Expected"]
        ], columns=["Client", "Amount", "Status"])

    return df, forecast, receivables

# ================== RUN ==================
if st.button("Run Analysis 🚀"):

    numbers, complexity, receivable_flag = layer_1(text)
    risks = layer_2(budget, complexity, receivable_flag)
    df, forecast, receivables = layer_3(budget, receivable_flag)

    # ================== KPI CARDS ==================
    st.markdown("## 📊 Overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="card">
        <h3>💰 Budget</h3>
        <h2>${budget:,}</h2>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
        <h3>📈 Forecast</h3>
        <h2>${forecast:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
        <h3>🧠 Complexity</h3>
        <h2>{complexity}</h2>
        </div>
        """, unsafe_allow_html=True)

    # ================== LAYERS ==================
    st.markdown("## 🟦 Risk Analysis")

    if risks:
        for r in risks:
            st.error(r)
    else:
        st.success("No major risks detected")

    # ================== ALLOCATION ==================
    st.markdown("## 📊 Budget Allocation")

    st.dataframe(df, use_container_width=True)

    st.bar_chart(df.set_index("Category")["Amount"])

    # ================== RECEIVABLES ==================
    st.markdown("## 🧾 Accounts Receivable")

    if not receivables.empty:
        st.dataframe(receivables, use_container_width=True)
    else:
        st.info("No receivables detected")
