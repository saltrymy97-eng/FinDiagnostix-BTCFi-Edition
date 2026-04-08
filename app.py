import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# الإعدادات
# =========================
DB_NAME = "pos.db"
CURRENCY = "ريال يمني (﷼)"

st.set_page_config(
    page_title="نظام المبيعات اكسترا",
    layout="wide"
)

# =========================
# قاعدة البيانات
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
# السلة
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# العنوان
# =========================
st.title("🛒 نظام المبيعات اكسترا")
st.caption("نظام كاشير بسيط للمحلات الصغيرة")

menu = st.sidebar.selectbox("القائمة", ["لوحة التحكم", "المنتجات", "الكاشير", "التقارير"])

# =========================
# لوحة التحكم
# =========================
if menu == "لوحة التحكم":
    st.markdown("## 📊 لوحة التحكم")

    products = pd.read_sql("SELECT * FROM products", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_items = sales["qty"].sum() if not sales.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📦 عدد المنتجات", len(products))
    col2.metric("🧾 عدد العمليات", len(sales))
    col3.metric("💰 إجمالي الإيرادات", f"{total_sales} {CURRENCY}")
    col4.metric("🛒 القطع المباعة", total_items)

    st.divider()

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 📈 رسم المبيعات")
        if not sales.empty:
            fig, ax = plt.subplots()
            sales.groupby("product")["qty"].sum().plot(kind="bar", ax=ax)
            st.pyplot(fig)
        else:
            st.info("لا توجد بيانات")

    with colB:
        st.markdown("### 🧾 آخر العمليات")
        st.dataframe(sales.tail(10), use_container_width=True)

# =========================
# المنتجات
# =========================
elif menu == "المنتجات":
    st.markdown("## 📦 إدارة المنتجات")

    name = st.text_input("اسم المنتج")
    price = st.number_input("السعر", min_value=0.0)
    stock = st.number_input("المخزون", min_value=0)

    if st.button("إضافة منتج"):
        if name.strip():
            try:
                cur.execute("INSERT INTO products VALUES (NULL,?,?,?)",
                            (name, price, stock))
                conn.commit()
                st.success("تمت الإضافة ✔")
                st.rerun()
            except:
                st.error("المنتج موجود ❌")

    st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)

# =========================
# الكاشير
# =========================
elif menu == "الكاشير":
    st.markdown("## 🛒 الكاشير")

    products = pd.read_sql("SELECT * FROM products", conn)

    search = st.text_input("بحث عن منتج")
    filtered = products[products["name"].str.contains(search, case=False)] if search else products

    if not filtered.empty:
        product = st.selectbox("اختر المنتج", filtered["name"])
        qty = st.number_input("الكمية", min_value=1)

        if st.button("إضافة للسلة"):
            row = products[products["name"] == product].iloc[0]

            if row["stock"] >= qty:
                st.session_state.cart.append({
                    "name": product,
                    "price": row["price"],
                    "qty": qty,
                    "total": row["price"] * qty
                })
                st.success("تمت الإضافة ✔")
            else:
                st.error("المخزون غير كافي")

    st.markdown("### 🧾 السلة")

    if st.session_state.cart:
        df = pd.DataFrame(st.session_state.cart)
        st.dataframe(df)

        total = df["total"].sum()
        st.metric("الإجمالي", f"{total} {CURRENCY}")

        if st.button("إتمام البيع"):
            for item in st.session_state.cart:
                cur.execute("UPDATE products SET stock = stock - ? WHERE name=?",
                            (item["qty"], item["name"]))

                cur.execute("INSERT INTO sales VALUES (NULL,?,?,?)",
                            (item["name"], item["qty"], item["total"]))

            conn.commit()
            st.session_state.cart = []
            st.success("تم البيع بنجاح ✔")
            st.rerun()

    else:
        st.info("السلة فارغة")

# =========================
# التقارير
# =========================
elif menu == "التقارير":
    st.markdown("## 📊 التقارير")

    sales = pd.read_sql("SELECT * FROM sales", conn)

    st.dataframe(sales)

    total = sales["total"].sum() if not sales.empty else 0
    st.metric("إجمالي الإيرادات", f"{total} {CURRENCY}")

conn.close()
