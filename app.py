import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import ollama
import io
import zipfile

# ==================== الإعدادات الأساسية ====================
DB_NAME = "pos.db"
CURRENCY = "ريال يمني (﷼)"
LOW_STOCK_THRESHOLD = 5

st.set_page_config(
    page_title="المسرحية المحاسبية | المبيعات X",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== التنسيقات CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    .main { background-color: #f4f7f9; }
    h1 { color: #4a1d8c; font-weight: 700; border-right: 6px solid #20c997; padding-right: 15px; }
    h2, h3 { color: #2d4059; font-weight: 600; }
    .stButton > button {
        background: linear-gradient(135deg, #6f42c1 0%, #8b5cf6 100%);
        color: white; border-radius: 30px; border: none; padding: 10px 20px;
        font-weight: 600; transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(111, 66, 193, 0.2); width: 100%;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a2b9c 0%, #7c3aed 100%);
        box-shadow: 0 8px 15px rgba(111, 66, 193, 0.3); transform: translateY(-2px);
    }
    .metric-card {
        background: white; border-radius: 20px; padding: 20px 10px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(111, 66, 193, 0.1); text-align: center; transition: transform 0.2s;
    }
    .metric-card:hover { transform: scale(1.02); border-color: #20c997; }
    .dataframe { border-radius: 15px; overflow: hidden; border: none; box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
    .stAlert { border-radius: 15px; border-left-width: 8px; font-weight: 500; }
    div[data-baseweb="notification"] { background-color: #fff8e5; border-left-color: #20c997; }
    .css-1d391kg { background: linear-gradient(180deg, #1e1a2e 0%, #2d1b4e 100%); color: white; }
    .css-1d391kg .stMarkdown, .css-1d391kg .stSelectbox label { color: rgba(255,255,255,0.9); }
    .css-1d391kg .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
        color: white; border-radius: 30px;
    }
    .footer {
        text-align: center; margin-top: 50px; padding: 20px; background: white;
        border-radius: 60px 60px 20px 20px; color: #4a5568; box-shadow: 0 -5px 20px rgba(0,0,0,0.02);
    }
    .banner {
        background: linear-gradient(135deg, #2d1b4e 0%, #4a1d8c 100%);
        padding: 25px; border-radius: 25px; color: white;
        display: flex; align-items: center; gap: 20px; margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(74,29,140,0.4);
    }
    .chat-message {
        background: white; border-radius: 15px; padding: 15px; margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .user-msg { border-right: 5px solid #6f42c1; }
    .assistant-msg { border-right: 5px solid #20c997; }
</style>
""", unsafe_allow_html=True)

# ==================== دوال قاعدة البيانات ====================
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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        qty INTEGER,
        movement_type TEXT,
        date_time TEXT,
        notes TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS refunds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        qty INTEGER,
        refund_amount REAL,
        date_time TEXT
    )
    """)
    conn.commit()
    conn.close()

def check_inventory_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_movements'")
    if cur.fetchone() is None:
        cur.execute("""
        CREATE TABLE inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT,
            qty INTEGER,
            movement_type TEXT,
            date_time TEXT,
            notes TEXT
        )
        """)
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

if check_inventory_table():
    st.toast("🛠️ تم تجهيز جدول حركة المخزون تلقائيًا", icon="✅")

init_db()
conn = get_conn()
cur = conn.cursor()

# ==================== تهيئة الجلسة ====================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "sale_just_completed" not in st.session_state:
    st.session_state.sale_just_completed = False
    st.session_state.expert_tip = ""

# ==================== الدوال المساعدة ====================
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

def record_movement(product, qty, movement_type, notes=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO inventory_movements VALUES (NULL, ?, ?, ?, ?, ?)",
                (product, qty, movement_type, now, notes))
    conn.commit()

def reset_all_data():
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM sales")
    cur.execute("DELETE FROM inventory_movements")
    cur.execute("DELETE FROM refunds")
    conn.commit()
    st.session_state.cart = []
    st.session_state.chat_messages = []

def generate_sales_insight():
    sales_df = pd.read_sql("SELECT * FROM sales", conn)
    products_df = pd.read_sql("SELECT * FROM products", conn)
    
    if sales_df.empty:
        st.info("🎭 لا توجد مبيعات مسجلة بعد. ابدأ ببيع منتج لتظهر التحليلات الذكية!")
        return

    total_revenue = sales_df["total"].sum()
    total_quantity = int(sales_df["qty"].sum())
    
    product_sales = sales_df.groupby("product").agg(
        total_qty=("qty", "sum"),
        total_revenue=("total", "sum")
    ).reset_index()

    top_3 = product_sales.sort_values("total_qty", ascending=False).head(3)

    st.markdown("---")
    st.subheader("📊 تحليل الأداء المالي")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 إجمالي الإيرادات", f"{total_revenue:,.2f} {CURRENCY}")
    with col2:
        st.metric("🛒 إجمالي القطع المباعة", total_quantity)

    st.markdown("---")
    st.subheader("🏆 أفضل 3 منتجات مبيعاً")
    
    for i, (_, row) in enumerate(top_3.iterrows()):
        qty = int(row['total_qty'])
        rev = row['total_revenue']
        st.markdown(f"{i+1}. **{row['product']}** ({qty} قطعة، {rev:,.2f} {CURRENCY})")

    sold_product_names = product_sales["product"].tolist()
    all_product_names = products_df["name"].tolist()
    unsold_products = [p for p in all_product_names if p not in sold_product_names]
    
    if unsold_products:
        st.markdown("---")
        st.warning(f"🚫 منتجات لم تبع بعد: {', '.join(unsold_products)}")
        st.markdown("💡 نصيحة: فكر في عمل عروض ترويجية للمنتجات الراكدة لتحريك مخزونها.")
    else:
        st.markdown("---")
        st.success("💡 أداء ممتاز! جميع منتجاتك تحقق مبيعات. حافظ على هذا الزخم.")

def call_llama(prompt, system_prompt=""):
    """استدعاء نموذج Llama 3.1 عبر Ollama مع معالجة الأخطاء"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    try:
        response = ollama.chat(model='llama3.1:8b', messages=messages)
        return response['message']['content']
    except Exception as e:
        return f"⚠️ خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}"

def get_sales_summary():
    """ملخص المبيعات الحالي لتزويد الخبير الذكي"""
    sales_df = pd.read_sql("SELECT * FROM sales", conn)
    if sales_df.empty:
        return "لا توجد مبيعات بعد."
    total_revenue = sales_df['total'].sum()
    top_product = sales_df.groupby('product')['qty'].sum().idxmax() if not sales_df.empty else "لا يوجد"
    return f"إجمالي الإيرادات: {total_revenue:,.2f} {CURRENCY}. المنتج الأكثر مبيعاً: {top_product}."

# ==================== القائمة الجانبية ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/theater-mask.png", width=80)
    st.markdown("## 🎭 المسرحية المحاسبية")
    st.markdown("### نظام المبيعات X")
    st.markdown("---")
    st.markdown("**🎓 جامعة القرآن الكريم**")
    st.markdown("**📍 غيل باوزير - حضرموت**")
    st.markdown("---")
    menu = st.selectbox("📋 القائمة الرئيسية", [
        "🏠 لوحة التحكم",
        "📦 إدارة المنتجات",
        "🛒 الكاشير",
        "📊 التقارير",
        "📋 حركة المخزون",
        "🔄 استرجاع البضاعة",
        "🧠 الخبير الذكي (شات)"
    ])
    st.markdown("---")
    
    st.markdown("### ⚙️ أدوات النظام")
    if st.button("🔄 إعادة ضبط النظام", use_container_width=True):
        if "confirm_reset" not in st.session_state:
            st.session_state.confirm_reset = True
            st.warning("⚠️ سيتم حذف جميع المنتجات والمبيعات وسجل الحركة. اضغط مرة أخرى للتأكيد.")
        else:
            reset_all_data()
            st.session_state.confirm_reset = False
            st.success("✅ تم إعادة ضبط النظام بنجاح! كل شيء أصبح نظيفًا.")
            st.rerun()
    if "confirm_reset" in st.session_state and st.session_state.confirm_reset:
        st.caption("اضغط الزر مرة أخرى لتأكيد الحذف الكامل.")
    
    st.markdown("---")
    # زر تحميل النسخة المحلية
    if st.button("📥 تحميل نسخة للعمل بدون إنترنت", use_container_width=True):
        try:
            # قراءة السكربت الحالي
            with open(__file__, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # محتويات requirements.txt
            reqs = "streamlit\npandas\nmatplotlib\nollama\n"
            
            # محتويات run_local.bat
            bat = "@echo off\npip install streamlit pandas matplotlib ollama\nstreamlit run app.py\npause\n"
            
            # محتويات README.txt
            readme = """نظام المبيعات X – المسرحية المحاسبية
            إعداد: سالم التريمي | جامعة القرآن الكريم – غيل باوزير

            للتشغيل بدون إنترنت:
            1. تأكد من تثبيت Python 3.9+
            2. شغّل ملف run_local.bat (في ويندوز) أو نفّذ الأوامر يدويًا:
               pip install streamlit pandas matplotlib ollama
               streamlit run app.py
            3. ستحتاج إلى تشغيل خدمة Ollama محليًا مع نموذج llama3.1:8b
            4. افتح المتصفح على http://localhost:8501
            """
            
            # إنشاء ZIP في الذاكرة
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("app.py", script_content)
                zf.writestr("requirements.txt", reqs)
                zf.writestr("run_local.bat", bat)
                zf.writestr("README.txt", readme)
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 انقر لتحميل الملف المضغوط",
                data=zip_buffer,
                file_name="pos_system_offline.zip",
                mime="application/zip",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"حدث خطأ أثناء إنشاء الملف: {e}")
    
    st.markdown("---")
    st.markdown("**👨‍💻 بواسطة: سالم التريمي**")
    st.markdown("*طالب محاسبة - مبتكر*")
    st.markdown("---")
    st.markdown("🎯 *تحويل المحاسبة إلى تجربة حية*")

# ==================== بانر لوحة التحكم ====================
if menu == "🏠 لوحة التحكم":
    st.markdown("""
        <div class="banner">
            <img src="https://img.icons8.com/fluency/96/theater-mask.png" width="80">
            <div>
                <h1 style="color:white; margin:0;">🎭 المسرحية المحاسبية | نظام المبيعات X</h1>
                <p style="color:#e0d7ff; font-size:1.2rem; margin:0;">أول نظام كاشير حضرمي بذكاء اصطناعي محلي</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.title("🎭 المسرحية المحاسبية | نظام المبيعات X")
    st.caption("نظام ذكي لمحاكاة عمليات البيع والشراء - مصمم خصيصًا للورشة التفاعلية")

# ==================== الصفحات ====================
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
    low_stock = get_low_stock_products()
    if not low_stock.empty:
        warning_msg = "⚠️ **تنبيه مخزون:** " + " | ".join([f"{row['name']} ({row['stock']} قطعة)" for _, row in low_stock.iterrows()])
        st.warning(warning_msg)
    else:
        st.success(f"✅ جميع المنتجات بمخزون آمن (أعلى من {LOW_STOCK_THRESHOLD})")

    generate_sales_insight()

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

    # أزرار التحليل الذكي
    st.markdown("---")
    st.subheader("🧠 أدوات الذكاء الاصطناعي")
    col_ai1, col_ai2 = st.columns(2)

    with col_ai1:
        if st.button("🔍 اكتشف المنتجات الراكدة", use_container_width=True):
            with st.spinner("جارٍ التحليل..."):
                # جمع المنتجات التي لم تبع أبدًا
                products_df = pd.read_sql("SELECT name FROM products", conn)
                sales_df = pd.read_sql("SELECT DISTINCT product FROM sales", conn)
                all_prods = set(products_df["name"].tolist())
                sold_prods = set(sales_df["product"].tolist()) if not sales_df.empty else set()
                unsold = list(all_prods - sold_prods)
                if not unsold:
                    st.success("🎉 جميع المنتجات تباع، لا توجد راكدة!")
                else:
                    prompt = f"المنتجات التالية لم تُبع أبداً: {', '.join(unsold)}. قدم خطة ترويجية من 3 نقاط لتحريك مبيعاتها. اكتب النقاط مباشرة."
                    response = call_llama(prompt, "أنت خبير تسويق تجزئة. أعط إجابات قصيرة ومفيدة.")
                    st.markdown("### 💡 خطة ترويجية مقترحة")
                    st.info(response)

    with col_ai2:
        if st.button("📈 توقعات الطلب الذكية", use_container_width=True):
            with st.spinner("جارٍ التوقع..."):
                top_df = get_top_selling_products(5)
                if top_df.empty:
                    st.warning("لا توجد بيانات مبيعات كافية.")
                else:
                    products_list = "\n".join([f"- {row['product']}: بِيع {int(row['total_qty'])} قطعة" for _, row in top_df.iterrows()])
                    prompt = f"بناءً على أفضل 5 منتجات مبيعاً:\n{products_list}\n\nتوقع أي منتج سينفد من المخزون أولاً، وما هي كمية إعادة الطلب المثلى له. كن دقيقاً ومختصراً."
                    response = call_llama(prompt, "أنت محلل مخزون ذكي. قدم إجابة قصيرة.")
                    st.markdown("### 🔮 توقعات الخبير")
                    st.success(response)

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
                    record_movement(name, stock, "إضافة", "مخزون أولي")
                    st.success(f"✅ تمت إضافة {name} بنجاح")
                    st.rerun()
                except:
                    st.error("❌ المنتج موجود مسبقاً")

    st.markdown("---")
    st.markdown("### 📋 جميع المنتجات")
    products_df = pd.read_sql("SELECT id, name, price, stock FROM products", conn)
    
    if not products_df.empty:
        for idx, row in products_df.iterrows():
            col_name, col_price, col_stock, col_action = st.columns([2, 1, 1, 1])
            with col_name:
                st.markdown(f"**{row['name']}**")
            with col_price:
                st.markdown(f"{row['price']:,.0f} {CURRENCY}")
            with col_stock:
                st.markdown(f"{row['stock']} قطعة")
            with col_action:
                if st.button(f"🗑️ حذف", key=f"del_{row['id']}"):
                    with st.spinner("جارٍ الحذف..."):
                        cur.execute("DELETE FROM products WHERE id=?", (row['id'],))
                        cur.execute("DELETE FROM inventory_movements WHERE product=?", (row['name'],))
                        conn.commit()
                        st.warning(f"🗑️ تم حذف المنتج: {row['name']}")
                        st.rerun()
            st.markdown("---")
    else:
        st.info("لا توجد منتجات حالياً")

    st.markdown("---")
    st.markdown("### 🔍 تفاصيل المخزون الحالي")
    for idx, row in products_df.iterrows():
        with st.expander(f"{row['name']} (المتاح: {row['stock']})"):
            mov = pd.read_sql("SELECT * FROM inventory_movements WHERE product=? ORDER BY date_time DESC", conn, params=(row["name"],))
            if not mov.empty:
                st.dataframe(mov[["qty", "movement_type", "date_time", "notes"]], use_container_width=True)
            else:
                st.text("لا توجد حركات مسجلة.")

elif menu == "🛒 الكاشير":
    st.markdown("## 🛒 واجهة البيع")

    # عرض نصيحة الخبير بعد إتمام بيع سابق
    if st.session_state.sale_just_completed and st.session_state.expert_tip:
        st.markdown("---")
        st.markdown("### 🧠 نصيحة الخبير بعد البيع")
        st.info(st.session_state.expert_tip)
        st.session_state.sale_just_completed = False  # إعادة التعيين بعد العرض

    products = pd.read_sql("SELECT * FROM products", conn)
    top_products = get_top_selling_products()
   
