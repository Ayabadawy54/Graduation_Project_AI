"""
Generate all 10 comprehensive Jupyter notebooks for TalentTree Admin Dashboard
"""
import nbformat as nbf
import os


def create_notebook(title, cells_list):
    """Helper to create notebook with given cells"""
    nb = nbf.v4.new_notebook()
    nb['cells'] = cells_list
    return nb


def save_notebook(nb, filename):
    """Save notebook to file"""
    filepath = f'notebooks/{filename}'
    with open(filepath, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f'[OK] Created: {filename}')


# Import and style cells (reusable)
def get_import_cell():
    return nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')
plt.rcParams['figure.figsize'] = (14, 6)

print('[OK] Libraries loaded successfully')""")


def main():
    print("\n" + "="*70)
    print("[NOTEBOOK GENERATOR] CREATING ALL 10 JUPYTER NOTEBOOKS")
    print("="*70 + "\n")
    
    # Create notebooks directory
    os.makedirs('notebooks', exist_ok=True)
    
    print("Generating notebooks...\n")
    
    # 1. EXECUTIVE DASHBOARD
    exec_cells = [
        nbf.v4.new_markdown_cell("""# Executive Dashboard
## Platform Overview & Key Metrics
**Date:** 2026-02-01 | **Author:** AI Team"""),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## 1. Load Data"),
        nbf.v4.new_code_cell("""users_df = pd.read_csv('../mock_data/users.csv', encoding='utf-8-sig')
brands_df = pd.read_csv('../mock_data/brands.csv', encoding='utf-8-sig')
products_df = pd.read_csv('../mock_data/products.csv', encoding='utf-8-sig')
orders_df = pd.read_csv('../mock_data/orders.csv', encoding='utf-8-sig')
payments_df = pd.read_csv('../mock_data/payments.csv', encoding='utf-8-sig')
reviews_df = pd.read_csv('../mock_data/reviews.csv', encoding='utf-8-sig')

orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
print(f'[DATA] Loaded: {len(users_df)} users, {len(brands_df)} brands, {len(products_df)} products, {len(orders_df)} orders')"""),
        nbf.v4.new_markdown_cell("## 2. Key Performance Indicators"),
        nbf.v4.new_code_cell("""total_revenue = orders_df['total_price_egp'].sum()
avg_order_value = orders_df['total_price_egp'].mean()
active_brands = len(brands_df[brands_df['total_orders'] > 0])

print('='*70)
print('PLATFORM KEY PERFORMANCE INDICATORS')
print('='*70)
print(f'Total Revenue: {total_revenue:,.2f} EGP')
print(f'Average Order Value: {avg_order_value:,.2f} EGP')
print(f'Active Brands: {active_brands}')
print(f'Total Orders: {len(orders_df):,}')
print(f'Average Rating: {reviews_df["rating"].mean():.2f}/5.0')
print('='*70)"""),
        nbf.v4.new_markdown_cell("## 3. Revenue by Category"),
        nbf.v4.new_code_cell("""orders_with_cat = orders_df.merge(products_df[['product_id', 'category']], on='product_id', how='left')
