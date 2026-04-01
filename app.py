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
st.set_page_config(page_title="BigMart AI", layout="wide")

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
# LOAD MODEL + DATA
# ======================
model = pickle.load(open('model.pkl', 'rb'))
data = pd.read_csv('Train.csv')

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.stApp { background: #f5f7fb; }
.card {
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0 5px 15px rgba(0,0,0,0.08);
}
.stButton>button {
    background: linear-gradient(to right,#ff512f,#dd2476);
    color:white;
    border-radius:10px;
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

    st.title("🔐 BigMart Login")

    menu = st.radio("", ["Login", "Register"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Register":
        role = st.selectbox("Role", ["user", "admin"])
        if st.button("Register"):
            try:
                register_user(username, password, role)
                st.success("Registered!")
            except:
                st.error("User exists")

    else:
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.user = username
                st.session_state.role = user[2]

                c.execute("INSERT INTO login_logs VALUES (?, ?)",
                          (username, str(datetime.now())))
                conn.commit()

                st.rerun()
            else:
                st.error("Invalid login")

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
    # HOME
    # ======================
    if page == "Home":
        st.title("🛒 BigMart AI System")
        st.image("https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif")
        st.write("Smart Retail Prediction System using Machine Learning.")

    # ======================
    # DASHBOARD (FIXED)
    # ======================
    elif page == "Dashboard":

        st.title("📊 Dashboard")

        col1, col2, col3 = st.columns(3)

        col1.metric("Records", len(data))
        col2.metric("Avg Sales", f"₹ {data['Item_Outlet_Sales'].mean():.0f}")
        col3.metric("Max Sales", f"₹ {data['Item_Outlet_Sales'].max():.0f}")

        st.subheader("Sales Distribution")

        # ✅ FIXED SAFE PLOT
        fig = plt.figure()
        plt.hist(data['Item_Outlet_Sales'], bins=30)
        plt.xlabel("Sales")
        plt.ylabel("Count")

        st.pyplot(fig)
        plt.close(fig)  # 🔥 VERY IMPORTANT FIX

    # ======================
    # PREDICTION
    # ======================
    elif page == "Prediction":

        st.title("🤖 Prediction")

        weight = st.slider("Weight", 0.0, 25.0, 10.0)
        visibility = st.slider("Visibility", 0.0, 0.5, 0.1)
        mrp = st.slider("MRP", 50.0, 300.0, 150.0)

        if st.button("Predict"):

            input_data = np.array([[0,weight,0,visibility,0,mrp,0,2000,0,0,0]])
            pred = model.predict(input_data)[0]

            c.execute("INSERT INTO predictions VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.user, mrp, weight, pred, str(datetime.now())))
            conn.commit()

            st.success(f"💰 ₹ {pred:.2f}")

    # ======================
    # HISTORY
    # ======================
    elif page == "History":

        df = pd.read_sql(f"SELECT * FROM predictions WHERE username='{st.session_state.user}'", conn)
        st.dataframe(df)

    # ======================
    # ADMIN PANEL
    # ======================
    elif page == "Admin Panel":

        st.title("👨‍💼 Admin Panel")

        tab1, tab2, tab3 = st.tabs(["Users","Predictions","Logs"])

        with tab1:
            st.dataframe(pd.read_sql("SELECT * FROM users", conn))

        with tab2:
            st.dataframe(pd.read_sql("SELECT * FROM predictions", conn))

        with tab3:
            st.dataframe(pd.read_sql("SELECT * FROM login_logs", conn))
