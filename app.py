import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="BigMart AI System",
    page_icon="🛒",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.big-title {
    font-size: 42px;
    font-weight: bold;
    color: #2c3e50;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="big-title">🛒 BigMart AI Dashboard</div>', unsafe_allow_html=True)
st.write("Smart Sales Analysis & Insights System")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    np.random.seed(42)
    data = pd.DataFrame({
        "Sales": np.random.randint(1000, 15000, 8500),
        "Item_Type": np.random.choice(["Food", "Drinks", "Non-Consumable"], 8500),
        "Outlet_Size": np.random.choice(["Small", "Medium", "High"], 8500),
        "Outlet_Location": np.random.choice(["Tier 1", "Tier 2", "Tier 3"], 8500)
    })
    return data

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")

item_type = st.sidebar.selectbox("Select Item Type", df["Item_Type"].unique())
outlet_size = st.sidebar.selectbox("Select Outlet Size", df["Outlet_Size"].unique())

filtered_df = df[
    (df["Item_Type"] == item_type) &
    (df["Outlet_Size"] == outlet_size)
]

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📦 Total Records", len(filtered_df))

with col2:
    st.metric("💰 Avg Sales", f"₹ {int(filtered_df['Sales'].mean())}")

with col3:
    st.metric("🔥 Max Sales", f"₹ {int(filtered_df['Sales'].max())}")

st.markdown("---")

# ---------------- CHART 1 ----------------
st.subheader("📈 Sales Distribution")

fig1, ax1 = plt.subplots()
ax1.hist(filtered_df["Sales"], bins=25)
ax1.set_title("Sales Distribution")
ax1.set_xlabel("Sales")
ax1.set_ylabel("Frequency")

st.pyplot(fig1)   # ✅ No recursion issue

# ---------------- CHART 2 ----------------
st.subheader("📊 Avg Sales by Item Type")

avg_sales = df.groupby("Item_Type")["Sales"].mean()

fig2, ax2 = plt.subplots()
avg_sales.plot(kind="bar", ax=ax2)
ax2.set_title("Average Sales by Item Type")

st.pyplot(fig2)   # ✅ Safe

# ---------------- STREAMLIT CHART ----------------
st.subheader("⚡ Sales Trend (Fast Chart)")
st.line_chart(filtered_df["Sales"].head(50))

# ---------------- EXTRA INSIGHT ----------------
st.subheader("📍 Sales by Outlet Location")

location_sales = df.groupby("Outlet_Location")["Sales"].mean()

fig3, ax3 = plt.subplots()
location_sales.plot(kind="pie", autopct='%1.1f%%', ax=ax3)

st.pyplot(fig3)

# ---------------- DATA TABLE ----------------
st.subheader("📋 Filtered Data Preview")
st.dataframe(filtered_df.head(20))

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🚀 Built with ❤️ using Streamlit | BigMart AI System")
