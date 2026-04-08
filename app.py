import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# SETTINGS
# =========================
DB_NAME = "pos.db"
CURRENCY = "YER (﷼)"

st.set_page_config(
    page_title="Extra Sales System",
    layout="wide"
)

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
# CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# HEADER
# =========================
st.title("🛒 EXTRA SALES SYSTEM")
st.caption("Simple POS for Small Shops")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Products", "Cashier", "Reports"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.markdown("## 📊 Dashboard Overview")

    products = pd.read_sql("SELECT * FROM products", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_items = sales["qty"].sum() if not sales.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Products", len(products))
    col2.metric("Sales Transactions", len(sales))
    col3.metric("Total Revenue", f"{total_sales} {CURRENCY}")
    col4.metric("Items Sold", total_items)

    st.divider()

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 📈 Sales Chart")

        if not sales.empty:
            fig, ax = plt.subplots()
            sales.groupby("product")["qty"].sum().plot(kind="bar", ax=ax)
            st.pyplot(fig)
        else:
            st.info("No sales data available")

    with colB:
        st.markdown("### 🧾 Recent Transactions")
        st.dataframe(sales.tail(10), use_container_width=True)

# =========================
# PRODUCTS
# =========================
elif menu == "Products":
    st.markdown("## 📦 Product Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Product Name")

    with col2:
        price = st.number_input("Price", min_value=0.0)

    with col3:
        stock = st.number_input("Stock", min_value=0)

    if st.button("Add Product"):
        if name.strip():
            try:
                cur.execute("INSERT INTO products VALUES (NULL,?,?,?)",
                            (name, price, stock))
                conn.commit()
                st.success("Product added ✔")
                st.rerun()
            except:
                st.error("Product already exists ❌")

    st.markdown("### 📋 Product List")
    st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)

# =========================
# CASHIER
# =========================
elif menu == "Cashier":
    st.markdown("## 🛒 Cashier Screen")

    products = pd.read_sql("SELECT * FROM products", conn)

    search = st.text_input("Search Product")
    filtered = products[products["name"].str.contains(search, case=False)] if search else products

    if not filtered.empty:
        selected = st.selectbox("Select Product", filtered["name"])
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
                st.success("Added to cart ✔")
            else:
                st.error("Not enough stock ❌")

    st.markdown("### 🧾 Cart")

    if st.session_state.cart:
        df = pd.DataFrame(st.session_state.cart)
        st.dataframe(df, use_container_width=True)

        subtotal = df["total"].sum()
        discount = st.slider("Discount (%)", 0, 100, 0)
        total = subtotal - (subtotal * discount / 100)

        st.metric("Final Total", f"{total} {CURRENCY}")

        if st.button("Checkout 💰"):
            for item in st.session_state.cart:
                cur.execute("UPDATE products SET stock = stock - ? WHERE name=?",
                            (item["qty"], item["name"]))

                cur.execute("INSERT INTO sales VALUES (NULL,?,?,?)",
                            (item["name"], item["qty"], item["total"]))

            conn.commit()
            st.session_state.cart = []
            st.success("Payment completed ✔")
            st.balloons()
            st.rerun()

    else:
        st.info("Cart is empty")

# =========================
# REPORTS
# =========================
elif menu == "Reports":
    st.markdown("## 📊 Reports")

    sales = pd.read_sql("SELECT * FROM sales", conn)

    st.dataframe(sales, use_container_width=True)

    total = sales["total"].sum() if not sales.empty else 0
    st.metric("Total Revenue", f"{total} {CURRENCY}")

    if not sales.empty:
        st.markdown("### 📈 Sales Analysis")

        fig, ax = plt.subplots()
        sales.groupby("product")["qty"].sum().plot(kind="bar", ax=ax)
        st.pyplot(fig)

conn.close()
