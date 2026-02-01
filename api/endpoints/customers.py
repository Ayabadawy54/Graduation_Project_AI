"""
Customers management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd

from api.services.data_service import data_service
from api.services.ai_service import ai_service

router = APIRouter()

@router.get("/customers")
async def get_customers(
    governorate: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Get list of customers
    """
    customers_df = data_service.get_users(user_type='customer')
    
    if governorate:
        customers_df = customers_df[customers_df['governorate'] == governorate]
    
    orders_df = data_service.get_orders()
    
    # Add segment for each customer
    customers_list = []
    for _, customer in customers_df.head(limit).iterrows():
        customer_dict = customer.to_dict()
        
        # Get customer orders
        customer_orders = orders_df[orders_df['customer_user_id'] == customer['user_id']]
        
        # Segment
        segment = ai_service.segment_customer(customer_orders, customer_dict)
        customer_dict['segment'] = segment
        customer_dict['total_orders'] = len(customer_orders)
        customer_dict['total_spent_egp'] = round(customer_orders['total_price_egp'].sum(), 2)
        
        customers_list.append(customer_dict)
    
    return customers_list

@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str):
    """
    Get detailed customer information
    """
    users_df = data_service.get_users()
    customer = users_df[users_df['user_id'] == customer_id]
    
    if len(customer) == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer_dict = customer.iloc[0].to_dict()
    
    # Get orders
    orders_df = data_service.get_orders()
    customer_orders = orders_df[orders_df['customer_user_id'] == customer_id]
    
    # Calculate metrics
    total_orders = len(customer_orders)
    total_spent = customer_orders['total_price_egp'].sum()
    avg_order_value = customer_orders['total_price_egp'].mean() if total_orders > 0 else 0
    
    # Segment
    segment = ai_service.segment_customer(customer_orders, customer_dict)
    
    return {
        **customer_dict,
        'total_orders': total_orders,
        'total_spent_egp': round(total_spent, 2),
        'avg_order_value_egp': round(avg_order_value, 2),
        'segment': segment
    }

@router.get("/customers/analytics/segments")
async def get_customer_segments():
    """
    Get customer segmentation distribution
    """
    customers_df = data_service.get_users(user_type='customer')
    orders_df = data_service.get_orders()
    
    segments = {'VIP': 0, 'Loyal': 0, 'Occasional': 0, 'New Customer': 0, 'At Risk': 0}
    
    for _, customer in customers_df.iterrows():
        customer_orders = orders_df[orders_df['customer_user_id'] == customer['user_id']]
        segment = ai_service.segment_customer(customer_orders, customer.to_dict())
        segments[segment] = segments.get(segment, 0) + 1
    
    return {
        'segments': [
            {'segment': k, 'count': v, 'percentage': round(v / len(customers_df) * 100, 1)}
            for k, v in segments.items()
        ],
        'total_customers': len(customers_df)
    }