cat_revenue = orders_with_cat.groupby('category')['total_price_egp'].sum().sort_values(ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
cat_revenue.plot(kind='pie', ax=ax1, autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Revenue Distribution', fontsize=14, fontweight='bold')
ax1.set_ylabel('')

cat_revenue.plot(kind='barh', ax=ax2, color=colors)
ax2.set_title('Revenue by Category', fontsize=14, fontweight='bold')
for i, v in enumerate(cat_revenue.values):
    ax2.text(v, i, f' {v:,.0f} EGP', va='center', fontweight='bold')

plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Executive Dashboard", exec_cells), '01_executive_dashboard.ipynb')
    
    # 2. OWNER ANALYTICS  
    owner_cells = [
        nbf.v4.new_markdown_cell("# Owner Analytics\n## Brand Performance & Risk Analysis"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""brands_df = pd.read_csv('../mock_data/brands.csv', encoding='utf-8-sig')
print(f'Total Brands: {len(brands_df)}')"""),
        nbf.v4.new_markdown_cell("## Top Brands by Revenue"),
        nbf.v4.new_code_cell("""top_brands = brands_df.nlargest(10, 'total_sales_egp')

plt.figure(figsize=(12, 8))
plt.barh(range(len(top_brands)), top_brands['total_sales_egp'], color='#4ECDC4')
plt.yticks(range(len(top_brands)), top_brands['business_name'])
plt.xlabel('Total Sales (EGP)')
plt.title('Top 10 Brands', fontsize=16, fontweight='bold')
plt.gca().invert_yaxis()

for i, v in enumerate(top_brands['total_sales_egp'].values):
    plt.text(v, i, f' {v:,.0f} EGP', va='center')

plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Owner Analytics", owner_cells), '02_owner_analytics.ipynb')
    
    # 3. PRODUCT PERFORMANCE
    product_cells = [
        nbf.v4.new_markdown_cell("# Product Performance\n## Product Analytics & Trends"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""products_df = pd.read_csv('../mock_data/products.csv', encoding='utf-8-sig')
print(f'Total Products: {len(products_df)}')"""),
        nbf.v4.new_markdown_cell("## Product Status"),
        nbf.v4.new_code_cell("""status_counts = products_df['status'].value_counts()

plt.figure(figsize=(10, 6))
colors = {'approved': '#6BCF7F', 'pending': '#FFD93D', 'rejected': '#FF6B6B'}
bar_colors = [colors.get(s, '#CCC') for s in status_counts.index]

bars = plt.bar(status_counts.index, status_counts.values, color=bar_colors)
plt.title('Product Status Distribution', fontsize=14, fontweight='bold')
plt.ylabel('Count')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}', 
             ha='center', va='bottom', fontweight='bold')

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Product Performance", product_cells), '03_product_performance.ipynb')
    
    # 4. CUSTOMER INSIGHTS
    customer_cells = [
        nbf.v4.new_markdown_cell("# Customer Insights\n## Customer Behavior & Segmentation"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""users_df = pd.read_csv('../mock_data/users.csv', encoding='utf-8-sig')
orders_df = pd.read_csv('../mock_data/orders.csv', encoding='utf-8-sig')

customers_df = users_df[users_df['user_type'] == 'customer']
print(f'Total Customers: {len(customers_df)}')"""),
        nbf.v4.new_markdown_cell("## Customer Distribution by Governorate"),
        nbf.v4.new_code_cell("""gov_dist = customers_df['governorate'].value_counts().head(15)

plt.figure(figsize=(12, 8))
plt.barh(range(len(gov_dist)), gov_dist.values, color='#4ECDC4')
plt.yticks(range(len(gov_dist)), gov_dist.index)
plt.xlabel('Number of Customers')
plt.title('Top 15 Governorates', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()

for i, v in enumerate(gov_dist.values):
    plt.text(v, i, f' {int(v)}', va='center')

plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Customer Insights", customer_cells), '04_customer_insights.ipynb')
    
    # 5. GEOGRAPHIC ANALYSIS
    geo_cells = [
        nbf.v4.new_markdown_cell("# Geographic Analysis\n## Egyptian Market Distribution"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""orders_df = pd.read_csv('../mock_data/orders.csv', encoding='utf-8-sig')
print(f'Total Orders: {len(orders_df)}')"""),
        nbf.v4.new_markdown_cell("## Orders by Governorate"),
        nbf.v4.new_code_cell("""gov_stats = orders_df.groupby('shipping_governorate').agg({
    'order_id': 'count',
    'total_price_egp': 'sum'
}).reset_index().sort_values('order_id', ascending=False).head(15)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

ax1.barh(range(len(gov_stats)), gov_stats['order_id'], color='#FF6B6B')
ax1.set_yticks(range(len(gov_stats)))
ax1.set_yticklabels(gov_stats['shipping_governorate'])
ax1.set_title('Top 15 by Orders', fontsize=14, fontweight='bold')
ax1.invert_yaxis()

ax2.barh(range(len(gov_stats)), gov_stats['total_price_egp'], color='#4ECDC4')
ax2.set_yticks(range(len(gov_stats)))
ax2.set_yticklabels(gov_stats['shipping_governorate'])
ax2.set_title('Top 15 by Revenue', fontsize=14, fontweight='bold')
ax2.invert_yaxis()

plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Geographic Analysis", geo_cells), '05_geographic_analysis.ipynb')
    
    # 6. AI MODELS PERFORMANCE
    ai_cells = [
        nbf.v4.new_markdown_cell("# AI Models Performance\n## Model Evaluation & Insights"),
        nbf.v4.new_code_cell("""import pandas as pd
import matplotlib.pyplot as plt
import json
import os

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 6)
print('[OK] Libraries loaded')"""),
        nbf.v4.new_markdown_cell("## Load AI Model Metadata"),
        nbf.v4.new_code_cell("""models = {}
files = ['owner_risk_model_metadata.json', 'sentiment_analyzer_metadata.json', 
         'sales_forecaster_metadata.json', 'churn_predictor_metadata.json',
         'fraud_detector_metadata.json']

for file in files:
    path = f'../ai_models/{file}'
    if os.path.exists(path):
        with open(path, 'r') as f:
            models[file.replace('_metadata.json', '')] = json.load(f)
        print(f'[OK] {file}')

print(f'\\nLoaded {len(models)} models')"""),
        nbf.v4.new_markdown_cell("## Sentiment Analysis Results"),
        nbf.v4.new_code_cell("""try:
    sentiment_df = pd.read_csv('../ai_models/sentiment_analysis_results.csv')
    sentiment_dist = sentiment_df['sentiment'].value_counts()
    
    plt.figure(figsize=(10, 6))
    colors = {'positive': '#6BCF7F', 'neutral': '#FFD93D', 'negative': '#FF6B6B'}
    bar_colors = [colors[s] for s in sentiment_dist.index]
    
    bars = plt.bar(sentiment_dist.index, sentiment_dist.values, color=bar_colors)
    plt.title('Review Sentiment Distribution', fontsize=14, fontweight='bold')
    plt.ylabel('Count')
    
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h, f'{int(h)}', 
                ha='center', va='bottom', fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
except:
    print('[WARN] Sentiment results not found')""")
    ]
    save_notebook(create_notebook("AI Models Performance", ai_cells), '06_ai_models_performance.ipynb')
    
    # 7. FINANCIAL ANALYSIS
    finance_cells = [
        nbf.v4.new_markdown_cell("# Financial Analysis\n## Revenue, Payments & Financial Metrics"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""orders_df = pd.read_csv('../mock_data/orders.csv', encoding='utf-8-sig')
payments_df = pd.read_csv('../mock_data/payments.csv', encoding='utf-8-sig')
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
print(f'Total Orders: {len(orders_df)}')"""),
        nbf.v4.new_markdown_cell("## Payment Methods"),
        nbf.v4.new_code_cell("""payment_dist = payments_df['payment_method'].value_counts()

plt.figure(figsize=(10, 6))
colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6BCF7F']
payment_dist.plot(kind='pie', autopct='%1.1f%%', colors=colors, startangle=90)
plt.title('Payment Methods Distribution', fontsize=14, fontweight='bold')
plt.ylabel('')
plt.tight_layout()
plt.show()""")
    ]
    save_notebook(create_notebook("Financial Analysis", finance_cells), '07_financial_analysis.ipynb')
    
    # 8. QUALITY CONTROL
    quality_cells = [
        nbf.v4.new_markdown_cell("# Quality Control\n## Product Approvals & Review Analysis"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""products_df = pd.read_csv('../mock_data/products.csv', encoding='utf-8-sig')
reviews_df = pd.read_csv('../mock_data/reviews.csv', encoding='utf-8-sig')
print(f'Products: {len(products_df)}, Reviews: {len(reviews_df)}')"""),
        nbf.v4.new_markdown_cell("## Review Rating Distribution"),
        nbf.v4.new_code_cell("""rating_dist = reviews_df['rating'].value_counts().sort_index()

plt.figure(figsize=(10, 6))
colors_rating = {1: '#FF6B6B', 2: '#FFA07A', 3: '#FFD93D', 4: '#90EE90', 5: '#6BCF7F'}
bar_colors = [colors_rating[r] for r in rating_dist.index]

bars = plt.bar(rating_dist.index, rating_dist.values, color=bar_colors)
plt.title('Review Rating Distribution', fontsize=14, fontweight='bold')
plt.xlabel('Rating')
plt.ylabel('Count')

for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., h, f'{int(h)}', 
            ha='center', va='bottom', fontweight='bold')

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()

print(f'Average Rating: {reviews_df["rating"].mean():.2f}/5.0')""")
    ]
    save_notebook(create_notebook("Quality Control", quality_cells), '08_quality_control.ipynb')
    
    # 9. SEASONAL ANALYSIS
    seasonal_cells = [
        nbf.v4.new_markdown_cell("# Seasonal Patterns\n## Time-based Analysis & Trends"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Load Data"),
        nbf.v4.new_code_cell("""orders_df = pd.read_csv('../mock_data/orders.csv', encoding='utf-8-sig')
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
orders_df['hour'] = orders_df['order_date'].dt.hour
orders_df['day_of_week'] = orders_df['order_date'].dt.day_name()
print(f'Total Orders: {len(orders_df)}')"""),
        nbf.v4.new_markdown_cell("## Orders by Hour"),
        nbf.v4.new_code_cell("""hourly = orders_df['hour'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
plt.plot(hourly.index, hourly.values, marker='o', linewidth=2, markersize=8, color='#4ECDC4')
plt.title('Orders by Hour of Day', fontsize=14, fontweight='bold')
plt.xlabel('Hour')
plt.ylabel('Orders')
plt.xticks(range(24))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print(f'Peak Hour: {hourly.idxmax()}:00 ({hourly.max()} orders)')""")
    ]
    save_notebook(create_notebook("Seasonal Analysis", seasonal_cells), '09_seasonal_analysis.ipynb')
    
    # 10. PREDICTIONS DASHBOARD
    pred_cells = [
        nbf.v4.new_markdown_cell("# Predictions Dashboard\n## AI-Powered Forecasts & Recommendations"),
        get_import_cell(),
        nbf.v4.new_markdown_cell("## Sales Forecast"),
        nbf.v4.new_code_cell("""try:
    forecast_df = pd.read_csv('../ai_models/sales_forecast_7day.csv')
    
    plt.figure(figsize=(14, 6))
    x = range(len(forecast_df))
    
    plt.plot(x, forecast_df['predicted_orders'], marker='o', linewidth=3,
             markersize=10, label='Predicted Orders', color='#4ECDC4')
    
    plt.fill_between(x, forecast_df['confidence_low'], forecast_df['confidence_high'],
                     alpha=0.3, color='#4ECDC4', label='95% Confidence')
    
    plt.title('7-Day Sales Forecast', fontsize=16, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Predicted Orders')
    plt.xticks(x, forecast_df['date'], rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print('7-Day Forecast:')
    for _, row in forecast_df.iterrows():
        print(f'  {row["date"]}: {row["predicted_orders"]} orders')
except:
    print('[WARN] Forecast not available')"""),
        nbf.v4.new_markdown_cell("## AI Recommendations"),
        nbf.v4.new_code_cell("""print('='*70)
print('AI-POWERED RECOMMENDATIONS')
print('='*70)
print('1. Monitor peak hours (8-11 PM) for support staffing')
print('2. Focus marketing on top-performing categories')
print('3. Target high-value customer segments')
print('4. Optimize inventory based on demand forecasts')
print('='*70)""")
    ]
    save_notebook(create_notebook("Predictions Dashboard", pred_cells), '10_predictions_dashboard.ipynb')
    
    print("\n" + "="*70)
    print("[SUCCESS] ALL 10 NOTEBOOKS GENERATED!")
    print("="*70)
    print("\nGenerated Notebooks:")
    print("   01. Executive Dashboard")
    print("   02. Owner Analytics")
    print("   03. Product Performance")
    print("   04. Customer Insights")
    print("   05. Geographic Analysis")
    print("   06. AI Models Performance")
    print("   07. Financial Analysis")
    print("   08. Quality Control")
    print("   09. Seasonal Analysis")
    print("   10. Predictions Dashboard")
    print("\nTo open notebooks:")
    print("   cd notebooks")
    print("   jupyter notebook")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
