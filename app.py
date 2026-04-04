import streamlit as st
import pandas as pd
from datetime import datetime

# --- Professional Page Config ---
st.set_page_config(page_title="FinDiagnostix - Academic Auditor", page_icon="⚖️", layout="wide")

# --- Header Section ---
st.title("⚖️ FinDiagnostix: The AI Professor & Senior Auditor")
st.markdown(f"### Developed by: **Salem Al-Tamimi** | Accounting Dept. | Workshop 2026")
st.write("---")

# --- Session State ---
if 'ledger' not in st.session_state:
    st.session_state.ledger = []

# --- 🧠 The Academic & Audit Engine ---
def academic_audit_engine(input_text):
    text = input_text.lower()
    amount_str = "".join(filter(str.isdigit, text))
    amount = float(amount_str) if amount_str else 0
    
    # Logic 1: Purchases (Expenses)
    if any(word in text for word in ["buy", "purchase", "diesel", "fuel"]):
        return {
            "dr": "Purchases (Diesel/Expenses)",
            "cr": "Cash Account",
            "amt": amount,
            "professor_logic": "Since the entity purchased fuel, Expenses increased (Natural Debit) and Assets/Cash decreased (Natural Debit becomes Credit when decreasing).",
            "audit_verdict": "✅ Valid Entry. Matches standard operational patterns.",
            "risk": "Low"
        }
    
    # Logic 2: Sales (Revenue)
    elif any(word in text for word in ["sell", "sales", "revenue", "received"]):
        # Special Audit Check for 'False Profit'
        audit_note = "✅ Revenue recognized according to IFRS/GAAP."
        risk_level = "Low"
        if amount > 500000: # Example Threshold
            audit_note = "⚠️ **AUDIT ALERT:** Unusually high revenue entry. Potential 'False Profit' to inflate financial position. Verify against physical delivery records."
            risk_level = "High"

        return {
            "dr": "Cash Account",
            "cr": "Sales Revenue",
            "amt": amount,
            "professor_logic": "Revenue increases (Natural Credit) and Cash increases (Natural Debit). Both sides of the equation are balanced.",
            "audit_verdict": audit_note,
            "risk": risk_level
        }
    
    # Logic 3: Unknown / Suspicious Entry
    else:
        return {
            "dr": "Suspense Account (Pending)",
            "cr": "Cash Account",
            "amt": amount,
            "professor_logic": "The system cannot determine the debit nature. Placing in Suspense Account to keep the trial balance intact.",
            "audit_verdict": "🔴 **FRAUD WARNING:** Transaction description is vague. High risk of 'Window Dressing' or embezzlement.",
            "risk": "Critical"
        }

# --- Sidebar Input ---
st.sidebar.header("📥 Transaction Input")
st.sidebar.info("Describe the event (e.g., 'Sold water for 80000')")
user_input = st.sidebar.text_area("Entry Description:")

if st.sidebar.button("Run AI Audit"):
    if user_input:
        analysis = academic_audit_engine(user_input)
        
        # 1. The Professor's Explanation
        st.subheader("👨‍🏫 The Professor's Explanation:")
        st.info(analysis['professor_logic'])
        
        # 2. The Auditor's Verdict
        st.subheader("🔍 Auditor's Verification:")
        if analysis['risk'] == "Low":
            st.success(analysis['audit_verdict'])
        elif analysis['risk'] == "High":
            st.warning(analysis['audit_verdict'])
        else:
            st.error(analysis['audit_verdict'])

        # 3. The Official Double-Entry Journal
        st.subheader("📑 Automated Journal Entry:")
        journal_data = {
            "Account Title": [analysis['dr'], analysis['cr']],
            "Debit (DR)": [f"{analysis['amt']:,}", ""],
            "Credit (CR)": ["", f"{analysis['amt']:,}"]
        }
        st.table(pd.DataFrame(journal_data))
        
        # Save to session history
        st.session_state.ledger.append(analysis)
    else:
        st.sidebar.error("Please enter transaction details.")

st.write("---")
st.caption("FinDiagnostix AI v2.0 - Bridging Academia and Industry.")
            
