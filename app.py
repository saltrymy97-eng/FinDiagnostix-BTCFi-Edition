import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# الإعدادات العامة
# =========================
DB_NAME = "pos.db"
CURRENCY = "ريال يمني (﷼)"
LOW_STOCK_THRESHOLD = 5

st.set_page_config(
    page_title="المسرحية المحاسبية | المبيعات X",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# تنسيقات CSS احترافية وجذابة
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .main {
        background-color: #f4f7f9;
    }

    h1 {
        color: #4a1d8c;
        font-weight: 700;
        border-right: 6px solid #20c997;
        padding-right: 15px;
    }

    h2, h3 {
        color: #2d4059;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6f42c1 0%, #8b5cf6 100%);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(111, 66, 193, 0.2);
        width: 100%;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #5a2b9c 0%, #7c3aed 100%);
        box-shadow: 0 8px 15px rgba(111, 66, 193, 0.3);
        transform: translateY(-2px);
    }

    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 20px 10px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(111, 66, 193, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }

    .metric-card:hover {
        transform: scale(1.02);
        border-color: #20c997;
    }

    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.03);
    }

    .stAlert {
        border-radius: 15px;
        border-left-width: 8px;
        font-weight: 500;
    }

    div[data-baseweb="notification"] {
        background-color: #fff8e5;
        border-left-color: #20c997;
    }

    .css-1d391kg {
        background: linear-gradient(180deg, #1e1a2e 0%, #2d1b4e 100%);
        color: white;
    }

    .css-1d391kg .stMarkdown, .css-1d391kg .stSelectbox label {
        color: rgba(255,255,255,0.9);
    }

    .css-1d391kg .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        border-radius: 30px;
    }

    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        background: white;
        border-radius: 60px 60px 20px 20px;
        color: #4a5568;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

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
    query = f"""
    SELECT name, stock FROM products
    WHERE stock <= {LOW_STOCK_THRESHOLD}
    ORDER BY stock ASC
    """
    df = pd.read_sql(query, conn)
    return df

def get_top_selling_products(limit=5):
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
    sales_df = pd.read_sql("SELECT * FROM sales", conn)
    if sales_df.empty:
        return "🎭 لا توجد مبيعات مسجلة بعد. ابدأ ببيع منتج لتظهر التحليلات الذكية!"

    total_revenue = sales_df["total"].sum()
    total_quantity = sales_df["qty"].sum()
    top_product = sales_df.groupby("product")["qty"].sum().idxmax()
    top_qty = sales_df.groupby("product")["qty"].sum().max()
    top_percentage = (top_qty / total_quantity) * 100

    insight = f"""
    <div style='background-color: #e8f0fe; padding: 16px; border-radius: 12px; border-right: 6px solid #6f42c1;'>
        <h3 style='color: #4a1d8c; margin-top: 0;'>📊 تحليل الأداء المالي</h3>
        <p style='font-size: 16px;'>
            💰 إجمالي الإيرادات: <strong>{total_revenue:,.2f} {CURRENCY}</strong><br>
            🛒 إجمالي القطع المباعة: <strong>{int(total_quantity)}</strong> قطعة<br>
            🏆 المنتج الأكثر مبيعاً: <strong>{top_product}</strong> ({int(top_qty)} قطعة، {top_percentage:.1f}% من المبيعات)
        </p>
        <p style='font-size: 14px; color: #20c997; margin-bottom: 0;'>
            💡 نصيحة استراتيجية: حافظ على مخزون <strong>{top_product}</strong> وضعه في واجهة المتجر.
        </p>
    </div>
    """
    return insight

# =========================
# الشريط الجانبي (مرتب)
# =========================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/theater-mask.png", width=80)
    st.markdown("## 🎭 المسرحية المحاسبية")
    st.markdown("### نظام المبيعات X")
    st.markdown("---")
    st.markdown("**🎓 جامعة القرآن الكريم**")
    st.markdown("**📍 غيل باوزير - حضرموت**")
    st.markdown("---")
    menu = st.selectbox("📋 القائمة الرئيسية", ["🏠 لوحة التحكم", "📦 إدارة المنتجات", "🛒 الكاشير", "📊 التقارير"])
    st.markdown("---")
    st.markdown("**👨‍💻 بواسطة: سالم التريمي**")
    st.markdown("*طالب محاسبة - مبتكر*")
    st.markdown("---")
    st.markdown("🎯 *تحويل المحاسبة إلى تجربة حية*")

# =========================
# العنوان الرئيسي
# =========================
st.title("🎭 المسرحية المحاسبية | نظام المبيعات X")
st.caption("نظام ذكي لمحاكاة عمليات البيع والشراء - مصمم خصيصًا للورشة التفاعلية")

