# data/generate_expenses.py
# Generates 12 months of realistic personal expense data

import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs('data', exist_ok=True)

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
START_DATE     = '2024-01-01'
END_DATE       = '2024-12-31'
MONTHLY_INCOME = 75000

CATEGORIES = {
    'Food & Dining'  : {'min': 200,  'max': 2500,  'freq': 25},
    'Transportation' : {'min': 50,   'max': 800,   'freq': 20},
    'Shopping'       : {'min': 500,  'max': 8000,  'freq': 8},
    'Entertainment'  : {'min': 200,  'max': 3000,  'freq': 6},
    'Health'         : {'min': 300,  'max': 5000,  'freq': 4},
    'Education'      : {'min': 1000, 'max': 10000, 'freq': 3},
    'Utilities'      : {'min': 500,  'max': 3000,  'freq': 4},
    'Rent'           : {'min': 12000,'max': 12000, 'freq': 1},
    'Groceries'      : {'min': 1000, 'max': 5000,  'freq': 6},
    'Travel'         : {'min': 3000, 'max': 20000, 'freq': 2},
}

PAYMENT_METHODS = ['UPI', 'Credit Card', 'Debit Card', 'Cash', 'Net Banking']
PAYMENT_WEIGHTS = [0.40, 0.25, 0.20, 0.10, 0.05]

DESCRIPTIONS = {
    'Food & Dining'  : ['Zomato order', 'Swiggy delivery', 'Restaurant dinner',
                        'Cafe coffee', 'Street food', 'Lunch with friends'],
    'Transportation' : ['Ola cab', 'Uber ride', 'Metro card recharge',
                        'Petrol', 'Auto rickshaw', 'Bus ticket'],
    'Shopping'       : ['Amazon purchase', 'Flipkart order', 'Clothes shopping',
                        'Electronics', 'Home decor', 'Myntra order'],
    'Entertainment'  : ['Netflix subscription', 'Movie tickets', 'Spotify premium',
                        'Gaming', 'Concert tickets', 'Amazon Prime'],
    'Health'         : ['Doctor consultation', 'Medicine', 'Gym membership',
                        'Lab tests', 'Pharmacy', 'Health checkup'],
    'Education'      : ['Udemy course', 'Books', 'Online certification',
                        'Coaching fees', 'Stationery', 'Workshop'],
    'Utilities'      : ['Electricity bill', 'Internet bill', 'Mobile recharge',
                        'Water bill', 'Gas cylinder', 'DTH recharge'],
    'Rent'           : ['Monthly rent', 'Room rent', 'PG accommodation'],
    'Groceries'      : ['BigBasket order', 'Blinkit delivery', 'Vegetable market',
                        'Supermarket', 'D-Mart shopping', 'Milk & dairy'],
    'Travel'         : ['Flight ticket', 'Hotel booking', 'Train ticket',
                        'Holiday trip', 'Weekend trip', 'Bus booking'],
}

# -------------------------------------------------------
# GENERATE TRANSACTIONS
# -------------------------------------------------------
date_range = pd.date_range(START_DATE, END_DATE, freq='D')
records = []

for date in date_range:
    month = date.month
    for category, config in CATEGORIES.items():
        daily_prob = config['freq'] / 30

        if category == 'Travel' and month in [5, 6, 12]:
            daily_prob *= 2.5
        if category == 'Shopping' and month in [10, 11, 12]:
            daily_prob *= 2.0
        if category == 'Entertainment' and month in [12, 1]:
            daily_prob *= 1.5

        if np.random.random() < daily_prob:
            amount = np.random.randint(config['min'], config['max'] + 1)
            if date.dayofweek >= 5:
                if category in ['Food & Dining', 'Entertainment', 'Shopping']:
                    amount = int(amount * np.random.uniform(1.2, 1.6))

            records.append({
                'date'           : date,
                'category'       : category,
                'amount'         : amount,
                'payment_method' : np.random.choice(PAYMENT_METHODS,
                                                    p=PAYMENT_WEIGHTS),
                'description'    : np.random.choice(DESCRIPTIONS[category]),
                'month'          : date.strftime('%B'),
                'month_num'      : month,
                'day_of_week'    : date.strftime('%A'),
                'is_weekend'     : 1 if date.dayofweek >= 5 else 0,
                'week_of_year'   : date.isocalendar()[1],
            })

df = pd.DataFrame(records)
df = df.sort_values('date').reset_index(drop=True)
df['transaction_id'] = [f'TXN{1000 + i}' for i in range(len(df))]

# -------------------------------------------------------
# BUILD MONTHLY SUMMARY — no merge, direct calculation
# -------------------------------------------------------
rows = []
for m in range(1, 13):
    month_date  = pd.Timestamp(f'2024-{m:02d}-01')
    month_name  = month_date.strftime('%B')
    month_txns  = df[df['month_num'] == m]
    total_exp   = int(month_txns['amount'].sum())
    savings     = MONTHLY_INCOME - total_exp
    savings_pct = round(savings / MONTHLY_INCOME * 100, 2)

    rows.append({
        'month_num'   : m,
        'month'       : month_name,
        'income'      : MONTHLY_INCOME,
        'total_expense': total_exp,
        'savings'     : savings,
        'savings_rate': savings_pct,
    })

income_df = pd.DataFrame(rows)

# -------------------------------------------------------
# SAVE
# -------------------------------------------------------
df.to_csv('data/expenses.csv', index=False)
income_df.to_csv('data/monthly_summary.csv', index=False)

print("✅ Expense dataset created!")
print(f"   Total Transactions : {len(df)}")
print(f"   Date Range         : {df['date'].min().date()} to {df['date'].max().date()}")
print(f"   Total Spent        : Rs.{df['amount'].sum():,}")
print(f"   Avg Monthly Spend  : Rs.{df['amount'].sum()//12:,}")
print(f"\n Category Breakdown:")
cat_summary = df.groupby('category')['amount'].sum().sort_values(ascending=False)
for cat, amt in cat_summary.items():
    print(f"   {cat:<20}: Rs.{amt:>10,}")
print(f"\n Monthly Summary:")
print(income_df[['month','income','total_expense',
                  'savings','savings_rate']].to_string(index=False))
print("\n Files saved: data/expenses.csv and data/monthly_summary.csv")