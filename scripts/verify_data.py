import pandas as pd
import os

files = [
    'users.csv', 'brands.csv', 'products.csv', 'static_vendors.csv', 
    'raw_material_marketplace.csv', 'material_requests.csv', 'orders.csv', 
    'payments.csv', 'reviews.csv', 'support_tickets.csv', 'admin_actions.csv', 
    'analytics_snapshots.csv'
]

print('\n' + '='*70)
print('✅ TALENTREE EGYPTIAN MOCK DATA - GENERATION SUMMARY')
print('='*70 + '\n')

total_rows = 0
for f in files:
    path = f'mock_data/{f}'
    if os.path.exists(path):
        df = pd.read_csv(path)
        rows = len(df)
        size_kb = os.path.getsize(path) / 1024
        total_rows += rows
        print(f'{f:30s} | {rows:6d} rows | {size_kb:7.1f} KB')
    else:
        print(f'{f:30s} | NOT FOUND')

print('\n' + '='*70)
print(f'TOTAL RECORDS GENERATED: {total_rows:,}')
print('='*70 + '\n')

# Show sample data from key tables
print('\n📊 SAMPLE DATA FROM KEY TABLES:\n')

# Users sample
print('👥 USERS (Top 3):')
users_df = pd.read_csv('mock_data/users.csv')
print(users_df[['user_id', 'user_type', 'full_name', 'phone', 'governorate', 'city']].head(3))
print()

# Brands sample
print('🏪 BRANDS (Top 3):')
brands_df = pd.read_csv('mock_data/brands.csv')
print(brands_df[['brand_id', 'business_name', 'category', 'total_sales_egp', 'avg_rating']].head(3))
print()

# Orders sample
print('🛒 ORDERS (Top 3):')
orders_df = pd.read_csv('mock_data/orders.csv')
print(orders_df[['order_id', 'customer_user_id', 'total_price_egp', 'order_date', 'status']].head(3))
print()

print('✅ DATA GENERATION VERIFICATION COMPLETE!')
