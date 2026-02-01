"""
Analytics and reporting endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service
from api.services.ai_service import ai_service

router = APIRouter()

@router.get("/analytics/sales-trends")
async def get_sales_trends(period: int = Query(30, ge=7, le=180)):
    """
    Get sales trends over specified period
    """
    orders_df = data_service.get_orders()
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Filter to period
    cutoff_date = datetime.now() - timedelta(days=period)
    recent_orders = orders_df[orders_df['order_date'] >= cutoff_date]
    
    # Group by date
    daily_sales = recent_orders.groupby(recent_orders['order_date'].dt.date).agg({
        'order_id': 'count',
        'total_price_egp': 'sum'
    }).reset_index()
    
    daily_sales.columns = ['date', 'orders', 'revenue_egp']
    daily_sales['date'] = daily_sales['date'].astype(str)
    daily_sales['revenue_egp'] = daily_sales['revenue_egp'].round(2)
    
    return daily_sales.to_dict(orient='records')

@router.get("/analytics/revenue-breakdown")
async def get_revenue_breakdown():
    """
    Get revenue breakdown by category and governorate
    """
    orders_df = data_service.get_orders()
    products_df = data_service.get_products()
    
    # Merge to get category
    orders_with_category = orders_df.merge(
        products_df[['product_id', 'category']], 
        on='product_id', 
        how='left'
    )
    
    # By category
    by_category = orders_with_category.groupby('category')['total_price_egp'].sum().reset_index()
    by_category.columns = ['category', 'revenue_egp']
    by_category['revenue_egp'] = by_category['revenue_egp'].round(2)
    
    # By governorate
    by_governorate = orders_df.groupby('shipping_governorate')['total_price_egp'].sum().reset_index()
    by_governorate.columns = ['governorate', 'revenue_egp']
    by_governorate['revenue_egp'] = by_governorate['revenue_egp'].round(2)
    by_governorate = by_governorate.sort_values('revenue_egp', ascending=False).head(10)
    
    return {
        'by_category': by_category.to_dict(orient='records'),
        'by_governorate': by_governorate.to_dict(orient='records')
    }

@router.get("/analytics/conversion-funnel")
async def get_conversion_funnel():
    """
    Calculate conversion funnel metrics
    """
    products_df = data_service.get_products()
    
    # Calculate funnel
    total_views = products_df['views'].sum()
    total_clicks = products_df['clicks'].sum()
    total_favorites = products_df['favorites'].sum()
    total_sales = products_df['sales_count'].sum()
    
    view_to_click = (total_clicks / total_views * 100) if total_views > 0 else 0
    click_to_favorite = (total_favorites / total_clicks * 100) if total_clicks > 0 else 0
    click_to_purchase = (total_sales / total_clicks * 100) if total_clicks > 0 else 0
    
    return {
        'total_views': int(total_views),
        'total_clicks': int(total_clicks),
        'total_favorites': int(total_favorites),
        'total_purchases': int(total_sales),
        'view_to_click_rate': round(view_to_click, 2),
        'click_to_favorite_rate': round(click_to_favorite, 2),
        'click_to_purchase_rate': round(click_to_purchase, 2)
    }

@router.get("/analytics/reports/weekly")
async def get_weekly_report():
    """
    Generate automated weekly report
    """
    orders_df = data_service.get_orders()
    users_df = data_service.get_users()
    brands_df = data_service.get_brands()
    products_df = data_service.get_products()
    
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Last 7 days
    now = datetime.now()
    week_start = now - timedelta(days=7)
    this_week = orders_df[orders_df['order_date'] >= week_start]
    
    # Previous 7 days
    prev_week_start = now - timedelta(days=14)
    prev_week = orders_df[(orders_df['order_date'] >= prev_week_start) & (orders_df['order_date'] < week_start)]
    
    # Calculate metrics
    this_week_orders = len(this_week)
    prev_week_orders = len(prev_week)
    orders_change = ((this_week_orders - prev_week_orders) / prev_week_orders * 100) if prev_week_orders > 0 else 0
    
    this_week_revenue = this_week['total_price_egp'].sum()
    prev_week_revenue = prev_week['total_price_egp'].sum()
    revenue_change = ((this_week_revenue - prev_week_revenue) / prev_week_revenue * 100) if prev_week_revenue > 0 else 0
    
    # New users
    users_df['created_at'] = pd.to_datetime(users_df['created_at'])
    new_customers = len(users_df[(users_df['user_type'] == 'customer') & (users_df['created_at'] >= week_start)])
    new_brands = len(brands_df[pd.to_datetime(brands_df['created_at']) >= week_start])
    
    # New products
    products_df['created_at'] = pd.to_datetime(products_df['created_at'])
    new_products = len(products_df[products_df['created_at'] >= week_start])
    
    return {
        'period': f"{week_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
        'metrics': {
            'total_orders': this_week_orders,
            'orders_change_pct': round(orders_change, 1),
            'total_revenue_egp': round(this_week_revenue, 2),
            'revenue_change_pct': round(revenue_change, 1),
            'new_customers': new_customers,
            'new_brands': new_brands,
            'new_products': new_products
        },
        'highlights': [
            f"Orders {abs(orders_change):.1f}% {'up' if orders_change > 0 else 'down'} vs last week",
            f"Revenue {abs(revenue_change):.1f}% {'up' if revenue_change > 0 else 'down'} vs last week",
            f"{new_customers} new customers joined",
            f"{new_brands} new brands registered"
        ]
    }

@router.get("/analytics/category-deep-dive/{category}")
async def get_category_deep_dive(category: str):
    """
    Comprehensive analysis of a specific category
    """
    products_df = data_service.get_products(category=category)
    orders_df = data_service.get_orders()
    brands_df = data_service.get_brands(category=category)
    
    # Get category orders
    cat_product_ids = products_df['product_id'].tolist()
    cat_orders = orders_df[orders_df['product_id'].isin(cat_product_ids)]
    
    # Top products
    top_products = products_df.nlargest(5, 'sales_count')[['product_id', 'name', 'sales_count', 'price_egp']]
    
    # Price analysis
    avg_price = products_df['price_egp'].mean()
    min_price = products_df['price_egp'].min()
    max_price = products_df['price_egp'].max()
    
    # Performance
    total_sales = cat_orders['total_price_egp'].sum()
    total_orders = len(cat_orders)
    
    return {
        'category': category,
        'total_products': len(products_df),
        'total_brands': len(brands_df),
        'total_sales_egp': round(total_sales, 2),
        'total_orders': total_orders,
        'avg_price_egp': round(avg_price, 2),
        'price_range': {
            'min': round(min_price, 2),
            'max': round(max_price, 2)
        },
        'top_products': top_products.to_dict(orient='records')
    }
