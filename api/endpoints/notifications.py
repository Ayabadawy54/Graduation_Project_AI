"""
Notifications system endpoints
Notifications are generated dynamically from platform state (no separate CSV needed)
"""
from fastapi import APIRouter, Path
from datetime import datetime

from api.services.data_service import data_service
from api.services.ai_service import ai_service

router = APIRouter()

# In-memory read tracking (resets on restart — acceptable for MVP)
_read_ids: set = set()


def _generate_notifications() -> list:
    """Build notification list from current platform state."""
    notifications = []
    nid = 1

    # Pending product approvals
    products_df = data_service.get_products(status='pending')
    if len(products_df) > 0:
        notifications.append({
            'id': str(nid),
            'type': 'pending_approvals',
            'severity': 'warning' if len(products_df) > 20 else 'info',
            'title': 'Products Awaiting Approval',
            'message': f'{len(products_df)} products are pending admin approval.',
            'action_url': '/api/admin/products/pending-approval',
            'count': len(products_df),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': str(nid) in _read_ids
        })
    nid += 1

    # High-risk brands
    brands_df = data_service.get_brands()
    orders_df = data_service.get_orders()
    reviews_df = data_service.get_reviews()
    high_risk = []
    for _, brand in brands_df.iterrows():
        risk = ai_service.calculate_brand_risk_score(brand.to_dict(), orders_df, reviews_df)
        if risk['risk_level'] == 'high':
            high_risk.append(brand['brand_id'])

    if len(high_risk) > 0:
        notifications.append({
            'id': str(nid),
            'type': 'high_risk_brands',
            'severity': 'error',
            'title': 'High-Risk Brands Detected',
            'message': f'{len(high_risk)} brand(s) flagged as high-risk. Immediate review recommended.',
            'action_url': '/api/admin/brands/analytics/risk-analysis',
            'count': len(high_risk),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': str(nid) in _read_ids
        })
    nid += 1

    # Order anomalies
    anomalies = ai_service.detect_anomalies(orders_df)
    for anomaly in anomalies:
        notifications.append({
            'id': str(nid),
            'type': anomaly['type'],
            'severity': anomaly['severity'],
            'title': 'Order Anomaly Detected',
            'message': anomaly['message'],
            'action_url': '/api/admin/orders',
            'count': 1,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': str(nid) in _read_ids
        })
        nid += 1

    # Low stock alert
    low_stock_count = len(data_service.get_products(status='approved').query('stock_quantity <= 5'))
    if low_stock_count > 0:
        notifications.append({
            'id': str(nid),
            'type': 'low_stock',
            'severity': 'warning',
            'title': 'Critical Low Stock',
            'message': f'{low_stock_count} approved products have 5 or fewer units remaining.',
            'action_url': '/api/admin/inventory/low-stock',
            'count': low_stock_count,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': str(nid) in _read_ids
        })

    return notifications


@router.get("/notifications")
async def get_notifications():
    """
    List all admin notifications generated from current platform state.
    Includes pending approvals, high-risk brands, anomalies, and low-stock alerts.
    """
    all_notifications = _generate_notifications()
    unread_count = sum(1 for n in all_notifications if not n['read'])

    return {
        'total': len(all_notifications),
        'unread': unread_count,
        'notifications': all_notifications
    }


@router.get("/notifications/count")
async def get_notification_count():
    """
    Lightweight endpoint — returns only the unread notification count.
    Use this for the badge/indicator in the frontend navbar.
    """
    all_notifications = _generate_notifications()
    unread = sum(1 for n in all_notifications if not n['read'])
    total = len(all_notifications)

    return {
        'unread': unread,
        'total': total,
        'has_urgent': any(n['severity'] == 'error' for n in all_notifications if not n['read'])
    }


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str = Path(..., description="Notification ID to mark as read")):
    """
    Mark a notification as read. State persists until API restart.
    """
    _read_ids.add(notification_id)
    return {
        'success': True,
        'notification_id': notification_id,
        'message': 'Notification marked as read'
    }