# =========================
# لوحة التحكم
# =========================
if menu == "🏠 لوحة التحكم":
    st.markdown("## 📊 لوحة القيادة")

    products = pd.read_sql("SELECT * FROM products", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    total_sales = sales["total"].sum() if not sales.empty else 0
    total_items = sales["qty"].sum() if not sales.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>📦</h3><h2>{len(products)}</h2><p>المنتجات</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>🧾</h3><h2>{len(sales)}</h2><p>العمليات</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h3>💰</h3><h2>{total_sales:,.0f}</h2><p>الإيرادات ({CURRENCY})</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h3>🛒</h3><h2>{total_items}</h2><p>القطع المباعة</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    # تنبيهات المخزون
    low_stock = get_low_stock_products()
    if not low_stock.empty:
        warning_msg = "⚠️ **تنبيه مخزون:** " + " | ".join([f"{row['name']} ({row['stock']} قطعة)" for _, row in low_stock.iterrows()])
        st.warning(warning_msg)
    else:
        st.success(f"✅ جميع المنتجات بمخزون آمن (أعلى من {LOW_STOCK_THRESHOLD})")

    st.markdown("---")

    # التحليل الذكي
    st.markdown(generate_sales_insight(), unsafe_allow_html=True)

    st.markdown("---")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("### 📈 توزيع المبيعات")
        if not sales.empty:
            fig, ax = plt.subplots(figsize=(8, 4))
            sales.groupby("product")["qty"].sum().plot(kind="bar", ax=ax, color="#6f42c1")
            ax.set_facecolor("#f8f9fa")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("لا توجد بيانات كافية للرسم")
    with colB:
        st.markdown("### 🧾 آخر 10 عمليات بيع")
        st.dataframe(sales.tail(10), use_container_width=True)

# =========================
# المنتجات
# =========================
elif menu == "📦 إدارة المنتجات":
    st.markdown("## 📦 إدارة المنتجات")

    col1, col2 = st.columns([2, 1])
    with col1:
        name = st.text_input("📌 اسم المنتج")
        price = st.number_input("💵 السعر", min_value=0.0, step=100.0)
        stock = st.number_input("📊 المخزون الأولي", min_value=0, step=1)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ إضافة المنتج", use_container_width=True):
            if name.strip():
                try:
                    cur.execute("INSERT INTO products VALUES (NULL,?,?,?)", (name, price, stock))
                    conn.commit()
                    st.success(f"✅ تمت إضافة {name} بنجاح")
                    st.rerun()
                except:
                    st.error("❌ المنتج موجود مسبقاً")

    st.markdown("---")
    st.dataframe(pd.read_sql("SELECT * FROM products", conn), use_container_width=True)

# =========================
# الكاشير
# =========================
elif menu == "🛒 الكاشير":
    st.markdown("## 🛒 واجهة البيع")

    products = pd.read_sql("SELECT * FROM products", conn)

    # اقتراحات ذكية
    top_products = get_top_selling_products()
    if not top_products.empty:
        st.markdown("### 🔥 الأكثر مبيعاً (إضافة سريعة)")
        cols = st.columns(len(top_products))
        for idx, (_, row) in enumerate(top_products.iterrows()):
            with cols[idx]:
                if st.button(f"➕ {row['product']}\n({int(row['total_qty'])})", key=f"top_{idx}", use_container_width=True):
                    prod_row = products[products["name"] == row["product"]].iloc[0]
                    st.session_state.cart.append({
                        "name": row["product"],
                        "price": prod_row["price"],
                        "qty": 1,
                        "total": prod_row["price"]
                    })
                    st.success(f"✅ تمت إضافة {row['product']}")
        st.markdown("---")

    col1, col2 = st.columns([3, 2])
    with col1:
        search = st.text_input("🔍 ابحث عن منتج")
        filtered = products[products["name"].str.contains(search, case=False)] if search else products
        if not filtered.empty:
            product = st.selectbox("📌 اختر المنتج", filtered["name"])
            qty = st.number_input("🔢 الكمية", min_value=1, step=1)
            if st.button("🛒 إضافة إلى السلة", use_container_width=True):
                row = products[products["name"] == product].iloc[0]
                if row["stock"] >= qty:
                    st.session_state.cart.append({
                        "name": product,
                        "price": row["price"],
                        "qty": qty,
                        "total": row["price"] * qty
                    })
                    st.success(f"✅ تمت إضافة {qty} × {product}")
                else:
                    st.error(f"❌ المخزون غير كافٍ (متوفر: {row['stock']})")

    with col2:
        st.markdown("### 🧾 سلة المشتريات")
        if st.session_state.cart:
            df = pd.DataFrame(st.session_state.cart)
            st.dataframe(df, use_container_width=True)
            total = df["total"].sum()
            st.metric("💰 الإجمالي", f"{total:,.2f} {CURRENCY}")
            if st.button("✅ إتمام عملية البيع", use_container_width=True):
                for item in st.session_state.cart:
                    cur.execute("UPDATE products SET stock = stock - ? WHERE name=?", (item["qty"], item["name"]))
                    cur.execute("INSERT INTO sales VALUES (NULL,?,?,?)", (item["name"], item["qty"], item["total"]))
                conn.commit()
                st.session_state.cart = []
                st.success("🎉 تمت عملية البيع بنجاح!")
                st.rerun()
        else:
            st.info("السلة فارغة حالياً")

# =========================
# التقارير
# =========================
elif menu == "📊 التقارير":
    st.markdown("## 📊 تقارير المبيعات")
    sales = pd.read_sql("SELECT * FROM sales", conn)
    st.dataframe(sales, use_container_width=True)
    total = sales["total"].sum() if not sales.empty else 0
    st.metric("💰 إجمالي الإيرادات", f"{total:,.2f} {CURRENCY}")

# =========================
# تذييل الصفحة (مرتب)
# =========================
st.markdown("---")
st.markdown("<div class='footer'>🎭 نظام المبيعات X | المسرحية المحاسبية - غيل باوزير © 2026<br>👨‍💻 تصميم وتطوير: سالم التريمي</div>", unsafe_allow_html=True)

conn.close()
