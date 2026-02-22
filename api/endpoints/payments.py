"""
Payments analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta

from api.services.data_service import data_service

router = APIRouter()


@router.get("/payments")
async def get_payments(
    status: Optional[str] = Query(None, description="Filter by status: paid, pending, failed, refunded"),
    method: Optional[str] = Query(None, description="Filter by method: credit_card, cash_on_delivery, wallet, bank_transfer"),
    days: int = Query(30, ge=1, le=365, description="Look-back window in days"),
    limit: int = Query(100, le=500)
):
    """
    List payments with optional filters.
    """
    payments_df = data_service.get_payments()
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])

    # Date filter
    cutoff = datetime.now() - timedelta(days=days)
    payments_df = payments_df[payments_df['payment_date'] >= cutoff]

    if status:
        payments_df = payments_df[payments_df['payment_status'] == status]
    if method:
        payments_df = payments_df[payments_df['payment_method'] == method]

    payments_df['payment_date'] = payments_df['payment_date'].astype(str)
    return payments_df.head(limit).to_dict(orient='records')


@router.get("/payments/analytics/summary")
async def get_payment_summary():
    """
    Payment analytics: revenue by method, success rate, totals.
    """
    payments_df = data_service.get_payments()

    total_transactions = len(payments_df)
    total_revenue = payments_df[payments_df['payment_status'] == 'paid']['amount_egp'].sum()
    paid_count = len(payments_df[payments_df['payment_status'] == 'paid'])
    failed_count = len(payments_df[payments_df['payment_status'] == 'failed'])
    pending_count = len(payments_df[payments_df['payment_status'] == 'pending'])
    refunded_count = len(payments_df[payments_df['payment_status'] == 'refunded'])

    success_rate = round(paid_count / total_transactions * 100, 2) if total_transactions > 0 else 0

    # Revenue by payment method
    by_method = (
        payments_df[payments_df['payment_status'] == 'paid']
        .groupby('payment_method')['amount_egp']
        .agg(['sum', 'count', 'mean'])
        .reset_index()
    )
    by_method.columns = ['method', 'total_revenue_egp', 'transaction_count', 'avg_amount_egp']
    by_method['total_revenue_egp'] = by_method['total_revenue_egp'].round(2)
    by_method['avg_amount_egp'] = by_method['avg_amount_egp'].round(2)

    # Transactions by status
    by_status = payments_df.groupby('payment_status').size().to_dict()

    return {
        'total_transactions': total_transactions,
        'total_revenue_egp': round(total_revenue, 2),
        'success_rate_pct': success_rate,
        'by_status': {
            'paid': paid_count,
            'failed': failed_count,
            'pending': pending_count,
            'refunded': refunded_count
        },
        'by_method': by_method.to_dict(orient='records')
    }


@router.get("/payments/analytics/trends")
async def get_payment_trends(days: int = Query(30, ge=7, le=180)):
    """
    Daily payment volume and revenue over the past N days.
    """
    payments_df = data_service.get_payments()
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])

    cutoff = datetime.now() - timedelta(days=days)
    recent = payments_df[payments_df['payment_date'] >= cutoff]

    daily = recent.groupby(recent['payment_date'].dt.date).agg(
        transactions=('payment_id', 'count'),
        revenue_egp=('amount_egp', lambda x: x[payments_df.loc[x.index, 'payment_status'] == 'paid'].sum()),
        failed=('payment_status', lambda x: (x == 'failed').sum())
    ).reset_index()

    daily.columns = ['date', 'transactions', 'revenue_egp', 'failed']
    daily['date'] = daily['date'].astype(str)
    daily['revenue_egp'] = daily['revenue_egp'].round(2)

    return daily.to_dict(orient='records')


@router.get("/payments/{payment_id}")
async def get_payment_detail(payment_id: str):
    """
    Get single payment detail by ID.
    """
    payments_df = data_service.get_payments()
    match = payments_df[payments_df['payment_id'] == payment_id]

    if len(match) == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = match.iloc[0].to_dict()
    # Get linked order info if available
    orders_df = data_service.get_orders()
    order = orders_df[orders_df['order_id'] == result.get('order_id')]
    if len(order) > 0:
        result['order_status'] = order.iloc[0]['status']
        result['order_total_egp'] = order.iloc[0]['total_price_egp']

    return result
