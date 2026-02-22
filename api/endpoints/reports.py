"""
Reports generation endpoints
"""
from fastapi import APIRouter, HTTPException, Query
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service
from api.services.ai_service import ai_service

router = APIRouter()


@router.get("/reports/monthly")
async def get_monthly_report(
    year: int = Query(None, description="Year (e.g. 2026). Defaults to current year."),
    month: int = Query(None, ge=1, le=12, description="Month number 1-12. Defaults to current month.")
):
    """
    Full monthly report: revenue, orders, top brands, top products, new users.
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1)
    else:
        month_end = datetime(year, month + 1, 1)

    orders_df = data_service.get_orders()
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    month_orders = orders_df[(orders_df['order_date'] >= month_start) & (orders_df['order_date'] < month_end)]

    users_df = data_service.get_users()
    users_df['created_at'] = pd.to_datetime(users_df['created_at'])
    new_customers = len(users_df[
        (users_df['user_type'] == 'customer') &
        (users_df['created_at'] >= month_start) &
        (users_df['created_at'] < month_end)
    ])

    brands_df = data_service.get_brands()
    new_brands = len(brands_df[
        (pd.to_datetime(brands_df['created_at']) >= month_start) &
        (pd.to_datetime(brands_df['created_at']) < month_end)
    ])

    products_df = data_service.get_products()
    products_df['created_at'] = pd.to_datetime(products_df['created_at'])
    new_products = len(products_df[
        (products_df['created_at'] >= month_start) &
        (products_df['created_at'] < month_end)
    ])

    # Top 5 brands by orders
    top_brands_raw = month_orders.groupby('brand_id')['total_price_egp'].agg(['sum', 'count']).reset_index()
    top_brands_raw.columns = ['brand_id', 'revenue_egp', 'order_count']
    top_brands_raw = top_brands_raw.nlargest(5, 'revenue_egp')
    brand_names = brands_df.set_index('brand_id')['business_name'].to_dict()
    top_brands_raw['brand_name'] = top_brands_raw['brand_id'].map(brand_names)
    top_brands_raw['revenue_egp'] = top_brands_raw['revenue_egp'].round(2)

    # Top 5 products by order count
    top_products_raw = month_orders.groupby('product_id').size().reset_index(name='order_count')
    top_products_raw = top_products_raw.nlargest(5, 'order_count')
    product_names = products_df.set_index('product_id')['name'].to_dict()
    top_products_raw['product_name'] = top_products_raw['product_id'].map(product_names)

    # Order status breakdown
    status_breakdown = month_orders.groupby('status').size().to_dict()

    return {
        'period': f"{year}-{month:02d}",
        'month_start': month_start.strftime('%Y-%m-%d'),
        'month_end': (month_end - timedelta(days=1)).strftime('%Y-%m-%d'),
        'metrics': {
            'total_orders': len(month_orders),
            'total_revenue_egp': round(month_orders['total_price_egp'].sum(), 2),
            'avg_order_value_egp': round(month_orders['total_price_egp'].mean(), 2) if len(month_orders) > 0 else 0,
            'new_customers': new_customers,
            'new_brands': new_brands,
            'new_products': new_products
        },
        'order_status_breakdown': status_breakdown,
        'top_brands': top_brands_raw[['brand_id', 'brand_name', 'revenue_egp', 'order_count']].to_dict(orient='records'),
        'top_products': top_products_raw[['product_id', 'product_name', 'order_count']].to_dict(orient='records')
    }


@router.get("/reports/brands/{brand_id}")
async def get_brand_report(brand_id: str):
    """
    Per-brand performance report: orders, revenue, ratings, risk, top products.
    """
    brand = data_service.get_brand_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    orders_df = data_service.get_orders()
    reviews_df = data_service.get_reviews()
    products_df = data_service.get_products()

    brand_orders = orders_df[orders_df['brand_id'] == brand_id]
    brand_products = products_df[products_df['brand_id'] == brand_id]
    brand_reviews = reviews_df[reviews_df['brand_id'] == brand_id] if 'brand_id' in reviews_df.columns else pd.DataFrame()

    # Risk analysis
    risk = ai_service.calculate_brand_risk_score(brand, orders_df, reviews_df)

    # Order status
    status_breakdown = brand_orders.groupby('status').size().to_dict()

    # Monthly revenue trend (last 6 months)
    brand_orders = brand_orders.copy()
    brand_orders['order_date'] = pd.to_datetime(brand_orders['order_date'])
    monthly = brand_orders.groupby(brand_orders['order_date'].dt.to_period('M')).agg(
        orders=('order_id', 'count'),
        revenue=('total_price_egp', 'sum')
    ).reset_index()
    monthly['order_date'] = monthly['order_date'].astype(str)
    monthly['revenue'] = monthly['revenue'].round(2)

    # Top products
    top_products = brand_products.nlargest(5, 'sales_count')[['product_id', 'name', 'price_egp', 'sales_count', 'stock_quantity']]

    return {
        'brand_id': brand_id,
        'business_name': brand['business_name'],
        'category': brand['category'],
        'verified': brand['verified'],
        'created_at': brand['created_at'],
        'performance': {
            'total_orders': len(brand_orders),
            'total_revenue_egp': round(brand_orders['total_price_egp'].sum(), 2),
            'avg_order_value_egp': round(brand_orders['total_price_egp'].mean(), 2) if len(brand_orders) > 0 else 0,
            'avg_rating': brand.get('avg_rating', 0),
            'total_products': len(brand_products),
            'active_products': len(brand_products[brand_products['status'] == 'approved'])
        },
        'risk': {
            'risk_score': risk['risk_score'],
            'risk_level': risk['risk_level'],
            'risk_factors': risk['risk_factors']
        },
        'order_status_breakdown': status_breakdown,
        'monthly_trend': monthly.to_dict(orient='records'),
        'top_products': top_products.to_dict(orient='records')
    }


@router.get("/reports/export/summary")
async def get_export_summary():
    """
    Platform-wide structured summary for frontend PDF/Excel generation.
    Contains all key metrics in one response.
    """
    users_df = data_service.get_users()
    brands_df = data_service.get_brands()
    orders_df = data_service.get_orders()
    products_df = data_service.get_products()
    payments_df = data_service.get_payments()

    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    now = datetime.now()
    this_month_orders = orders_df[orders_df['order_date'] >= datetime(now.year, now.month, 1)]

    return {
        'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
        'platform_summary': {
            'total_users': len(users_df),
            'total_owners': len(users_df[users_df['user_type'] == 'owner']),
            'total_customers': len(users_df[users_df['user_type'] == 'customer']),
            'total_brands': len(brands_df),
            'verified_brands': int(brands_df['verified'].sum()),
            'total_products': len(products_df),
            'approved_products': len(products_df[products_df['status'] == 'approved']),
            'total_orders': len(orders_df),
            'total_revenue_egp': round(orders_df['total_price_egp'].sum(), 2),
            'total_payments': len(payments_df),
            'successful_payments': len(payments_df[payments_df['payment_status'] == 'paid'])
        },
        'this_month': {
            'orders': len(this_month_orders),
            'revenue_egp': round(this_month_orders['total_price_egp'].sum(), 2)
        },
        'categories': products_df['category'].value_counts().to_dict(),
        'order_status_breakdown': orders_df['status'].value_counts().to_dict(),
        'payment_method_breakdown': payments_df['payment_method'].value_counts().to_dict()
    }
