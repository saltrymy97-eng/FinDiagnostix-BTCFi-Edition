import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# الإعدادات
# =========================
DB_NAME = "pos.db"
CURRENCY = "ريال يمني (﷼)"
LOW_STOCK_THRESHOLD = 5  # حد المخزون المنخفض

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
# دوال التحسينات الذكية
# =========================
def get_low_stock_products():
    """جلب المنتجات التي وصل مخزونها للحد الأدنى"""
    query = f"""
    SELECT name, stock FROM products
    WHERE stock <= {LOW_STOCK_THRESHOLD}
    ORDER BY stock ASC
    """
    df = pd.read_sql(query, conn)
    return df

def get_top_selling_products(limit=5):
    """جلب أكثر المنتجات مبيعاً"""
    query = f"""
    SELECT product, SUM(qty) as total_qty
    FROM sales
    GROUP BY product
    ORDER BY total_qty DESC
    LIMIT {limit}
    """
    df = pd.read_sql(query, conn)
    return df

def generate_sales_insight():
    """توليد جملة تحليلية ذكية عن المبيعات"""
    sales_df = pd.read_sql("SELECT * FROM sales", conn)
    products_df = pd.read_sql("SELECT * FROM products", conn)

    if sales_df.empty:
        return "لا توجد مبيعات مسجلة بعد لتحليلها."

    total_revenue = sales_df["total"].sum()
    total_quantity = sales_df["qty"].sum()

    # المنتج الأكثر مبيعاً
    top_product = sales_df.groupby("product")["qty"].sum().idxmax()
    top_qty = sales_df.groupby("product")["qty"].sum().max()
    top_percentage = (top_qty / total_quantity) * 100

    insight = (
        f"📊 **تحليل ذكي للمبيعات:**\n\n"
        f"إجمالي الإيرادات: **{total_revenue:,.2f}** {CURRENCY}.\n"
        f"إجمالي القطع المباعة: **{int(total_quantity)}** قطعة.\n"
        f"أفضل منتج لديك هو **{top_product}**، حيث تم بيع **{int(top_qty)}** قطعة، "
        f"ويمثل **{top_percentage:.1f}%** من إجمالي مبيعاتك.\n\n"
        f"💡 **نصيحة:** ركز على ترويج هذا المنتج وحافظ على مخزونه لتلبية الطلب."
    )
    return insight

# =========================
# العنوان
# =========================
st.title("🛒 نظام المبيعات اكسترا")
st.caption("نظام كاشير بسيط مع تحسينات ذكية")

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

    # ===== تنبيهات المخزون الذكية =====
    low_stock = get_low_stock_products()
    if not low_stock.empty:
        st.warning("⚠️ **تنبيه مخزون منخفض:** المنتجات التالية وصلت لحد إعادة الطلب:")
        for _, row in low_stock.iterrows():
            st.write(f"- {row['name']}: {row['stock']} قطعة فقط متبقية")
    else:
        st.success("✅ جميع المنتجات بمخزون جيد (أعلى من {LOW_STOCK_THRESHOLD}).")

    st.divider()

    # ===== التحليل الذكي للمبيعات =====
    st.markdown(generate_sales_insight())

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

    # ===== اقتراحات المنتجات الذكية =====
    top_products = get_top_selling_products()
    if not top_products.empty:
        st.markdown("### 🔥 المنتجات الأكثر مبيعاً (اقتراحات سريعة)")
        cols = st.columns(len(top_products))
        for idx, (_, row) in enumerate(top_products.iterrows()):
            with cols[idx]:
                if st.button(f"{row['product']}\n({int(row['total_qty'])})", key=f"top_{idx}"):
                    st.session_state.cart.append({
                        "name": row['product'],
                        "price": products[products["name"]==row['product']]["price"].values[0],
                        "qty": 1,
                        "total": products[products["name"]==row['product']]["price"].values[0]
                    })
                    st.success(f"تمت إضافة {row['product']} ✔")
        st.divider()

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
