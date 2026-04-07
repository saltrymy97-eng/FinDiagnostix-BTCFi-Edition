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
# DATABASE
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

# =========================
# APP SETTINGS
# =========================
st.set_page_config(page_title="Supermarket POS", layout="wide")
st.title("🛒 Supermarket POS System - Yemen")

conn = get_conn()
cur = conn.cursor()

# =========================
# SESSION CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# PDF INVOICE
# =========================
def generate_invoice(cart, total):
    file_name = "invoice.pdf"
    c = canvas.Canvas(file_name)

    c.drawString(200, 800, "SUPERMARKET INVOICE")

    y = 750
    for item in cart:
        line = f"{item['name']} | {item['qty']} x {item['price']} = {item['total']}"
        c.drawString(50, y, line)
        y -= 20

    c.drawString(50, y - 20, f"TOTAL: {total} {CURRENCY}")
    c.save()

    return file_name

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📦 Products", "🛒 Cashier", "📊 Reports"])

# =========================
# PRODUCTS TAB
# =========================
with tab1:
    st.header("Product Management")

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Add Product"):
        try:
            cur.execute("INSERT INTO products VALUES (NULL,?,?,?)",
                        (name, price, stock))
            conn.commit()
            st.success("Product added successfully ✔")
        except:
            st.error("Product already exists ❌")

    st.subheader("All Products")
    products = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(products, use_container_width=True)

# =========================
# CASHIER TAB
# =========================
with tab2:
    st.header("Cashier System")

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
                st.success("Added to cart ✔")
            else:
                st.error("Not enough stock ❌")

    st.subheader("🧾 Cart")

    if st.session_state.cart:
        df = pd.DataFrame(st.session_state.cart)
        st.dataframe(df, use_container_width=True)

        total = df["total"].sum()
        st.metric("Total", f"{total} {CURRENCY}")

        col1, col2 = st.columns(2)

        # Checkout
        with col1:
            if st.button("💰 Checkout"):
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

                pdf = generate_invoice(st.session_state.cart, total)
                st.session_state.cart = []

                with open(pdf, "rb") as f:
                    st.download_button("Download Invoice PDF", f, file_name="invoice.pdf")

                st.success("Payment completed ✔")

        # Clear cart
        with col2:
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.warning("Cart cleared")

    else:
        st.info("Cart is empty")

# =========================
# REPORTS TAB
# =========================
with tab3:
    st.header("Sales Reports")

    sales = pd.read_sql("SELECT * FROM sales", conn)
    st.dataframe(sales, use_container_width=True)

    total_sales = sales["total"].sum() if not sales.empty else 0
    st.metric("Total Revenue", f"{total_sales} {CURRENCY}")

    if not sales.empty:
        chart = sales.groupby("product")["qty"].sum()

        fig, ax = plt.subplots()
        chart.plot(kind="bar", ax=ax)
        st.pyplot(fig)

conn.close()
