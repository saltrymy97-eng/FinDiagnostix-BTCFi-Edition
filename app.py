import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# --- Professional Configuration ---
st.set_page_config(page_title="FinDiagnostix AI Auditor", layout="wide")

st.title("⚖️ FinDiagnostix: AI Professor & Auditor")
st.markdown(f"### Coordinator: **Salem Al-Tamimi** | Accounting Dept.")
st.write("---")

# --- 1. Session State ---
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []

# --- 2. The "Professor & Auditor" Engine ---
def academic_audit(filename, text_input=""):
    # Combine filename and text for analysis
    content = (filename + " " + text_input).lower()
    amount_str = "".join(filter(str.isdigit, content))
    amount = float(amount_str) if amount_str else 10000 # Default for demo
    
    # Audit Logic
    if any(word in content for word in ["diesel", "fuel", "purchase"]):
        return {
            "dr": "Purchases (Expenses)", "cr": "Cash Account", "amt": amount,
            "logic": "Expenses increased (Natural Debit) and Assets decreased (Natural Credit).",
            "verdict": "✅ Valid Operational Expense.", "risk": "Low"
        }
    elif any(word in content for word in ["sale", "revenue", "received"]):
        return {
            "dr": "Cash Account", "cr": "Sales Revenue", "amt": amount,
            "logic": "Assets increased (Natural Debit) and Revenue increased (Natural Credit).",
            "verdict": "✅ Revenue recognized per Accounting Standards.", "risk": "Low"
        }
    else:
        return {
            "dr": "Suspense Account", "cr": "Cash Account", "amt": amount,
            "logic": "Nature of debit is unclear. Placed in Suspense to balance the entry.",
            "verdict": "🔴 **FRAUD ALERT:** Vague documentation. Potential 'False Profit' or embezzlement.", "risk": "High"
        }

# --- 3. THE UPLOAD SECTION (HERE IT IS!) ---
st.sidebar.header("📤 Document Center")
# This is the button to upload images
uploaded_file = st.sidebar.file_uploader("Upload Invoice/Receipt Image", type=["jpg", "png", "jpeg"])

user_description = st.sidebar.text_input("Optional: Add Description")

if uploaded_file is not None:
    # Show the image
    img = Image.open(uploaded_file)
    st.sidebar.image(img, caption="Uploaded Document", use_container_width=True)
    
    if st.sidebar.button("Analyze & Audit"):
        result = academic_audit(uploaded_file.name, user_description)
        
        # Display Professor's Explanation
        st.subheader("👨‍🏫 Professor's Accounting Logic:")
        st.info(result['logic'])
        
        # Display Auditor's Verdict
        st.subheader("🔍 Auditor's Verdict:")
        if result['risk'] == "Low":
            st.success(result['verdict'])
        else:
            st.error(result['verdict'])
            
        # Display Official Journal Entry
        st.subheader("📑 Automated Journal Entry:")
        df_entry = pd.DataFrame({
            "Description": ["Debit (Dr.)", "Credit (Cr.)"],
            "Account": [result['dr'], result['cr']],
            "Amount (YR)": [f"{result['amt']:,}", f"{result['amt']:,}"]
        })
        st.table(df_entry)
        
        st.session_state.audit_log.append(result)

# --- 4. Historical Audit Trail ---
if st.session_state.audit_log:
    st.write("---")
    st.subheader("📋 Session Audit Trail")
    st.write(pd.DataFrame(st.session_state.audit_log)[['dr', 'cr', 'amt', 'risk']])
