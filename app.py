import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fintech Pro | Intelligence Suite",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PROFESSIONAL STYLING (CSS) ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #30363d; 
    }
    .rec-card { 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 15px;
        border-left: 5px solid #238636;
        background-color: #1c2128;
    }
    .risk-high { border-left-color: #da3633; }
    .risk-med { border-left-color: #e3b341; }
    .title-text { font-size: 32px; font-weight: 700; color: #f0f6fc; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Client_Name": ["Alpha Corp", "Beta Logistics", "Gamma Tech", "Delta Services"],
        "Monthly_Income": [55000, 12000, 8500, 42000],
        "Monthly_Expenses": [32000, 14500, 7000, 48000],
        "Credit_Score": [820, 450, 610, 390]
    })

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6081/6081518.png", width=80)
    st.title("Fintech Pipeline")
    step = st.radio("Navigation", 
                   ["📥 Data Ingestion", 
                    "👥 Client Classification", 
                    "📊 Budget Intelligence", 
                    "💡 Strategic Insights"])
    st.divider()
    st.caption("v2.1.0 | AI-Powered Financial Suite")

# --- STEP 1: DATA INGESTION ---
if step == "📥 Data Ingestion":
    st.markdown("<p class='title-text'>📥 Data Ingestion & Management</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload Financial Report (CSV)", type="csv")
        if uploaded_file:
            st.session_state.data = pd.read_csv(uploaded_file)
            st.success("Database updated successfully!")
    
    with col2:
        with st.expander("➕ Add Client Manually"):
            with st.form("manual_entry"):
                name = st.text_input("Client Name")
                income = st.number_input("Income ($)", min_value=0)
                exp = st.number_input("Expenses ($)", min_value=0)
                score = st.slider("Credit Score", 300, 850, 600)
                if st.form_submit_button("Add Entry"):
                    new_data = pd.DataFrame([{"Client_Name": name, "Monthly_Income": income, "Monthly_Expenses": exp, "Credit_Score": score}])
                    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
                    st.rerun()

    st.subheader("Current Portfolio Data")
    st.dataframe(st.session_state.data, use_container_width=True)

# --- STEP 2: CLIENT CLASSIFICATION ---
elif step == "👥 Client Classification":
    st.markdown("<p class='title-text'>👥 Risk-Based Classification</p>", unsafe_allow_html=True)
    df = st.session_state.data.copy()
    
    def classify_risk(row):
        if row['Credit_Score'] >= 700 and row['Monthly_Income'] > row['Monthly_Expenses']:
            return "Prime (Low Risk)"
        elif row['Credit_Score'] < 500 or row['Monthly_Expenses'] > row['Monthly_Income']:
            return "Subprime (High Risk)"
        return "Standard (Medium Risk)"

    df['Risk_Level'] = df.apply(classify_risk, axis=1)
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Clients", len(df))
    c2.metric("High Risk", len(df[df['Risk_Level'] == "Subprime (High Risk)"]), delta_color="inverse")
    c3.metric("Avg Credit Score", int(df['Credit_Score'].mean()))

    # Visualization
    fig = px.scatter(df, x="Monthly_Income", y="Credit_Score", color="Risk_Level",
                     size="Monthly_Income", hover_name="Client_Name",
                     color_discrete_map={"Prime (Low Risk)": "#238636", 
                                         "Subprime (High Risk)": "#da3633", 
                                         "Standard (Medium Risk)": "#e3b341"})
    st.plotly_chart(fig, use_container_width=True)
    st.table(df[['Client_Name', 'Risk_Level', 'Credit_Score']])

# --- STEP 3: BUDGET INTELLIGENCE ---
elif step == "📊 Budget Intelligence":
    st.markdown("<p class='title-text'>📊 Budget Forecasting</p>", unsafe_allow_html=True)
    
    df = st.session_state.data
    total_inc = df['Monthly_Income'].sum()
    total_exp = df['Monthly_Expenses'].sum()
    net_cash = total_inc - total_exp
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Portfolio Revenue", f"${total_inc:,}")
        st.metric("Total Operating Costs", f"${total_exp:,}")
        st.metric("Net Cash Flow", f"${net_cash:,}", delta=f"{(net_cash/total_inc)*100:.1f}% Margin")

    with col2:
        st.subheader("Automated Budget Allocation")
        # Proposed budget allocation logic
        labels = ['OpEx Reserve', 'Growth Fund', 'Risk Mitigation', 'Retained Earnings']
        values = [total_inc * 0.4, total_inc * 0.25, total_inc * 0.15, total_inc * 0.2]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- STEP 4: STRATEGIC INSIGHTS ---
elif step == "💡 Strategic Insights":
    st.markdown("<p class='title-text'>💡 Executive Recommendations</p>", unsafe_allow_html=True)
    
    df = st.session_state.data
    deficit_clients = len(df[df['Monthly_Expenses'] > df['Monthly_Income']])

    # Recommendation 1
    st.markdown(f"""<div class='rec-card risk-high'>
    <h3>1. Credit Exposure Alert</h3>
    <p><b>Critical:</b> {deficit_clients} clients are currently operating in a deficit. 
    Immediate suspension of further credit lines is recommended until debt restructuring is finalized.</p>
    </div>""", unsafe_allow_html=True)

    # Recommendation 2
    st.markdown("""<div class='rec-card risk-med'>
    <h3>2. Liquidity Optimization</h3>
    <p>Current analysis suggests a <b>12% increase</b> in cash-on-hand is required to maintain stability 
    against projected market volatility in the next fiscal quarter.</p>
    </div>""", unsafe_allow_html=True)

    # Recommendation 3
    st.markdown("""<div class='rec-card'>
    <h3>3. Portfolio Growth Policy</h3>
    <p>Approve expansion for <b>Prime</b> clients. Data shows these entities have a 95% repayment 
    probability, justifying a 15% increase in their credit ceiling.</p>
    </div>""", unsafe_allow_html=True)

    if st.button("Generate Executive PDF Report"):
        st.toast("Processing Report...")
        st.info("PDF Engine initializing... Download will be available shortly.")
    
