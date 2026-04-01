import streamlit as st
import sqlite3
import pickle
import numpy as np
import pandas as pd
import time
import hashlib
from datetime import datetime
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="BigMart AI System", layout="wide")

# ======================
# HASH FUNCTION
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
# LOAD MODEL + DATA
# ======================
model = pickle.load(open('model.pkl', 'rb'))
data = pd.read_csv('Train.csv')

# ======================
# 🎨 UI STYLE
# ======================
st.markdown("""
<style>
.stApp { background: linear-gradient(to right,#eef2f3,#ffffff); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: white;
}

/* Titles */
h1,h2,h3 { color:#0d47a1; }

/* Cards */
.card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0 8px 20px rgba(0,0,0,0.08);
    transition:0.3s;
}
.card:hover { transform: scale(1.05); }

/* Buttons */
.stButton>button {
    background: linear-gradient(to right,#ff512f,#dd2476);
    color:white;
    border-radius:10px;
    height:45px;
    font-weight:bold;
}

/* Animation */
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
# AUTH FUNCTIONS
# ======================
def register_user(username, password, role):
    hashed = hash_password(password)
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hashed, role))
    conn.commit()

def login_user(username, password):
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    return c.fetchone()

# ======================
# LOGIN PAGE
# ======================
if st.session_state.user is None:

    st.markdown("<h1 style='text-align:center;'>🔐 BigMart AI Login</h1>", unsafe_allow_html=True)

    menu = st.radio("", ["Login", "Register"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Register":
        role = st.selectbox("Role", ["user", "admin"])

        if st.button("Register"):
            if len(password) < 4:
                st.warning("Password must be at least 4 characters")
            else:
                try:
                    register_user(username, password, role)
                    st.success("Account created!")
                except:
                    st.error("Username already exists")

    else:
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.session_state.role = user[2]

                c.execute("INSERT INTO login_logs VALUES (?, ?)",
                          (username, str(datetime.now())))
                conn.commit()

                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# ======================
# MAIN APP
# ======================
else:

    st.sidebar.write(f"👤 {st.session_state.user}")
    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    pages = ["Home", "Dashboard", "Prediction", "History"]
    if st.session_state.role == "admin":
        pages.append("Admin Panel")

    page = st.sidebar.radio("Navigation", pages)

    # ======================
    # 🏠 HOME
    # ======================
    if page == "Home":

        st.markdown("<h1 style='text-align:center;'>🛒 BigMart AI Platform</h1>", unsafe_allow_html=True)

        st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif")

        st.markdown("## 📌 About")
        st.write("""
        This system predicts retail sales using Machine Learning. It helps businesses 
        optimize pricing, inventory, and decision-making.
        """)

        col1, col2, col3 = st.columns(3)

        col1.markdown("<div class='card'><h3>📊 Analytics</h3></div>", unsafe_allow_html=True)
        col2.markdown("<div class='card'><h3>🤖 Prediction</h3></div>", unsafe_allow_html=True)
        col3.markdown("<div class='card'><h3>🔐 Secure</h3></div>", unsafe_allow_html=True)

    # ======================
    # DASHBOARD
    # ======================
    elif page == "Dashboard":

        st.title("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric("Records", len(data))
        col2.metric("Avg Sales", f"₹ {data['Item_Outlet_Sales'].mean():.0f}")
        col3.metric("Max Sales", f"₹ {data['Item_Outlet_Sales'].max():.0f}")

        fig, ax = plt.subplots()
        ax.hist(data['Item_Outlet_Sales'], bins=30)
        st.pyplot(fig)

    # ======================
    # PREDICTION
    # ======================
    elif page == "Prediction":

        st.title("🤖 Prediction")

        item_weight = st.slider("Weight", 0.0, 25.0, 10.0)
        item_visibility = st.slider("Visibility", 0.0, 0.5, 0.1)
        item_mrp = st.slider("MRP", 50.0, 300.0, 150.0)

        if st.button("Predict"):
            with st.spinner("Processing..."):
                time.sleep(1)

                input_data = np.array([[0,item_weight,0,item_visibility,0,item_mrp,0,2000,0,0,0]])
                prediction = model.predict(input_data)[0]

                c.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?)",
                          (st.session_state.user, item_mrp, item_weight,
                           prediction, str(datetime.now())))
                conn.commit()

                st.success(f"💰 ₹ {prediction:.2f}")

    # ======================
    # HISTORY
    # ======================
    elif page == "History":

        st.title("📜 History")

        df = pd.read_sql(f"SELECT * FROM predictions WHERE username='{st.session_state.user}'", conn)
        st.dataframe(df)

    # ======================
    # ADMIN PANEL
    # ======================
    elif page == "Admin Panel":

        st.title("👨‍💼 Admin Panel")

        tab1, tab2, tab3 = st.tabs(["Users","Predictions","Logins"])

        with tab1:
            st.dataframe(pd.read_sql("SELECT * FROM users", conn))

        with tab2:
            st.dataframe(pd.read_sql("SELECT * FROM predictions", conn))

        with tab3:
            st.dataframe(pd.read_sql("SELECT * FROM login_logs", conn))
