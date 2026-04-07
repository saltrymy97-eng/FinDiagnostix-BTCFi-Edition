import streamlit as st
import sqlite3
import pandas as pd

# =========================
# DATABASE
# =========================
DB_NAME = "supermarket.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        quantity INTEGER,
        total REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# SESSION CART
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Supermarket POS", layout="wide")
st.title("🛒 Supermarket POS System")

conn = get_conn()
cur = conn.cursor()

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📦 Products", "🛒 Cashier", "📊 Reports"])

# =========================
# TAB 1 - PRODUCTS
# =========================
with tab1:
    st.header("Product Management")

    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, step=0.5)
    stock = st.number_input("Stock", min_value=0, step=1)

    if st.button("Add Product"):
        cur.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                    (name, price, stock))
        conn.commit()
        st.success("Product added!")

    st.subheader("All Products")
    products = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(products, use_container_width=True)

    # Delete product
    del_id = st.number_input("Delete Product ID", min_value=1, step=1)
    if st.button("Delete Product"):
        cur.execute("DELETE FROM products WHERE id=?", (del_id,))
        conn.commit()
        st.warning("Product deleted!")

# =========================
# TAB 2 - CASHIER
# =========================
with tab2:
    st.header("Cashier System")

    products = pd.read_sql("SELECT * FROM products", conn)
    product_list = products["name"].tolist() if not products.empty else []

    selected = st.selectbox("Select Product", product_list)
    qty = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Add to Cart"):
        cur.execute("SELECT price, stock FROM products WHERE name=?", (selected,))
        item = cur.fetchone()

        if item:
            price, stock = item

            if stock >= qty:
                st.session_state.cart.append({
                    "name": selected,
                    "price": price,
                    "qty": qty,
                    "total": price * qty
                })
                st.success("Added to cart!")
            else:
                st.error("Not enough stock")

    st.subheader("🧾 Cart")

    if st.session_state.cart:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, use_container_width=True)

        total = cart_df["total"].sum()
        st.metric("Total Amount", f"${total}")

        if st.button("Checkout"):
            for item in st.session_state.cart:
                cur.execute("UPDATE products SET stock = stock - ? WHERE name=?",
                            (item["qty"], item["name"]))

                cur.execute("INSERT INTO sales (product, quantity, total) VALUES (?, ?, ?)",
                            (item["name"], item["qty"], item["total"]))

            conn.commit()
            st.session_state.cart = []
            st.success("Payment Completed!")
    else:
        st.info("Cart is empty")

# =========================
# TAB 3 - REPORTS
# =========================
with tab3:
    st.header("Sales Reports")

    sales = pd.read_sql("SELECT * FROM sales", conn)
    st.dataframe(sales, use_container_width=True)

    total_sales = sales["total"].sum() if not sales.empty else 0
    st.metric("Total Revenue", f"${total_sales}")

    st.subheader("Top Products")
    if not sales.empty:
        top = sales.groupby("product")["quantity"].sum().reset_index()
        st.dataframe(top)

conn.close()
