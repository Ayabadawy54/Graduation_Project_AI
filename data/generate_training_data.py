"""
Talentree AI - Training Data Generator
=======================================
Generates large synthetic datasets as CSV files for offline ML training.
These are NOT inserted into the database - they exist only for training.

Output files:
  csv/churn_training.csv      - 5000 users with churn labels
  csv/fraud_training.csv      - 5000 orders with fraud labels
  csv/anomaly_training.csv    - 5000 transactions with anomaly labels
  csv/demand_training.csv     - Time series data for demand forecasting
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

np.random.seed(42)
random.seed(42)


# ============================================================
# 1. CHURN TRAINING DATA (5000 users)
# ============================================================
def generate_churn_data(n=5000):
    """
    Features that indicate churn risk:
    - days_since_last_login: high = churned
    - login_count_30d: low = churned
    - total_orders: low = churned
    - avg_order_value: low = churned
    - support_tickets_open: high = churned
    - profile_completeness: low = churned
    - account_age_days: new users churn more
    - product_count: BOs with few products churn more
    - revenue_last_30d: low = churned
    - negative_review_pct: high = churned
    """
    print("Generating churn_training.csv (5000 users)...")

    data = []
    for i in range(n):
        # Decide if churned first (25% churn rate)
        is_churned = np.random.random() < 0.25

        if is_churned:
            # Churned user pattern
            days_since_last_login = np.random.randint(30, 180)
            login_count_30d = np.random.randint(0, 3)
            total_orders = np.random.randint(0, 5)
            avg_order_value = round(np.random.uniform(0, 3000), 2)
            support_tickets_open = np.random.randint(0, 8)
            profile_completeness = np.random.randint(10, 60)
            account_age_days = np.random.randint(5, 365)
            product_count = np.random.randint(0, 3)
            revenue_last_30d = round(np.random.uniform(0, 2000), 2)
            negative_review_pct = round(np.random.uniform(0.15, 0.6), 2)
            login_frequency_weekly = round(np.random.uniform(0, 1.5), 2)
            avg_session_minutes = round(np.random.uniform(0.5, 5), 2)
        else:
            # Active user pattern
            days_since_last_login = np.random.randint(0, 14)
            login_count_30d = np.random.randint(5, 60)
            total_orders = np.random.randint(3, 50)
            avg_order_value = round(np.random.uniform(2000, 25000), 2)
            support_tickets_open = np.random.randint(0, 3)
            profile_completeness = np.random.randint(60, 100)
            account_age_days = np.random.randint(30, 730)
            product_count = np.random.randint(2, 20)
            revenue_last_30d = round(np.random.uniform(3000, 50000), 2)
            negative_review_pct = round(np.random.uniform(0, 0.15), 2)
            login_frequency_weekly = round(np.random.uniform(2, 14), 2)
            avg_session_minutes = round(np.random.uniform(5, 45), 2)

        # Add some noise to make it realistic
        days_since_last_login = max(0, days_since_last_login + np.random.randint(-3, 3))
        login_count_30d = max(0, login_count_30d + np.random.randint(-2, 2))

        data.append({
            "days_since_last_login": days_since_last_login,
            "login_count_30d": login_count_30d,
            "total_orders": total_orders,
            "avg_order_value": avg_order_value,
            "support_tickets_open": support_tickets_open,
            "profile_completeness": profile_completeness,
            "account_age_days": account_age_days,
            "product_count": product_count,
            "revenue_last_30d": revenue_last_30d,
            "negative_review_pct": negative_review_pct,
            "login_frequency_weekly": login_frequency_weekly,
            "avg_session_minutes": avg_session_minutes,
            "is_churned": int(is_churned),
        })

    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, "churn_training.csv")
    df.to_csv(path, index=False)
    print(f"  [OK] Saved {len(df)} rows -> {path}")
    print(f"  Churn rate: {df['is_churned'].mean():.1%}")
    return df


# ============================================================
# 2. FRAUD TRAINING DATA (5000 orders)
# ============================================================
def generate_fraud_data(n=5000):
    """
    Features that indicate fraud:
    - order_amount: unusually high
    - bo_account_age_days: very new accounts
    - bo_total_orders: first-time or few orders
    - order_hour: odd hours (2-5 AM)
    - title_length: very short or generic
    - has_notes: no notes = suspicious
    - bo_avg_order_value: huge deviation from average
    - time_since_last_order_hours: rapid successive orders
    - payment_status: unpaid orders
    - status_changes_count: too many status changes
    """
    print("Generating fraud_training.csv (5000 orders)...")

    data = []
    for i in range(n):
        # 8% fraud rate (realistic for e-commerce)
        is_fraud = np.random.random() < 0.08

        if is_fraud:
            # Fraud pattern
            order_amount = round(np.random.uniform(20000, 150000), 2)
            bo_account_age_days = np.random.randint(1, 30)
            bo_total_orders = np.random.randint(1, 3)
            order_hour = np.random.choice([1, 2, 3, 4, 5, 23], p=[0.15, 0.25, 0.25, 0.2, 0.1, 0.05])
            title_length = np.random.randint(5, 20)
            has_notes = np.random.random() < 0.2
            bo_avg_order_value = round(np.random.uniform(1000, 5000), 2)
            amount_deviation = round(order_amount / max(bo_avg_order_value, 1), 2)
            time_since_last_order_hours = np.random.randint(0, 12)
            is_payment_unpaid = np.random.random() < 0.7
            status_changes_count = np.random.randint(3, 10)
            items_count = np.random.randint(1, 2)
            is_first_order = np.random.random() < 0.6
        else:
            # Legitimate order pattern
            order_amount = round(np.random.uniform(1000, 50000), 2)
            bo_account_age_days = np.random.randint(30, 730)
            bo_total_orders = np.random.randint(3, 50)
            order_hour = np.random.randint(8, 22)
            title_length = np.random.randint(20, 80)
            has_notes = np.random.random() < 0.7
            bo_avg_order_value = round(order_amount * np.random.uniform(0.5, 1.5), 2)
            amount_deviation = round(order_amount / max(bo_avg_order_value, 1), 2)
            time_since_last_order_hours = np.random.randint(24, 720)
            is_payment_unpaid = np.random.random() < 0.15
            status_changes_count = np.random.randint(1, 4)
            items_count = np.random.randint(1, 10)
            is_first_order = np.random.random() < 0.05

        data.append({
            "order_amount": order_amount,
            "bo_account_age_days": bo_account_age_days,
            "bo_total_orders": bo_total_orders,
            "order_hour": order_hour,
            "title_length": title_length,
            "has_notes": int(has_notes),
            "bo_avg_order_value": bo_avg_order_value,
            "amount_deviation": amount_deviation,
            "time_since_last_order_hours": time_since_last_order_hours,
            "is_payment_unpaid": int(is_payment_unpaid),
            "status_changes_count": status_changes_count,
            "items_count": items_count,
            "is_first_order": int(is_first_order),
            "is_fraud": int(is_fraud),
        })

    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, "fraud_training.csv")
    df.to_csv(path, index=False)
    print(f"  [OK] Saved {len(df)} rows -> {path}")
    print(f"  Fraud rate: {df['is_fraud'].mean():.1%}")
    return df


# ============================================================
# 3. ANOMALY TRAINING DATA (5000 transactions)
# ============================================================
def generate_anomaly_data(n=5000):
    """
    Features for Isolation Forest (unsupervised, but we label for evaluation):
    - amount: transaction amount
    - amount_zscore: how far from user's average
    - transaction_hour: time of day
    - bo_avg_transaction: user's typical amount
    - bo_transaction_count: how many transactions user has
    - days_since_last_transaction: gap between transactions
    - is_weekend: weekend transactions
    - amount_to_balance_ratio: amount vs current balance
    """
    print("Generating anomaly_training.csv (5000 transactions)...")

    tx_types = ["Sale", "MaterialPurchase", "Refund", "Fee", "Payout"]
    type_weights = [50, 25, 10, 10, 5]
    data = []

    for i in range(n):
        # 5% anomaly rate
        is_anomaly = np.random.random() < 0.05
        tx_type = np.random.choice(tx_types, p=[w/100 for w in type_weights])

        if tx_type == "Sale":
            base_amount = np.random.uniform(500, 15000)
        elif tx_type == "MaterialPurchase":
            base_amount = np.random.uniform(200, 5000)
        elif tx_type == "Refund":
            base_amount = np.random.uniform(100, 3000)
        elif tx_type == "Fee":
            base_amount = np.random.uniform(50, 500)
        else:
            base_amount = np.random.uniform(1000, 10000)

        if is_anomaly:
            # Anomaly: amount is 5-20x normal
            amount = round(base_amount * np.random.uniform(5, 20), 2)
            transaction_hour = np.random.choice([0, 1, 2, 3, 4, 5])
            days_since_last = np.random.randint(0, 2)
        else:
            amount = round(base_amount, 2)
            transaction_hour = np.random.randint(6, 23)
            days_since_last = np.random.randint(1, 30)

        bo_avg_transaction = round(base_amount * np.random.uniform(0.7, 1.3), 2)
        amount_zscore = round((amount - bo_avg_transaction) / max(bo_avg_transaction * 0.3, 1), 2)
        bo_transaction_count = np.random.randint(5, 200)
        balance = round(np.random.uniform(1000, 50000), 2)
        amount_to_balance = round(amount / max(balance, 1), 4)
        is_weekend = int(np.random.random() < 0.28)  # ~28% chance
        tx_type_encoded = tx_types.index(tx_type)

        data.append({
            "amount": amount,
            "amount_zscore": amount_zscore,
            "transaction_hour": transaction_hour,
            "bo_avg_transaction": bo_avg_transaction,
            "bo_transaction_count": bo_transaction_count,
            "days_since_last_transaction": days_since_last,
            "is_weekend": is_weekend,
            "amount_to_balance_ratio": amount_to_balance,
            "tx_type": tx_type_encoded,
            "is_anomaly": int(is_anomaly),
        })

    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, "anomaly_training.csv")
    df.to_csv(path, index=False)
    print(f"  [OK] Saved {len(df)} rows -> {path}")
    print(f"  Anomaly rate: {df['is_anomaly'].mean():.1%}")
    return df


# ============================================================
# 4. DEMAND FORECASTING DATA (time series per product)
# ============================================================
def generate_demand_data(n_products=12, n_weeks=52):
    """
    Weekly sales time series for each product.
    Features:
    - product_id
    - week_start: date
    - units_sold: target variable
    - avg_price: average selling price that week
    - promotion_active: was there a promotion
    - season: seasonal factor (Eid, summer, etc.)
    - views_count: product views that week
    """
    print(f"Generating demand_training.csv ({n_products} products x {n_weeks} weeks)...")

    data = []
    base_date = datetime.now() - timedelta(weeks=n_weeks)

    # Egyptian seasonal patterns
    seasonal_multipliers = {
        1: 0.8,   # January - post-holiday dip
        2: 0.85,  # February
        3: 1.0,   # March - spring
        4: 1.1,   # April - Ramadan prep
        5: 1.3,   # May - Eid al-Fitr (peak)
        6: 1.2,   # June - summer start
        7: 1.15,  # July - summer
        8: 1.0,   # August
        9: 0.9,   # September - back to school
        10: 1.0,  # October
        11: 1.1,  # November
        12: 1.25, # December - year end / holidays
    }

    for pid in range(1, n_products + 1):
        # Each product has a base demand level
        base_demand = np.random.randint(5, 40)
        base_price = np.random.uniform(100, 400)
        trend = np.random.uniform(-0.05, 0.15)  # slight upward trend for most

        for week in range(n_weeks):
            week_start = base_date + timedelta(weeks=week)
            month = week_start.month

            # Seasonal + trend + noise
            seasonal = seasonal_multipliers[month]
            trend_factor = 1 + (trend * week / n_weeks)
            noise = np.random.normal(1, 0.15)
            promotion = int(np.random.random() < 0.1)  # 10% chance of promotion
            promo_boost = 1.4 if promotion else 1.0

            units_sold = max(0, int(base_demand * seasonal * trend_factor * noise * promo_boost))
            avg_price = round(base_price * np.random.uniform(0.85, 1.15), 2)
            if promotion:
                avg_price = round(avg_price * 0.8, 2)  # 20% discount
            views = int(units_sold * np.random.uniform(8, 25))

            data.append({
                "product_id": pid,
                "week_start": week_start.strftime("%Y-%m-%d"),
                "week_number": week + 1,
                "month": month,
                "units_sold": units_sold,
                "avg_price": avg_price,
                "promotion_active": promotion,
                "seasonal_factor": seasonal,
                "views_count": views,
            })

    df = pd.DataFrame(data)
    path = os.path.join(OUTPUT_DIR, "demand_training.csv")
    df.to_csv(path, index=False)
    print(f"  [OK] Saved {len(df)} rows -> {path}")
    print(f"  Products: {n_products}, Weeks: {n_weeks}")
    return df


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  Talentree AI - Training Data Generator")
    print("  Generating CSV files for offline ML training")
    print("=" * 60)

    churn_df = generate_churn_data(5000)
    fraud_df = generate_fraud_data(5000)
    anomaly_df = generate_anomaly_data(5000)
    demand_df = generate_demand_data(12, 52)

    print("\n" + "=" * 60)
    print("  [OK] ALL TRAINING DATA GENERATED!")
    print(f"  Total rows: {len(churn_df) + len(fraud_df) + len(anomaly_df) + len(demand_df)}")
    print("=" * 60)
    print("\nFiles saved to:")
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".csv"):
            size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
            print(f"  {f:30s} {size/1024:.1f} KB")


if __name__ == "__main__":
    main()
