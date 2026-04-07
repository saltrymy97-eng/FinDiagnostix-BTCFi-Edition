import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas

# =========================
# SETTINGS
# =========================
DB_NAME = "pos.db"
CURRENCY = "YER (﷼)"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Extra Sales System",
    layout="wide",
    page_icon="🛒"
)

# =========================
# CUSTOM CSS (Enterprise UI)
# =========================
st.markdown("""
<style>
.main {
    background-color: #0f172a;
    color: white;
}

h1, h2, h3 {
    color: #38bdf8;
}

.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: bold;
}

.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🛒 EXTRA SALES SYSTEM")
st.subheader("نظام المبيعات اكسترا - Professional POS Dashboard")

# =========================
# DB
# =========================
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        price REAL,
        stock INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        qty INTEGER,
        total REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

conn = get_conn()
cur = conn.cursor()

# =========================
# SESSION CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# SIDEBAR MENU
# =========================
menu = st.sidebar.selectbox(
    "📌 Navigation",
    ["Dashboard", "Products", "Cashier", "Reports"]
)

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.header("📊 Dashboard Overview")

    products = pd.read_sql("SELECT * FROM products", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_products = len(products)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Products", total_products)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Sales", f"{total_sales} {CURRENCY}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Transactions", len(sales))
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PRODUCTS
# =========================
elif menu == "Products":
    st.header("📦 Product Management")

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Add Product"):
        try:
            cur.execute("INSERT INTO products VALUES (NULL,?,?,?)",
                        (name, price, stock))
            conn.commit()
            st.success("Product added ✔")
        except:
            st.error("Product already exists ❌")

    products = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(products, use_container_width=True)

# =========================
# CASHIER
# =========================
elif menu == "Cashier":
    st.header("🛒 Cashier System")

    products = pd.read_sql("SELECT * FROM products", conn)

    if not products.empty:
        selected = st.selectbox("Select Product", products["name"])
        qty = st.number_input("Quantity", min_value=1)

        if st.button("Add to Cart"):
            row = products[products["name"] == selected].iloc[0]

            if row["stock"] >= qty:
                st.session_state.cart.append({
                    "name": selected,
                    "price": row["price"],
                    "qty": qty,
                    "total": row["price"] * qty
                })
                st.success("Added ✔")
            else:
                st.error("Not enough stock")

    st.subheader("🧾 Cart")

    if st.session_state.cart:
        df = pd.DataFrame(st.session_state.cart)
        st.dataframe(df, use_container_width=True)

        total = df["total"].sum()
        st.metric("Total", f"{total} {CURRENCY}")

        if st.button("Checkout 💰"):
            for item in st.session_state.cart:
                cur.execute(
                    "UPDATE products SET stock = stock - ? WHERE name=?",
                    (item["qty"], item["name"])
                )

                cur.execute(
                    "INSERT INTO sales VALUES (NULL,?,?,?)",
                    (item["name"], item["qty"], item["total"])
                )

            conn.commit()
            st.session_state.cart = []
            st.success("Payment Completed ✔")

    else:
        st.info("Cart is empty")

# =========================
# REPORTS
# =========================
elif menu == "Reports":
    st.header("📊 Sales Reports")

    sales = pd.read_sql("SELECT * FROM sales", conn)

    st.dataframe(sales, use_container_width=True)

    total_sales = sales["total"].sum() if not sales.empty else 0
    st.metric("Revenue", f"{total_sales} {CURRENCY}")

    if not sales.empty:
        chart = sales.groupby("product")["qty"].sum()

        fig, ax = plt.subplots()
        chart.plot(kind="bar", ax=ax)
        st.pyplot(fig)

conn.close()
