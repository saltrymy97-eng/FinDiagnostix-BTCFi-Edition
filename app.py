import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# --- Page Configuration ---
st.set_page_config(page_title="FinDiagnostix AI - Image Scanner", page_icon="📸", layout="wide")

# --- Header Section ---
st.title("📸 FinDiagnostix AI: Smart Invoice Scanner")
st.markdown(f"### Coordinator: **Salem Al-Tamimi** | Accounting Dept. | Workshop Edition")
st.write("---")

# --- 1. Session State Initialization ---
if 'ledger' not in st.session_state:
    st.session_state.ledger = []

# --- 2. Logic to "Simulate" Image OCR ---
def process_invoice_image(uploaded_file):
    # In a real-world scenario, we use Tesseract or Google Vision API here.
    # For the workshop, we simulate the extraction to show the "AI flow".
    filename = uploaded_file.name.lower()
    
    if "diesel" in filename or "fuel" in filename:
        return {"dr": "Purchases (Fuel)", "cr": "Cash Account", "amt": 75000, "desc": "Extracted from Image: Diesel Purchase"}
    elif "sale" in filename or "inv" in filename:
        return {"dr": "Cash Account", "cr": "Sales Revenue", "amt": 120000, "desc": "Extracted from Image: Service Sale"}
    else:
        # Default fallback if image name doesn't match
        return {"dr": "Pending Classification", "cr": "Cash Account", "amt": 10000, "desc": "Manual Review Required"}

# --- 3. Sidebar: Image Upload Section ---
st.sidebar.header("📤 Upload Invoice/Receipt")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption='Uploaded Invoice', use_container_width=True)
    
    if st.sidebar.button("Scan & Process with AI"):
        with st.spinner('Analyzing Image Patterns...'):
            result = process_invoice_image(uploaded_file)
            
            entry = {
                "Date": datetime.now().strftime("%H:%M"),
                "Source": "📷 Image Scan",
                "Description": result['desc'],
                "Debit (DR)": result['dr'],
                "Credit (CR)": result['cr'],
                "Amount": float(result['amt']),
                "Status": "✅ OCR Verified"
            }
            st.session_state.ledger.append(entry)
            st.sidebar.success("Image Analyzed & Entry Generated!")

# --- 4. Audit Radar ---
st.header("🔍 Intelligent Audit Radar")
df = pd.DataFrame(st.session_state.ledger)

if not df.empty:
    if df['Amount'].max() > 100000:
        st.warning("⚠️ **High Risk Alert:** Large transaction detected via Image Scan.")
    
    # --- 5. Automated Ledger ---
    st.header("📑 Automated Digital Ledger")
    st.dataframe(df, use_container_width=True)

    # --- 6. Financial Metrics ---
    st.write("---")
    c1, c2, c3 = st.columns(3)
    total_exp = df[df['Debit (DR)'].str.contains("Purchases|Pending", na=False)]['Amount'].sum()
    total_rev = df[df['Debit (DR)'] == "Cash Account"]['Amount'].sum()
    
    c1.metric("Total Expenses", f"{total_exp:,.0f} YR")
    c2.metric("Total Revenue", f"{total_rev:,.0f} YR")
    c3.metric("Net Cash Position", f"{total_rev - total_exp:,.0f} YR")
else:
    st.info("Upload an image of an invoice in the sidebar to test the AI Scanner.")

st.sidebar.write("---")
st.sidebar.caption("FinDiagnostix AI v1.2 | Image Recognition Module")
        
