# src/preprocess.py
# Data Cleaning & Feature Engineering for Expense Tracker

import pandas as pd
import numpy as np
import os

os.makedirs('outputs', exist_ok=True)

# -------------------------------------------------------
# STEP 1: Load Data
# -------------------------------------------------------
df         = pd.read_csv('data/expenses.csv', parse_dates=['date'])
income_df  = pd.read_csv('data/monthly_summary.csv')

print("✅ Data Loaded")
print(f"   Transactions : {len(df)}")
print(f"   Columns      : {list(df.columns)}\n")

# -------------------------------------------------------
# STEP 2: Check Data Quality
# -------------------------------------------------------
print("🔍 Missing Values:")
print(df.isnull().sum())

print(f"\n🔍 Duplicate Transactions: {df.duplicated().sum()}")
df.drop_duplicates(inplace=True)

print(f"\n🔍 Amount Stats:")
print(df['amount'].describe().round(2))

# Remove any negative or zero amounts (data quality)
before = len(df)
df = df[df['amount'] > 0]
print(f"\n✅ Removed {before - len(df)} invalid rows")

# -------------------------------------------------------
# STEP 3: Feature Engineering
# -------------------------------------------------------

# Feature 1: quarter
df['quarter'] = df['date'].dt.quarter.map(
    {1:'Q1 (Jan-Mar)', 2:'Q2 (Apr-Jun)',
     3:'Q3 (Jul-Sep)', 4:'Q4 (Oct-Dec)'}
)

# Feature 2: week_part
df['week_part'] = df['is_weekend'].map({0: 'Weekday', 1: 'Weekend'})

# Feature 3: expense_size bucket
def size_bucket(amt):
    if amt < 500:       return 'Small (<500)'
    elif amt < 2000:    return 'Medium (500-2000)'
    elif amt < 5000:    return 'Large (2000-5000)'
    else:               return 'Very Large (5000+)'

df['expense_size'] = df['amount'].apply(size_bucket)

# Feature 4: is_essential
ESSENTIAL = ['Rent', 'Groceries', 'Utilities', 'Health', 'Education']
df['is_essential'] = df['category'].apply(
    lambda x: 'Essential' if x in ESSENTIAL else 'Non-Essential'
)

# Feature 5: cumulative monthly spend
df = df.sort_values('date')
df['cumulative_monthly_spend'] = df.groupby('month_num')['amount'].cumsum()

# Feature 6: day of month
df['day_of_month'] = df['date'].dt.day

# Feature 7: spending vs monthly average
monthly_avg = df.groupby('month_num')['amount'].transform('mean')
df['vs_monthly_avg'] = ((df['amount'] - monthly_avg) / monthly_avg * 100).round(2)

print("\n✅ Feature Engineering Complete!")
print(f"   New features added: quarter, week_part, expense_size,")
print(f"   is_essential, cumulative_monthly_spend, day_of_month, vs_monthly_avg")

# -------------------------------------------------------
# STEP 4: Category-level Summary
# -------------------------------------------------------
cat_summary = df.groupby('category').agg(
    total_spent   = ('amount', 'sum'),
    avg_per_txn   = ('amount', 'mean'),
    num_txns      = ('amount', 'count'),
    max_single    = ('amount', 'max'),
).reset_index().sort_values('total_spent', ascending=False)

cat_summary['pct_of_total'] = (
    cat_summary['total_spent'] / cat_summary['total_spent'].sum() * 100
).round(2)
cat_summary['avg_per_txn'] = cat_summary['avg_per_txn'].round(0).astype(int)

print("\n📊 Category Summary:")
print(cat_summary.to_string(index=False))

# -------------------------------------------------------
# STEP 5: Payment Method Summary
# -------------------------------------------------------
pay_summary = df.groupby('payment_method').agg(
    total_spent = ('amount', 'sum'),
    num_txns    = ('amount', 'count'),
).reset_index().sort_values('total_spent', ascending=False)

pay_summary['pct_of_total'] = (
    pay_summary['total_spent'] / pay_summary['total_spent'].sum() * 100
).round(2)

print("\n💳 Payment Method Summary:")
print(pay_summary.to_string(index=False))

# -------------------------------------------------------
# STEP 6: Essential vs Non-Essential
# -------------------------------------------------------
ess_summary = df.groupby('is_essential')['amount'].agg(['sum','count']).reset_index()
ess_summary.columns = ['type', 'total', 'transactions']
ess_summary['pct'] = (ess_summary['total'] / ess_summary['total'].sum() * 100).round(2)

print("\n🧾 Essential vs Non-Essential:")
print(ess_summary.to_string(index=False))

# -------------------------------------------------------
# STEP 7: Budget Alert System
# -------------------------------------------------------
BUDGETS = {
    'Food & Dining'  : 8000,
    'Shopping'       : 10000,
    'Entertainment'  : 5000,
    'Travel'         : 15000,
    'Health'         : 8000,
    'Education'      : 12000,
    'Utilities'      : 5000,
    'Rent'           : 13000,
    'Groceries'      : 8000,
    'Transportation' : 4000,
}

monthly_cat = df.groupby(['month_num', 'month', 'category'])['amount'].sum().reset_index()
monthly_cat.columns = ['month_num', 'month', 'category', 'spent']
monthly_cat['budget']     = monthly_cat['category'].map(BUDGETS)
monthly_cat['difference'] = monthly_cat['budget'] - monthly_cat['spent']
monthly_cat['status']     = monthly_cat['difference'].apply(
    lambda x: '🔴 OVER BUDGET' if x < 0
    else ('🟡 NEAR LIMIT' if x < 1000 else '🟢 ON TRACK')
)

alerts = monthly_cat[monthly_cat['status'] == '🔴 OVER BUDGET']
print(f"\n🚨 Budget Alerts — Over Budget Instances: {len(alerts)}")
print(alerts[['month','category','spent','budget','difference']].to_string(index=False))

# -------------------------------------------------------
# STEP 8: Save All Outputs
# -------------------------------------------------------
df.to_csv('outputs/expenses_clean.csv', index=False)
cat_summary.to_csv('outputs/category_summary.csv', index=False)
pay_summary.to_csv('outputs/payment_summary.csv', index=False)
monthly_cat.to_csv('outputs/monthly_budget_status.csv', index=False)
income_df.to_csv('outputs/monthly_summary.csv', index=False)

print("\n✅ All outputs saved to outputs/")
print("🎯 Preprocessing Complete!")