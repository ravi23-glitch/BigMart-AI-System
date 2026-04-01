import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="BigMart AI Dashboard", layout="wide")

# ---------------- TITLE ----------------
st.title("📊 BigMart AI Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    np.random.seed(42)
    data = pd.DataFrame({
        "Sales": np.random.randint(1000, 15000, 8500),
        "Item_Type": np.random.choice(["Food", "Drinks", "Non-Consumable"], 8500),
        "Outlet_Size": np.random.choice(["Small", "Medium", "High"], 8500)
    })
    return data

df = load_data()

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Records", len(df))
col2.metric("Average Sales", f"₹ {int(df['Sales'].mean())}")
col3.metric("Max Sales", f"₹ {int(df['Sales'].max())}")

st.markdown("---")

# ---------------- FILTER ----------------
st.sidebar.header("🔍 Filter Data")

selected_type = st.sidebar.selectbox(
    "Select Item Type",
    df["Item_Type"].unique()
)

filtered_df = df[df["Item_Type"] == selected_type]

# ---------------- CHART 1 (SAFE HISTOGRAM) ----------------
st.subheader("📈 Sales Distribution")

fig1, ax1 = plt.subplots()
ax1.hist(filtered_df["Sales"], bins=25)
ax1.set_xlabel("Sales")
ax1.set_ylabel("Frequency")
ax1.set_title("Sales Distribution")

st.pyplot(fig1)   # ✅ Safe (no recursion)


# ---------------- CHART 2 (BAR CHART) ----------------
st.subheader("📊 Average Sales by Item Type")

avg_sales = df.groupby("Item_Type")["Sales"].mean()

fig2, ax2 = plt.subplots()
avg_sales.plot(kind="bar", ax=ax2)

st.pyplot(fig2)   # ✅ Safe


# ---------------- STREAMLIT CHART (BEST PRACTICE) ----------------
st.subheader("⚡ Quick Trend")

st.line_chart(filtered_df["Sales"].head(50))


# ---------------- DATA TABLE ----------------
st.subheader("📋 Filtered Data")

st.dataframe(filtered_df.head(20))


# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🚀 Built with Streamlit | BigMart AI Project")
