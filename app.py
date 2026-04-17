import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker Dashboard")
st.markdown("---")

# -------------------------------
# Load Data (Cached for speed ⚡)
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('outputs/expenses_clean.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔍 Filters")

# Month filter
months = sorted(df['month'].unique(), key=lambda x: list(df['month']).index(x))
selected_month = st.sidebar.multiselect(
    "Select Month",
    options=months,
    default=months
)

# Category filter
categories = df['category'].unique()
selected_category = st.sidebar.multiselect(
    "Select Category",
    options=categories,
    default=categories
)

# -------------------------------
# Apply Filters (CORE FIX 🔥)
# -------------------------------
filtered_df = df[
    (df['month'].isin(selected_month)) &
    (df['category'].isin(selected_category))
]

# -------------------------------
# Recalculate EVERYTHING from filtered data
# -------------------------------

# Monthly aggregation
filtered_monthly = filtered_df.groupby(['month_num', 'month']).agg({
    'amount': 'sum'
}).reset_index().rename(columns={'amount': 'total_expense'})

# Sort months properly
filtered_monthly = filtered_monthly.sort_values(by='month_num')

# Category aggregation
filtered_category = filtered_df.groupby('category').agg({
    'amount': 'sum'
}).reset_index().rename(columns={'amount': 'total_spent'})

# -------------------------------
# KPIs (LIVE UPDATE ⚡)
# -------------------------------
total_expense = filtered_df['amount'].sum()
avg_expense = filtered_df['amount'].mean()

col1, col2 = st.columns(2)

col1.metric("💸 Total Expense", f"₹ {total_expense:,.0f}")
col2.metric("📊 Avg Expense", f"₹ {avg_expense:,.2f}")

st.markdown("---")

# -------------------------------
# 📈 Monthly Trend
# -------------------------------
st.subheader("📈 Monthly Expense Trend")

fig1 = px.line(
    filtered_monthly,
    x='month',
    y='total_expense',
    markers=True
)

fig1.update_layout(template='plotly_dark')

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------
# 📊 Category Spending
# -------------------------------
st.subheader("📊 Category-wise Spending")

fig2 = px.bar(
    filtered_category,
    x='total_spent',
    y='category',
    orientation='h',
    color='total_spent'
)

fig2.update_layout(template='plotly_dark')

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# 🥧 Expense Distribution
# -------------------------------
st.subheader("🥧 Expense Distribution")

fig3 = px.pie(
    filtered_category,
    values='total_spent',
    names='category'
)

fig3.update_layout(template='plotly_dark')

st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# 💡 Insights
# -------------------------------
st.markdown("---")
st.subheader("💡 Insights")

if not filtered_category.empty:
    top_category = filtered_category.sort_values(by='total_spent', ascending=False).iloc[0]
    st.success(f"🔥 Highest spending category: {top_category['category']}")

if total_expense > 50000:
    st.warning("⚠️ High spending detected! Consider budgeting.")
else:
    st.info("✅ Spending is under control.")

# -------------------------------
# 📋 Data Table (LIVE FILTERED)
# -------------------------------
st.markdown("---")
st.subheader("📋 Transactions")

st.dataframe(filtered_df)