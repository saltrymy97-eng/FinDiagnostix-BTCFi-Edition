import streamlit as st
import pandas as pd
import numpy as np
import re

# ================= CONFIG =================
st.set_page_config(page_title="Smart Budget AI Pro", layout="wide")

st.title("💰 Smart Budget AI PRO")
st.write("3-Layer Financial AI System + Accounts Receivable Module")

# ================= INPUT =================
text = st.text_area("📥 Project Description (include debts / receivables if any)")
budget = st.number_input("💵 Total Budget", value=10000)

# ================= LAYER 1 =================
def layer_1(text):

    numbers = list(map(int, re.findall(r'\d+', text)))

    # simple detection for receivables keywords
    receivable_keywords = ["debt", "owed", "credit", "receivable", "clients", "due"]
    receivable_flag = any(word in text.lower() for word in receivable_keywords)

    complexity = len(numbers)

    return {
        "numbers": numbers,
        "complexity": complexity,
        "receivables_detected": receivable_flag
    }

# ================= LAYER 2 =================
def layer_2(budget, analysis):

    warnings = []

    if budget < 5000:
        warnings.append("Low budget risk")

    if analysis["complexity"] > 10:
        warnings.append("High project complexity")

    if analysis["receivables_detected"]:
        warnings.append("Accounts receivable detected → liquidity risk possible")

    if budget / (analysis["complexity"] + 1) < 700:
        warnings.append("Budget efficiency is weak")

    return warnings

# ================= LAYER 3 =================
def layer_3(budget, analysis):

    # ===== Budget Allocation =====
    categories = {
        "Operations": 0.35,
        "Marketing": 0.20,
        "Development": 0.25,
        "Emergency": 0.10,
        "Receivables Buffer": 0.10
    }

    df = pd.DataFrame({
        "Category": categories.keys(),
        "Ratio": categories.values()
    })

    df["Amount"] = df["Ratio"] * budget

    # ===== Receivables Module =====
    receivables = []

    if analysis["receivables_detected"]:
        receivables = [
            {"Client": "Client A", "Amount": budget * 0.1, "Status": "Pending"},
            {"Client": "Client B", "Amount": budget * 0.07, "Status": "Overdue"},
            {"Client": "Client C", "Amount": budget * 0.05, "Status": "Expected"}
        ]

    receivables_df = pd.DataFrame(receivables) if receivables else pd.DataFrame(
        columns=["Client", "Amount", "Status"]
    )

    # ===== Forecast =====
    cashflow_risk = 1.0

    if analysis["receivables_detected"]:
        cashflow_risk = 0.8

    forecast = budget * np.random.uniform(1.1, 1.6) * cashflow_risk

    # ===== Recommendations =====
    recommendations = [
        "Focus on cash flow stability",
        "Reduce dependency on receivables",
        "Collect overdue payments faster",
        "Maintain emergency reserve",
        "Validate expenses before scaling"
    ]

    return df, receivables_df, forecast, recommendations

# ================= RUN PIPELINE =================
if st.button("🚀 Run AI Financial Analysis"):

    # Layer 1
    analysis = layer_1(text)

    st.subheader("🟦 Layer 1: Analysis")

    st.write("Numbers Found:", analysis["numbers"])
    st.write("Complexity Score:", analysis["complexity"])
    st.write("Receivables Detected:", analysis["receivables_detected"])

    # Layer 2
    warnings = layer_2(budget, analysis)

    st.subheader("🟨 Layer 2: Risk Engine")

    if warnings:
        for w in warnings:
            st.error(w)
    else:
        st.success("No major risks detected")

    # Layer 3
    df, receivables_df, forecast, recommendations = layer_3(budget, analysis)

    st.subheader("🟩 Layer 3: Financial Planning")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Budget Allocation")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown("### 💰 Forecast")
        st.metric("Projected Value", f"${forecast:,.0f}")

    # ================= RECEIVABLES =================
    st.subheader("🧾 Accounts Receivable")

    st.dataframe(receivables_df, use_container_width=True)

    # ================= RECOMMENDATIONS =================
    st.subheader("💡 Recommendations")

    for r in recommendations:
        st.info(r)
