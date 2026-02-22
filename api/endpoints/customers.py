"""
Customers & Users management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service
from api.services.ai_service import ai_service

router = APIRouter()


# =============================================================
# USER MANAGEMENT (all users: owners + customers)
# =============================================================

@router.get("/users")
async def get_all_users(
    user_type: Optional[str] = Query(None, description="Filter: 'customer' or 'owner'"),
    governorate: Optional[str] = Query(None),
    limit: int = Query(50, le=500)
):
    """
    List all platform users (owners + customers) with optional filters.
    """
    users_df = data_service.get_users(user_type=user_type)
    if governorate:
        users_df = users_df[users_df['governorate'] == governorate]
    return users_df.head(limit).to_dict(orient='records')


@router.get("/users/analytics/overview")
async def get_users_overview():
    """
    Users analytics: totals, growth trend, breakdown by type and governorate.
    """
    users_df = data_service.get_users()
    users_df['created_at'] = pd.to_datetime(users_df['created_at'])

    now = datetime.now()
    this_month = users_df[users_df['created_at'] >= datetime(now.year, now.month, 1)]
    last_month_start = (datetime(now.year, now.month, 1) - timedelta(days=1)).replace(day=1)
    last_month = users_df[
        (users_df['created_at'] >= last_month_start) &
        (users_df['created_at'] < datetime(now.year, now.month, 1))
    ]

    growth_pct = 0
    if len(last_month) > 0:
        growth_pct = round((len(this_month) - len(last_month)) / len(last_month) * 100, 1)

    by_type = users_df['user_type'].value_counts().to_dict()
    by_governorate = users_df['governorate'].value_counts().head(10).to_dict() if 'governorate' in users_df.columns else {}

    # Monthly signup trend (last 6 months)
    monthly = users_df.groupby(users_df['created_at'].dt.to_period('M')).size().reset_index(name='new_users')
    monthly['created_at'] = monthly['created_at'].astype(str)
    monthly = monthly.tail(6)

    return {
        'total_users': len(users_df),
        'by_type': by_type,
        'this_month_signups': len(this_month),
        'last_month_signups': len(last_month),
        'growth_pct': growth_pct,
        'top_governorates': by_governorate,
        'monthly_signup_trend': monthly.to_dict(orient='records')
    }


@router.put("/users/{user_id}/status")
async def update_user_status(user_id: str, action: str = Query(..., description="'suspend' or 'activate'")):
    """
    Suspend or activate a user account.
    In MVP this returns a success response (no live DB write).
    """
    users_df = data_service.get_users()
    user = users_df[users_df['user_id'] == user_id]

    if len(user) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    if action not in ['suspend', 'activate']:
        raise HTTPException(status_code=400, detail="Action must be 'suspend' or 'activate'")

    user_data = user.iloc[0].to_dict()
    return {
        'success': True,
        'user_id': user_id,
        'user_type': user_data.get('user_type'),
        'action': action,
        'message': f"User {user_id} has been {'suspended' if action == 'suspend' else 'activated'}.",
        'note': 'State is logged — connect to DB for persistence.'
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """
    Soft-delete a user (marks as deleted — does not remove from dataset in MVP).
    """
    users_df = data_service.get_users()
    user = users_df[users_df['user_id'] == user_id]

    if len(user) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.iloc[0].to_dict()
    return {
        'success': True,
        'user_id': user_id,
        'user_type': user_data.get('user_type'),
        'message': f"User {user_id} marked for deletion.",
        'note': 'Soft delete — connect to DB for persistence.'
    }


# =============================================================
# CUSTOMERS (existing endpoints — static routes BEFORE /{id})
# =============================================================

@router.get("/customers")
async def get_customers(
    governorate: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Get list of customers with AI-based segmentation.
    """
    customers_df = data_service.get_users(user_type='customer')

    if governorate:
        customers_df = customers_df[customers_df['governorate'] == governorate]

    orders_df = data_service.get_orders()

    customers_list = []
    for _, customer in customers_df.head(limit).iterrows():
        customer_dict = customer.to_dict()
        customer_orders = orders_df[orders_df['customer_user_id'] == customer['user_id']]
        segment = ai_service.segment_customer(customer_orders, customer_dict)
        customer_dict['segment'] = segment
        customer_dict['total_orders'] = len(customer_orders)
        customer_dict['total_spent_egp'] = round(customer_orders['total_price_egp'].sum(), 2)
        customers_list.append(customer_dict)

    return customers_list


# ⚠️ Static analytics route MUST come before /{customer_id}
@router.get("/customers/analytics/segments")
async def get_customer_segments():
    """
    Get customer segmentation distribution.
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


@router.get("/customers/{customer_id}")
async def get_customer_detail(customer_id: str):
    """
    Get detailed customer information with orders and AI segment.
    """
    users_df = data_service.get_users()
    customer = users_df[users_df['user_id'] == customer_id]

    if len(customer) == 0:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer_dict = customer.iloc[0].to_dict()

    orders_df = data_service.get_orders()
    customer_orders = orders_df[orders_df['customer_user_id'] == customer_id]

    total_orders = len(customer_orders)
    total_spent = customer_orders['total_price_egp'].sum()
    avg_order_value = customer_orders['total_price_egp'].mean() if total_orders > 0 else 0
    segment = ai_service.segment_customer(customer_orders, customer_dict)

    return {
        **customer_dict,
        'total_orders': total_orders,
        'total_spent_egp': round(total_spent, 2),
        'avg_order_value_egp': round(avg_order_value, 2),
        'segment': segment
    }
