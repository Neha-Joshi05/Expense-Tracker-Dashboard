import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('outputs/expenses_clean.csv')
monthly = pd.read_csv('outputs/monthly_summary.csv')
category = pd.read_csv('outputs/category_summary.csv')

# -------------------------------
# 1. Monthly Spending Trend
# -------------------------------
plt.figure(figsize=(10,5))

plt.plot(monthly['month'], monthly['total_expense'], marker='o')

plt.title("Monthly Spending Trend")
plt.xlabel("Month")
plt.ylabel("Total Expense")
plt.grid()

plt.savefig('images/monthly_trend.png')
plt.show()

# -------------------------------
# 2. Category-wise Spending
# -------------------------------
plt.figure(figsize=(10,5))

sns.barplot(x='total_spent', y='category', data=category, palette='coolwarm')

plt.title("Spending by Category")

plt.savefig('images/category_spending.png')
plt.show()

# -------------------------------
# 3. Expense Distribution
# -------------------------------
plt.figure(figsize=(6,6))

plt.pie(category['total_spent'], labels=category['category'], autopct='%1.1f%%')

plt.title("Expense Distribution")

plt.savefig('images/pie_chart.png')
plt.show()

# -------------------------------
# 4. Insights
# -------------------------------
print("\n--- INSIGHTS ---")

# Highest spending category
top_category = category.sort_values(by='total_spent', ascending=False).head(1)
print("\n1. Highest Spending Category:")
print(top_category)

# Total expense
total_expense = df['amount'].sum()
print("\n2. Total Expense:", total_expense)

# Average expense
avg_expense = df['amount'].mean()
print("3. Average Expense:", avg_expense)