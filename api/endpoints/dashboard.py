"""
Dashboard endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service
from api.services.ai_service import ai_service
from api.models.schemas import DashboardOverview, CategoryPerformance

router = APIRouter()

@router.get("/dashboard/overview", response_model=DashboardOverview)
async def get_dashboard_overview():
    """
    Get complete dashboard overview with AI insights
    """
    # Get data
    users_df = data_service.get_users()
    brands_df = data_service.get_brands()
    orders_df = data_service.get_orders()
    products_df = data_service.get_products()
    reviews_df = data_service.get_reviews()
    
    # Calculate metrics
    total_owners = len(users_df[users_df['user_type'] == 'owner'])
    active_owners = len(brands_df[brands_df['total_orders'] > 0])
    total_customers = len(users_df[users_df['user_type'] == 'customer'])
    total_orders = len(orders_df)
    total_revenue = orders_df['total_price_egp'].sum()
    
    # Calculate sales trend (last 7 days vs previous 7 days)
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    now = datetime.now()
    last_7_days = orders_df[orders_df['order_date'] >= now - timedelta(days=7)]
    prev_7_days = orders_df[(orders_df['order_date'] >= now - timedelta(days=14)) & 
                            (orders_df['order_date'] < now - timedelta(days=7))]
    
    last_week_revenue = last_7_days['total_price_egp'].sum()
    prev_week_revenue = prev_7_days['total_price_egp'].sum()
    
    if prev_week_revenue > 0:
        trend_pct = ((last_week_revenue - prev_week_revenue) / prev_week_revenue) * 100
        if trend_pct > 5:
            sales_trend = f"↑ {trend_pct:.1f}%"
        elif trend_pct < -5:
            sales_trend = f"↓ {abs(trend_pct):.1f}%"
        else:
            sales_trend = f"→ {trend_pct:.1f}%"
    else:
        sales_trend = "→ 0%"
    
    # Count high-risk brands
    high_risk_count = 0
    for _, brand in brands_df.iterrows():
        risk_analysis = ai_service.calculate_brand_risk_score(
            brand.to_dict(), orders_df, reviews_df
        )
        if risk_analysis['risk_level'] == 'high':
            high_risk_count += 1
    
    # Pending approvals
    pending_approvals = len(products_df[products_df['status'] == 'pending'])
    
    # AI Recommendations
    recommendations = []
    if high_risk_count > 5:
        recommendations.append(f'{high_risk_count} brands flagged as high-risk - review immediately')
    if pending_approvals > 20:
        recommendations.append(f'{pending_approvals} products awaiting approval - process queue')
    if trend_pct < -10:
        recommendations.append('Sales declining - consider promotional campaign')
    elif trend_pct > 20:
        recommendations.append('Sales surging - ensure vendor stock levels adequate')
    
    if not recommendations:
        recommendations.append('Platform performing normally - no urgent actions')
    
    # Detect anomalies
    anomalies = ai_service.detect_anomalies(orders_df)
    alerts = [
        {'type': a['type'], 'message': a['message'], 'severity': a['severity']}
        for a in anomalies
    ]
    
    if not alerts:
        alerts.append({'type': 'info', 'message': 'No anomalies detected', 'severity': 'info'})
    
    return {
        'total_owners': total_owners,
        'active_owners': active_owners,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue_egp': round(total_revenue, 2),
        'sales_trend': sales_trend,
        'high_risk_brands': high_risk_count,
        'pending_approvals': pending_approvals,
        'top_recommendations': recommendations,
        'alerts': alerts
    }

@router.get("/dashboard/category-performance", response_model=List[CategoryPerformance])
async def get_category_performance():
    """
    Get performance metrics by category
    """
    products_df = data_service.get_products()
    orders_df = data_service.get_orders()
    brands_df = data_service.get_brands()
    
    categories = ['Fashion & Accessories', 'Handmade & Crafts', 'Natural & Beauty']
    results = []
    
    for category in categories:
        # Get category products
        cat_products = products_df[products_df['category'] == category]
        cat_product_ids = cat_products['product_id'].tolist()
        
        # Get category orders
        cat_orders = orders_df[orders_df['product_id'].isin(cat_product_ids)]
        
        # Get category brands
        cat_brands = brands_df[brands_df['category'] == category]
        
        # Calculate metrics
        total_sales = cat_orders['total_price_egp'].sum()
        total_orders = len(cat_orders)
        avg_order_value = cat_orders['total_price_egp'].mean() if len(cat_orders) > 0 else 0
        active_brands = len(cat_brands[cat_brands['total_orders'] > 0])
        
        # Calculate trend (simplified)
        growth_trend = "→ 5%"  # Placeholder - would calculate from historical data
        
        results.append({
            'category': category,
            'total_sales_egp': round(total_sales, 2),
            'total_orders': total_orders,
            'avg_order_value_egp': round(avg_order_value, 2),
            'growth_trend': growth_trend,
            'active_brands': active_brands
        })
    
    return results
