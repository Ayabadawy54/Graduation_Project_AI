"""
Orders management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service
from api.services.ai_service import ai_service
from api.models.schemas import OrderForecast

router = APIRouter()

@router.get("/orders")
async def get_orders(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """
    Get orders with filters
    """
    orders_df = data_service.get_orders(status=status)
    
    # Date filtering
    if date_from or date_to:
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        if date_from:
            orders_df = orders_df[orders_df['order_date'] >= pd.to_datetime(date_from)]
        if date_to:
            orders_df = orders_df[orders_df['order_date'] <= pd.to_datetime(date_to)]
    
    orders_list = orders_df.head(limit).to_dict(orient='records')
    return orders_list

@router.get("/orders/{order_id}")
async def get_order_detail(order_id: str):
    """
    Get detailed order information
    """
    orders_df = data_service.get_orders()
    order = orders_df[orders_df['order_id'] == order_id]
    
    if len(order) == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_dict = order.iloc[0].to_dict()
    
    # Get product info
    product = data_service.get_product_by_id(order_dict['product_id'])
    
    # Get customer info
    users_df = data_service.get_users()
    customer = users_df[users_df['user_id'] == order_dict['customer_user_id']]
    
    return {
        **order_dict,
        'product_name': product['name'] if product else 'Unknown',
        'customer_name': customer.iloc[0]['full_name'] if len(customer) > 0 else 'Unknown'
    }

@router.get("/orders/analytics/forecast", response_model=List[OrderForecast])
async def get_order_forecast(
    days: int = Query(7, ge=1, le=30),
    category: Optional[str] = Query(None)
):
    """
    Forecast order volume for next N days
    """
    orders_df = data_service.get_orders()
    
    forecast = ai_service.forecast_orders(orders_df, days=days, category=category)
    
    return forecast

@router.get("/orders/analytics/late-fulfillment")
async def get_late_fulfillment_risk():
    """
    Identify orders at risk of late delivery
    """
    orders_df = data_service.get_orders()
    
    # Get processing orders
    processing = orders_df[orders_df['status'] == 'processing'].copy()
    processing['order_date'] = pd.to_datetime(processing['order_date'])
    
    # Calculate days since order
    now = pd.Timestamp.now()
    processing['days_since_order'] = (now - processing['order_date']).dt.days
    
    # Flag if > 5 days in processing
    at_risk = processing[processing['days_since_order'] > 5]
    
    at_risk_list = at_risk[['order_id', 'brand_id', 'customer_user_id', 'days_since_order']].to_dict(orient='records')
    
    for order in at_risk_list:
        order['risk_level'] = 'high' if order['days_since_order'] > 7 else 'medium'
        order['recommendation'] = 'Contact brand immediately' if order['days_since_order'] > 7 else 'Monitor closely'
    
    return at_risk_list

@router.get("/orders/analytics/by-governorate")
async def get_orders_by_governorate():
    """
    Get order distribution by Egyptian governorate
    """
    orders_df = data_service.get_orders()
    
    # Group by governorate
    by_gov = orders_df.groupby('shipping_governorate').agg({
        'order_id': 'count',
        'total_price_egp': 'sum'
    }).reset_index()
    
    by_gov.columns = ['governorate', 'total_orders', 'total_revenue_egp']
    by_gov['total_revenue_egp'] = by_gov['total_revenue_egp'].round(2)
    
    # Sort by orders
    by_gov = by_gov.sort_values('total_orders', ascending=False)
    
    return by_gov.to_dict(orient='records')

@router.get("/orders/analytics/anomalies")
async def get_order_anomalies():
    """
    Detect unusual order patterns
    """
    orders_df = data_service.get_orders()
    
    anomalies = ai_service.detect_anomalies(orders_df)
    
    return {
        'anomalies': anomalies,
        'total_detected': len(anomalies)
    }
