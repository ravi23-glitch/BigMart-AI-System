import streamlit as st
import sqlite3
import pickle
import numpy as np
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px
import time

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="BigMart SaaS", layout="wide")

# ======================
# LOADING SCREEN
# ======================
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    st.markdown("""
    <div style='text-align:center; padding-top:150px;'>
        <h1>🚀 BigMart AI</h1>
        <p>Loading Smart Retail Intelligence...</p>
    </div>
    """, unsafe_allow_html=True)

    st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        st.progress(i+1)

    st.session_state.loaded = True
    st.rerun()

# ======================
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users(
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS predictions(
    username TEXT,
    item_mrp REAL,
    item_weight REAL,
    prediction REAL,
    timestamp TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS login_logs(
    username TEXT,
    login_time TEXT
)""")

conn.commit()

# ======================
# LOAD DATA
# ======================
model = pickle.load(open('model.pkl', 'rb'))
data = pd.read_csv('Train.csv')

# ======================
# 🎨 PREMIUM UI
# ======================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
}
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Logo */
.logo {
    font-size: 24px;
    font-weight: bold;
    padding: 10px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-5px);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(to right,#6366f1,#8b5cf6);
    color:white;
    border-radius:12px;
    height:45px;
    font-weight:bold;
}

/* Animation */
.fade {
    animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
    from {opacity:0;}
    to {opacity:1;}
}
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION
# ======================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ======================
# AUTH
# ======================
def register_user(username, password, role):
    c.execute("INSERT INTO users VALUES (?, ?, ?)",
              (username, hash_password(password), role))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# ======================
# LOGIN PAGE
# ======================
if st.session_state.user is None:

    st.markdown("<h1 style='text-align:center;'>🚀 BigMart SaaS Platform</h1>", unsafe_allow_html=True)

    menu = st.radio("", ["Login", "Register"], horizontal=True)

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if menu == "Register":
        role = st.selectbox("Role", ["user", "admin"])
        if st.button("Create Account 🚀"):
            try:
                register_user(username, password, role)
                st.success("Account created!")
            except:
                st.error("Username exists")

    else:
        if st.button("Login 🔐"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.session_state.role = user[2]

                c.execute("INSERT INTO login_logs VALUES (?, ?)",
                          (username, str(datetime.now())))
                conn.commit()

                st.rerun()
            else:
                st.error("Invalid credentials")

# ======================
# MAIN APP
# ======================
else:

    # Sidebar branding
    st.sidebar.markdown("<div class='logo'>🛒 BigMart</div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {st.session_state.user}")
    st.sidebar.write(f"🛡 {st.session_state.role}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

    pages = ["🏠 Home", "📊 Dashboard", "🤖 Prediction", "📜 History"]
    if st.session_state.role == "admin":
        pages.append("👨‍💼 Admin")

    page = st.sidebar.radio("Navigation", pages)

    # HOME
    if page == "🏠 Home":
        st.markdown("<h1 class='fade'>🚀 Welcome to BigMart SaaS</h1>", unsafe_allow_html=True)
        st.write("AI-powered retail intelligence platform.")
        st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif")

    # DASHBOARD
    elif page == "📊 Dashboard":

        st.markdown("<h2 class='fade'>📊 Dashboard</h2>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='card'><h4>📦 Records</h4><h2>{len(data)}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><h4>📈 Avg Sales</h4><h2>₹ {data['Item_Outlet_Sales'].mean():.0f}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><h4>💰 Max Sales</h4><h2>₹ {data['Item_Outlet_Sales'].max():.0f}</h2></div>", unsafe_allow_html=True)

        fig = px.histogram(data, x="Item_Outlet_Sales", nbins=40)
        st.plotly_chart(fig, use_container_width=True)

    # PREDICTION
    elif page == "🤖 Prediction":

        st.markdown("<h2 class='fade'>🤖 Prediction Engine</h2>", unsafe_allow_html=True)

        weight = st.slider("⚖ Weight", 0.0, 25.0, 10.0)
        visibility = st.slider("👁 Visibility", 0.0, 0.5, 0.1)
        mrp = st.slider("💰 MRP", 50.0, 300.0, 150.0)

        if st.button("🚀 Predict"):
            input_data = np.array([[0,weight,0,visibility,0,mrp,0,2000,0,0,0]])
            pred = model.predict(input_data)[0]

            c.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.user, mrp, weight, pred, str(datetime.now())))
            conn.commit()

            st.success(f"💰 Predicted Sales: ₹ {pred:.2f}")

    # HISTORY
    elif page == "📜 History":
        df = pd.read_sql(f"SELECT * FROM predictions WHERE username='{st.session_state.user}'", conn)
        st.dataframe(df, use_container_width=True)

    # ADMIN
    elif page == "👨‍💼 Admin":
        tab1, tab2, tab3 = st.tabs(["Users","Predictions","Logs"])

        with tab1:
            st.dataframe(pd.read_sql("SELECT * FROM users", conn))

        with tab2:
            st.dataframe(pd.read_sql("SELECT * FROM predictions", conn))

        with tab3:
            st.dataframe(pd.read_sql("SELECT * FROM login_logs", conn))

 
