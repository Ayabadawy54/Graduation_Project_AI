"""
TalentTree Mock Data Generator - ENGLISH VERSION
Generates realistic Egyptian data with English names and creative brand names
Author: AI Engineering Team
Date: January 2026
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import json
import os

# Initialize Faker
fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ============================================
# EGYPTIAN CONTEXT DATA - ENGLISH
# ============================================

EGYPTIAN_GOVERNORATES = [
    'Cairo', 'Giza', 'Alexandria', 'Dakahlia', 'Sharqia',
    'Qalyubia', 'Kafr El Sheikh', 'Gharbia', 'Monufia', 'Beheira',
    'Ismailia', 'Port Said', 'Suez', 'North Sinai', 'South Sinai',
    'Faiyum', 'Beni Suef', 'Minya', 'Asyut', 'Sohag',
    'Qena', 'Luxor', 'Aswan', 'Red Sea', 'New Valley',
    'Matrouh', 'Damietta'
]

EGYPTIAN_CITIES = {
    'Cairo': ['Nasr City', 'Maadi', 'Zamalek', 'Heliopolis', 'Downtown', 'Mokattam', 'New Cairo', 'Shorouk', 'Helwan', 'Matariya'],
    'Giza': ['Haram', 'Faisal', 'Mohandessin', 'Dokki', '6th October', 'Sheikh Zayed', 'Pyramids Gardens', 'Imbaba'],
    'Alexandria': ['Montaza', 'Moharam Bek', 'Sidi Gaber', 'Asafra', 'Borg El Arab', 'Smouha', 'Ibrahimia'],
    'Dakahlia': ['Mansoura', 'Mit Ghamr', 'Dekernes', 'Belqas'],
    'Sharqia': ['Zagazig', 'Bilbeis', 'Faqus', 'Hehia'],
    'Qalyubia': ['Banha', 'Shubra El Kheima', 'Qaha', 'Qalyub'],
}

EGYPTIAN_FIRST_NAMES = [
    # Male
    'Mohamed', 'Ahmed', 'Ali', 'Hassan', 'Mostafa', 'Khaled', 'Omar', 'Youssef',
    'Karim', 'Abdullah', 'Mahmoud', 'Tarek', 'Yasser', 'Hisham', 'Waleed', 'Rami',
    'Amr', 'Adam', 'Ziad', 'Seif', 'Yezen', 'Ibrahim', 'Hussein', 'Amir',
    # Female
    'Fatma', 'Aisha', 'Mariam', 'Nour', 'Sara', 'Yasmin', 'Hoda', 'Malak',
    'Dina', 'Heba', 'Rana', 'Lama', 'Nada', 'Jana', 'Aya', 'Salma',
    'Reem', 'Doaa', 'Amal', 'Noha', 'Mona', 'Israa', 'Shimaa', 'Rawan'
]

EGYPTIAN_LAST_NAMES = [
    'Mahmoud', 'Ibrahim', 'Abdullah', 'Hassan', 'Elsayed', 'Abdelaziz',
    'Elshafei', 'Elmassry', 'Eldeen', 'Fouad', 'Ramadan', 'Osman',
    'Saleh', 'Abdelrahman', 'Gamal', 'Kamel', 'Fathy', 'Said',
    'Ali', 'Hussein', 'Mansour', 'Omar', 'Youssef', 'Khalil'
]

# ============================================
# CREATIVE MODERN BRAND NAMES BY CATEGORY
# ============================================

# Fashion & Accessories - Creative Modern Names
FASHION_BRANDS = [
    'Chic Cairo', 'Style Studio', 'Fashion Hub', 'Trendy Vibes', 'Urban Chic',
    'Cairo Threads', 'Modern Muse', 'Elegance Co', 'Style Craft', 'Vogue Egypt',
    'Luxe Boutique', 'Fashion Forward', 'Style Box', 'Trend Setter', 'Glam House',
    'Elite Fashion', 'Mode Studio', 'Style Lab', 'Fashion Nest', 'Chic & Unique',
    'Bella Mode', 'Style Avenue', 'Fashion Loft', 'Trend House', 'Classy Cairo'
]

# Handmade & Crafts - Creative Artisan Names
HANDMADE_BRANDS = [
    'Artisan Workshop', 'Craft Studio', 'Handmade Cairo', 'Creative Hands', 'Art & Craft Co',
    'The Maker Space', 'Crafted Cairo', 'Artisan Hub', 'Made with Love', 'Craft Lab',
    'Hands On Studio', 'Creative Corner', 'The Artisan', 'Craft Haven', 'Art House',
    'Maker Studio', 'Handmade Haven', 'Craft Masters', 'Creative Studio', 'Artisan Alley',
    'The Workshop', 'Craft & Create', 'Handmade Hub', 'Art Craft Studio', 'Creative Makers'
]

# Natural & Beauty - Modern Wellness Names
BEAUTY_BRANDS = [
    'Pure Glow', 'Natural Beauty', 'Essence Egypt', 'Glow Lab', 'Beauty Botanics',
    'Skin Secrets', 'Nature Care', 'Organic Glow', 'Herbal Beauty', 'Pure Essence',
    'Cairo Glow', 'Natural House', 'Beauty Studio', 'Skin Lab', 'Glow & Grow',
    'Nature\'s Touch', 'Radiant Skin', 'Botanical Beauty', 'Pure Naturals', 'Glow Studio',
    'Herbal Essence', 'Skin Revival', 'Natural Radiance', 'Beauty Bloom', 'Pure Beauty Co'
]

PRODUCT_CATEGORIES = [
    'Fashion & Accessories',
    'Handmade & Crafts',
    'Natural & Beauty'
]

# ============================================
# PRODUCTS BY CATEGORY - CREATIVE NAMES
# ============================================

# Fashion & Accessories Products
FASHION_PRODUCTS = [
    'Leather Tote Bag', 'Silver Hoop Earrings', 'Silk Scarf', 'Statement Necklace',
    'Leather Wallet', 'Crossbody Bag', 'Gold Bracelet', 'Fashion Ring',
    'Boho Bag', 'Vintage Earrings', 'Trendy Belt', 'Chic Clutch',
    'Designer Sunglasses', 'Pearl Necklace', 'Classic Watch', 'Leather Belt',
    'Beaded Bracelet', 'Chain Necklace', 'Stud Earrings', 'Woven Bag'
]

# Handmade & Crafts Products
HANDMADE_PRODUCTS = [
    'Hand-painted Canvas', 'Ceramic Vase', 'Wooden Box', 'Handmade Candle',
    'Macrame Wall Hanging', 'Pottery Bowl', 'Woven Basket', 'Decorative Cushion',
    'Art Print', 'Boho Cushion', 'Vintage Frame', 'Craft Decor',
    'Hand-knitted Blanket', 'Clay Pot', 'Wooden Sculpture', 'Embroidered Pillow',
    'Handmade Journal', 'Ceramic Plate', 'Wicker Storage', 'Fabric Wall Art'
]

# Natural & Beauty Products
BEAUTY_PRODUCTS = [
    'Organic Face Cream', 'Natural Soap Bar', 'Body Butter', 'Hair Oil',
    'Face Serum', 'Lip Balm', 'Body Scrub', 'Essential Oil Blend',
    'Glow Serum', 'Natural Moisturizer', 'Herbal Shampoo', 'Beauty Oil',
    'Clay Face Mask', 'Rose Water Toner', 'Argan Oil', 'Coffee Body Scrub',
    'Shea Butter Cream', 'Natural Deodorant', 'Hair Conditioner', 'Hand Cream'
]

# Raw Materials
RAW_MATERIALS = [
    'Egyptian Cotton Fabric', 'Natural Silk', 'Genuine Leather', 'Wool Yarn',
    'Glass Beads', 'Embroidery Thread', 'Beech Wood', 'Raw Clay', 'Pottery Clay',
    'Essential Oils', 'Natural Wax', 'Medicinal Herbs', 'Natural Clay', 'Shea Butter',
    'Raw Silver', 'Copper Wire', 'Palm Leaves', 'Seashells', 'Jute Rope'
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_egyptian_phone():
    """Generate Egyptian phone number: +20 1XX XXX XXXX"""
    prefix = random.choice(['010', '011', '012', '015'])
    number = f"+20 {prefix} {random.randint(100,999)} {random.randint(1000,9999)}"
    return number

def generate_egyptian_name():
    """Generate full Egyptian name"""
    first = random.choice(EGYPTIAN_FIRST_NAMES)
    last = random.choice(EGYPTIAN_LAST_NAMES)
    return f"{first} {last}"

def generate_email(name):
    """Generate email from name"""
    username = name.lower().replace(' ', '.').replace('\'', '')
    domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'])
    return f"{username}@{domain}"

def random_date(start_date, end_date):
    """Generate random date between two dates"""
    time_between = end_date - start_date
    days_between = time_between.days
    if days_between <= 0:
        return start_date
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)

def is_ramadan(date):
    """Check if date is during Ramadan (approximation)"""
    ramadan_periods = [
        (datetime(2024, 3, 11), datetime(2024, 4, 9)),
        (datetime(2025, 2, 28), datetime(2025, 3, 29)),
        (datetime(2026, 2, 17), datetime(2026, 3, 18))
    ]
    
    for start, end in ramadan_periods:
        if start <= date <= end:
            return True
    return False

def get_city_for_governorate(governorate):
    """Get random city for a governorate"""
    if governorate in EGYPTIAN_CITIES:
        return random.choice(EGYPTIAN_CITIES[governorate])
    else:
        return fake.city()

# ============================================
# TABLE 1: USERS
# ============================================

def generate_users(n_owners=100, n_customers=500):
    """Generate users table (owners + customers)"""
    print("Generating users table...")
    
    users = []
    user_id = 1
    
    # Generate Owners
    for i in range(n_owners):
        created = random_date(datetime(2024, 1, 1), datetime(2026, 1, 20))
        name = generate_egyptian_name()
        governorate = random.choice(EGYPTIAN_GOVERNORATES)
        
        user = {
            'user_id': f'USER{user_id:05d}',
            'user_type': 'owner',
            'full_name': name,
            'email': generate_email(name),
            'phone': generate_egyptian_phone(),
            'governorate': governorate,
            'city': get_city_for_governorate(governorate),
            'address': fake.street_address(),
            'created_at': created.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': (created + timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': random.choice([True] * 9 + [False]),
            'is_verified': random.choice([True] * 7 + [False] * 3),
            'national_id_verified': random.choice([True, False]),
        }
        users.append(user)
        user_id += 1
    
    # Generate Customers
    for i in range(n_customers):
        created = random_date(datetime(2024, 3, 1), datetime(2026, 1, 25))
        name = generate_egyptian_name()
        governorate = random.choice(EGYPTIAN_GOVERNORATES)
        
        user = {
            'user_id': f'USER{user_id:05d}',
            'user_type': 'customer',
            'full_name': name,
            'email': generate_email(name),
            'phone': generate_egyptian_phone(),
            'governorate': governorate,
            'city': get_city_for_governorate(governorate),
            'address': fake.street_address(),
            'created_at': created.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': (created + timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'is_active': random.choice([True] * 95 + [False] * 5),
            'is_verified': True,
            'national_id_verified': False,
        }
        users.append(user)
        user_id += 1
    
    df = pd.DataFrame(users)
    df.to_csv('mock_data/users.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} users ({n_owners} owners + {n_customers} customers)")
    return df

# ============================================
# TABLE 2: BRANDS
# ============================================

def generate_brands(users_df):
    """Generate brands table (business profiles for owners)"""
    print("Generating brands table...")
    
    owners = users_df[users_df['user_type'] == 'owner']
    brands = []
    
    # Assign categories evenly
    categories = PRODUCT_CATEGORIES * (len(owners) // 3 + 1)
    random.shuffle(categories)
    
    for idx, (i, owner) in enumerate(owners.iterrows()):
        created = datetime.strptime(owner['created_at'], '%Y-%m-%d %H:%M:%S')
        category = categories[idx]
        
        # Select brand name based on category
        if category == 'Fashion & Accessories':
            business_name = random.choice(FASHION_BRANDS)
        elif category == 'Handmade & Crafts':
            business_name = random.choice(HANDMADE_BRANDS)
        else:  # Natural & Beauty
            business_name = random.choice(BEAUTY_BRANDS)
        
        brand = {
            'brand_id': f'BRAND{idx:04d}',
            'owner_user_id': owner['user_id'],
            'business_name': business_name,
            'category': category,
            'bio': fake.text(max_nb_chars=200),
            'logo_url': f"https://cdn.talentree.eg/brands/logo_{idx}.jpg",
            'cover_image_url': f"https://cdn.talentree.eg/brands/cover_{idx}.jpg",
            'social_facebook': f"fb.com/{business_name.lower().replace(' ', '')}",
            'social_instagram': f"@{business_name.lower().replace(' ', '_')}",
            'created_at': created.strftime('%Y-%m-%d %H:%M:%S'),
            'verified': random.choice([True] * 7 + [False] * 3),
            'profile_complete': random.choice([True] * 8 + [False] * 2),
            'total_sales_egp': round(random.uniform(500, 50000), 2),
            'total_orders': random.randint(5, 500),
            'avg_rating': round(random.uniform(3.0, 5.0), 1),
            'rating_count': random.randint(0, 200),
        }
        brands.append(brand)
    
    df = pd.DataFrame(brands)
    df.to_csv('mock_data/brands.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} brands")
    return df

# ============================================
# TABLE 3: PRODUCTS
# ============================================

def generate_products(brands_df, n=500):
    """Generate products table"""
    print("Generating products table...")
    
    products = []
    
    for i in range(n):
        brand = brands_df.sample(1).iloc[0]
        category = brand['category']
        
        # Select product name based on category
        if category == 'Fashion & Accessories':
            product_name = random.choice(FASHION_PRODUCTS)
        elif category == 'Handmade & Crafts':
            product_name = random.choice(HANDMADE_PRODUCTS)
        else:  # Natural & Beauty
            product_name = random.choice(BEAUTY_PRODUCTS)
        
        created = random_date(
            datetime.strptime(brand['created_at'], '%Y-%m-%d %H:%M:%S'),
            datetime(2026, 1, 25)
        )
        
        product = {
            'product_id': f'PROD{i:05d}',
            'brand_id': brand['brand_id'],
            'name': product_name,
            'category': category,
            'description': fake.text(max_nb_chars=200),
            'price_egp': round(random.uniform(50, 2000), 2),
            'stock_quantity': random.randint(0, 100),
            'sku': f"SKU{random.randint(10000, 99999)}",
            'images': json.dumps([f"img{j}.jpg" for j in range(random.randint(1, 5))]),
            'created_at': created.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': (created + timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'status': random.choice(['approved'] * 85 + ['pending'] * 10 + ['rejected'] * 5),
            'views': random.randint(10, 5000),
            'clicks': random.randint(5, 1000),
            'favorites': random.randint(0, 300),
            'sales_count': random.randint(0, 200),
        }
        products.append(product)
    
    df = pd.DataFrame(products)
    df.to_csv('mock_data/products.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} products")
    return df

# ============================================
# TABLE 4: STATIC VENDORS
# ============================================

def generate_static_vendors(n=10):
    """Generate static vendors for raw materials"""
    print("Generating static_vendors table...")
    
    vendors = []
    vendor_companies = [
        'Cairo Supplies Co', 'Egypt Materials Ltd', 'Nile Trading', 'Delta Fabrics',
        'Alexandria Imports', 'Egyptian Cotton Co', 'Pharaoh Materials', 'Giza Supplies',
        'Mediterranean Trading', 'Cairo Craft Materials'
    ]
    
    for i in range(n):
        contact_name = generate_egyptian_name()
        
        vendor = {
            'vendor_id': f'VEND{i:03d}',
            'name': vendor_companies[i] if i < len(vendor_companies) else f"{fake.company()} Supplies",
            'contact_person': contact_name,
            'phone': generate_egyptian_phone(),
            'email': generate_email(contact_name),
            'governorate': random.choice(EGYPTIAN_GOVERNORATES[:10]),  # Major cities
            'address': fake.street_address(),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'fulfillment_rate': round(random.uniform(0.85, 1.0), 2),
            'avg_delivery_days': random.randint(2, 10),
            'total_materials': random.randint(5, 20),
            'created_at': random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).strftime('%Y-%m-%d %H:%M:%S'),
        }
        vendors.append(vendor)
    
    df = pd.DataFrame(vendors)
    df.to_csv('mock_data/static_vendors.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} vendors")
    return df

# ============================================
# TABLE 5: RAW MATERIAL MARKETPLACE
# ============================================

def generate_raw_materials(vendors_df, n=50):
    """Generate raw materials offered by vendors"""
    print("Generating raw_material_marketplace table...")
    
    materials = []
    
    categories = ['Fabrics', 'Leather & Textiles', 'Beads & Accessories', 'Wood & Clay', 'Oils & Herbs', 'Metals', 'Natural Materials']
    
    for i in range(n):
        vendor = vendors_df.sample(1).iloc[0]
        
        material = {
            'material_id': f'MAT{i:04d}',
            'vendor_id': vendor['vendor_id'],
            'name': random.choice(RAW_MATERIALS),
            'category': random.choice(categories),
            'description': fake.text(max_nb_chars=150),
            'price_per_unit_egp': round(random.uniform(5, 500), 2),
            'unit': random.choice(['meter', 'kg', 'piece', 'liter', 'gram', 'roll']),
            'min_order_quantity': random.randint(1, 10),
            'stock_available': random.randint(0, 1000),
            'image_url': f"https://cdn.talentree.eg/materials/mat_{i}.jpg",
            'created_at': random_date(datetime(2023, 6, 1), datetime(2025, 12, 1)).strftime('%Y-%m-%d %H:%M:%S'),
        }
        materials.append(material)
    
    df = pd.DataFrame(materials)
    df.to_csv('mock_data/raw_material_marketplace.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} raw materials")
    return df

# ============================================
# TABLE 6: MATERIAL REQUESTS
# ============================================

def generate_material_requests(brands_df, materials_df, n=200):
    """Generate material purchase requests from owners"""
    print("Generating material_requests table...")
    
    requests = []
    
    for i in range(n):
        brand = brands_df.sample(1).iloc[0]
        material = materials_df.sample(1).iloc[0]
        
        quantity = random.randint(
            int(material['min_order_quantity']),
            int(material['min_order_quantity']) * 10
        )
        
        order_date = random_date(
            datetime.strptime(brand['created_at'], '%Y-%m-%d %H:%M:%S'),
            datetime(2026, 1, 25)
        )
        
        status = random.choice(['completed'] * 70 + ['processing'] * 20 + ['pending'] * 10)
        
        request = {
            'request_id': f'REQ{i:05d}',
            'brand_id': brand['brand_id'],
            'material_id': material['material_id'],
            'vendor_id': material['vendor_id'],
            'quantity': quantity,
            'total_price_egp': round(quantity * material['price_per_unit_egp'], 2),
            'status': status,
            'request_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'delivery_date': (order_date + timedelta(days=random.randint(3, 14))).strftime('%Y-%m-%d %H:%M:%S') if status == 'completed' else None,
            'notes': fake.sentence() if random.random() > 0.7 else None,
        }
        requests.append(request)
    
    df = pd.DataFrame(requests)
    df.to_csv('mock_data/material_requests.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} material requests")
    return df

# ============================================
# TABLE 7: ORDERS
# ============================================

def generate_orders(users_df, products_df, n=2000):
    """Generate customer orders"""
    print("Generating orders table...")
    
    customers = users_df[users_df['user_type'] == 'customer']
    approved_products = products_df[products_df['status'] == 'approved']
    
    orders = []
    
    for i in range(n):
        customer = customers.sample(1).iloc[0]
        product = approved_products.sample(1).iloc[0]
        
        order_date = random_date(
            max(
                datetime.strptime(customer['created_at'], '%Y-%m-%d %H:%M:%S'),
                datetime.strptime(product['created_at'], '%Y-%m-%d %H:%M:%S')
            ),
            datetime(2026, 1, 27)
        )
        
        # Apply Ramadan boost
        quantity = random.randint(1, 5)
        if is_ramadan(order_date):
            quantity = random.randint(1, 8)  # Higher quantities during Ramadan
        
        # Egyptian shopping patterns: Evening hours (8-11 PM)
        hour = random.choice([8, 9, 10, 11, 20, 21, 22, 23])
        order_date = order_date.replace(hour=hour, minute=random.randint(0, 59))
        
        status = random.choice(['completed'] * 70 + ['shipped'] * 15 + ['processing'] * 10 + ['cancelled'] * 5)
        
        order = {
            'order_id': f'ORD{i:06d}',
            'customer_user_id': customer['user_id'],
            'product_id': product['product_id'],
            'brand_id': product['brand_id'],
            'quantity': quantity,
            'unit_price_egp': product['price_egp'],
            'total_price_egp': round(quantity * product['price_egp'], 2),
            'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'shipping_governorate': customer['governorate'],
            'shipping_city': customer['city'],
            'shipping_address': customer['address'],
            'delivery_date': (order_date + timedelta(days=random.randint(3, 14))).strftime('%Y-%m-%d %H:%M:%S') if status in ['completed', 'shipped'] else None,
        }
        orders.append(order)
    
    df = pd.DataFrame(orders)
    df.to_csv('mock_data/orders.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} orders")
    return df

# ============================================
# TABLE 8: PAYMENTS
# ============================================

def generate_payments(orders_df):
    """Generate payment records for orders"""
    print("Generating payments table...")
    
    payments = []
    
    for idx, order in orders_df.iterrows():
        payment_method = random.choice([
            'cash_on_delivery'] * 60 + 
            ['credit_card'] * 25 + 
            ['vodafone_cash'] * 10 + 
            ['fawry'] * 5
        )
        
        payment_status = 'paid' if order['status'] in ['completed', 'shipped'] else random.choice(['pending', 'processing'])
        
        payment = {
            'payment_id': f'PAY{idx:06d}',
            'order_id': order['order_id'],
            'amount_egp': order['total_price_egp'],
            'payment_method': payment_method,
            'payment_status': payment_status,
            'transaction_id': f"TXN{random.randint(100000, 999999)}" if payment_method != 'cash_on_delivery' else None,
            'payment_date': order['order_date'] if payment_status == 'paid' else None,
            'created_at': order['order_date'],
        }
        payments.append(payment)
    
    df = pd.DataFrame(payments)
    df.to_csv('mock_data/payments.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} payments")
    return df

# ============================================
# TABLE 9: REVIEWS
# ============================================

def generate_reviews(orders_df, n=400):
    """Generate product reviews"""
    print("Generating reviews table...")
    
    completed_orders = orders_df[orders_df['status'] == 'completed']
    
    if len(completed_orders) == 0:
        print("⚠️  No completed orders found for reviews")
        return pd.DataFrame()
    
    reviews = []
    
    positive_reviews = [
        "Great product! Highly recommend. Quality is excellent!",
        "Amazing quality and fast delivery. Will buy again!",
        "Love it! Exactly as described. Very happy with my purchase.",
        "Excellent product and great customer service!",
        "Perfect! Better than expected. Worth every penny.",
    ]
    
    negative_reviews = [
        "Not as described. Disappointed with the quality.",
        "Poor quality. Not worth the price.",
        "Delivery was very late. Product is just okay.",
        "Expected better quality for this price.",
    ]
    
    neutral_reviews = [
        "Product is okay. Nothing special.",
        "Good but expected better. Average quality.",
        "Decent product. Delivery was a bit slow.",
        "It's fine. Meets basic expectations.",
    ]
    
    sample_size = min(n, len(completed_orders))
    
    for i in range(sample_size):
        order = completed_orders.sample(1).iloc[0]
        
        rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 15, 30, 40])[0]
        
        if rating >= 4:
            review_text = random.choice(positive_reviews)
        elif rating <= 2:
            review_text = random.choice(negative_reviews)
        else:
            review_text = random.choice(neutral_reviews)
        
        review_date = datetime.strptime(order['order_date'], '%Y-%m-%d %H:%M:%S') + timedelta(days=random.randint(1, 30))
        
        review = {
            'review_id': f'REV{i:05d}',
            'order_id': order['order_id'],
            'product_id': order['product_id'],
            'customer_user_id': order['customer_user_id'],
            'brand_id': order['brand_id'],
            'rating': rating,
            'review_text': review_text,
            'language': 'english',
            'created_at': review_date.strftime('%Y-%m-%d %H:%M:%S'),
            'helpful_count': random.randint(0, 50),
            'verified_purchase': True,
        }
        reviews.append(review)
    
    df = pd.DataFrame(reviews)
    df.to_csv('mock_data/reviews.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} reviews")
    return df

# ============================================
# TABLE 10: SUPPORT TICKETS
# ============================================

def generate_support_tickets(users_df, orders_df, n=150):
    """Generate customer support tickets"""
    print("Generating support_tickets table...")
    
    ticket_subjects = [
        'Order inquiry', 'Delivery issue', 'Return request',
        'Product question', 'Address change', 'Order cancellation',
        'Product complaint', 'Payment issue', 'Refund request'
    ]
    
    tickets = []
    
    for i in range(n):
        user = users_df.sample(1).iloc[0]
        order = orders_df.sample(1).iloc[0] if random.random() > 0.3 else None
        
        created = random_date(
            datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S'),
            datetime(2026, 1, 27)
        )
        
        status = random.choice(['resolved'] * 60 + ['in_progress'] * 25 + ['pending'] * 15)
        
        ticket = {
            'ticket_id': f'TICKET{i:05d}',
            'user_id': user['user_id'],
            'order_id': order['order_id'] if order is not None else None,
            'subject': random.choice(ticket_subjects),
            'message': fake.text(max_nb_chars=200),
            'category': random.choice(['order_issue', 'product_question', 'delivery', 'payment', 'return', 'general']),
            'priority': random.choice(['low'] * 50 + ['medium'] * 35 + ['high'] * 15),
            'status': status,
            'created_at': created.strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_at': (created + timedelta(hours=random.randint(2, 72))).strftime('%Y-%m-%d %H:%M:%S') if status == 'resolved' else None,
        }
        tickets.append(ticket)
    
    df = pd.DataFrame(tickets)
    df.to_csv('mock_data/support_tickets.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} support tickets")
    return df

# ============================================
# TABLE 11: ADMIN ACTIONS
# ============================================

def generate_admin_actions(products_df, brands_df, tickets_df, n=200):
    """Generate admin activity log"""
    print("Generating admin_actions table...")
    
    admin_users = ['ADMIN001', 'ADMIN002', 'ADMIN003']
    
    actions = []
    
    action_types = [
        'approve_product', 'reject_product', 'verify_brand',
        'suspend_brand', 'resolve_ticket', 'update_product_status'
    ]
    
    for i in range(n):
        action_type = random.choice(action_types)
        
        if 'product' in action_type:
            target = products_df.sample(1).iloc[0]
            target_id = target['product_id']
            target_type = 'product'
        elif 'brand' in action_type:
            target = brands_df.sample(1).iloc[0]
            target_id = target['brand_id']
            target_type = 'brand'
        else:
            target = tickets_df.sample(1).iloc[0]
            target_id = target['ticket_id']
            target_type = 'ticket'
        
        action = {
            'action_id': f'ACT{i:05d}',
            'admin_user_id': random.choice(admin_users),
            'action_type': action_type,
            'target_type': target_type,
            'target_id': target_id,
            'reason': fake.sentence() if random.random() > 0.5 else None,
            'created_at': random_date(datetime(2024, 6, 1), datetime(2026, 1, 27)).strftime('%Y-%m-%d %H:%M:%S'),
        }
        actions.append(action)
    
    df = pd.DataFrame(actions)
    df.to_csv('mock_data/admin_actions.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} admin actions")
    return df

# ============================================
# TABLE 12: ANALYTICS SNAPSHOTS
# ============================================

def generate_analytics_snapshots(orders_df, users_df, brands_df):
    """Generate daily analytics snapshots"""
    print("Generating analytics_snapshots table...")
    
    snapshots = []
    
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2026, 1, 27)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        
        # Orders for this day
        day_orders = orders_df[
            pd.to_datetime(orders_df['order_date']).dt.date == date.date()
        ]
        
        snapshot = {
            'snapshot_id': f"SNAP{date.strftime('%Y%m%d')}",
            'date': date_str,
            'total_orders': len(day_orders),
            'total_revenue_egp': round(day_orders['total_price_egp'].sum(), 2) if len(day_orders) > 0 else 0,
            'new_customers': len(users_df[
                (users_df['user_type'] == 'customer') &
                (pd.to_datetime(users_df['created_at']).dt.date == date.date())
            ]),
            'new_brands': len(brands_df[
                pd.to_datetime(brands_df['created_at']).dt.date == date.date()
            ]),
            'active_customers': random.randint(50, 300),
            'avg_order_value_egp': round(day_orders['total_price_egp'].mean(), 2) if len(day_orders) > 0 else 0,
        }
        snapshots.append(snapshot)
    
    df = pd.DataFrame(snapshots)
    df.to_csv('mock_data/analytics_snapshots.csv', index=False, encoding='utf-8-sig')
    print(f"✅ Generated {len(df)} analytics snapshots")
    return df

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("\n" + "="*60)
    print("🇪🇬 TALENTREE EGYPTIAN MOCK DATA GENERATOR")
    print("="*60 + "\n")
    
    # Create mock_data folder if it doesn't exist
    if not os.path.exists('mock_data'):
        os.makedirs('mock_data')
        print("📁 Created mock_data folder\n")
    
    # Generate all tables in correct order (respecting foreign keys)
    print("Starting data generation...\n")
    
    users_df = generate_users(n_owners=100, n_customers=500)
    brands_df = generate_brands(users_df)
    products_df = generate_products(brands_df, n=500)
    vendors_df = generate_static_vendors(n=10)
    materials_df = generate_raw_materials(vendors_df, n=50)
    requests_df = generate_material_requests(brands_df, materials_df, n=200)
    orders_df = generate_orders(users_df, products_df, n=2000)
    payments_df = generate_payments(orders_df)
    reviews_df = generate_reviews(orders_df, n=400)
    tickets_df = generate_support_tickets(users_df, orders_df, n=150)
    actions_df = generate_admin_actions(products_df, brands_df, tickets_df, n=200)
    snapshots_df = generate_analytics_snapshots(orders_df, users_df, brands_df)
    
    print("\n" + "="*60)
    print("✅ DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   • Users: {len(users_df)}")
    print(f"   • Brands: {len(brands_df)}")
    print(f"   • Products: {len(products_df)}")
    print(f"   • Vendors: {len(vendors_df)}")
    print(f"   • Raw Materials: {len(materials_df)}")
    print(f"   • Material Requests: {len(requests_df)}")
    print(f"   • Orders: {len(orders_df)}")
    print(f"   • Payments: {len(payments_df)}")
    print(f"   • Reviews: {len(reviews_df)}")
    print(f"   • Support Tickets: {len(tickets_df)}")
    print(f"   • Admin Actions: {len(actions_df)}")
    print(f"   • Analytics Snapshots: {len(snapshots_df)}")
    print(f"\n📁 All files saved in: mock_data/")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
