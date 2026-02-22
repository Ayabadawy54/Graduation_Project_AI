"""
Admin action logs endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional
import pandas as pd

from api.services.data_service import data_service

router = APIRouter()


@router.get("/admin-actions")
async def get_admin_actions(
    action_type: Optional[str] = Query(None, description="e.g. verify_brand, reject_product, suspend_user"),
    admin_user_id: Optional[str] = Query(None, description="Filter by admin user ID"),
    target_type: Optional[str] = Query(None, description="e.g. brand, product, user"),
    limit: int = Query(100, le=500)
):
    """
    List admin action logs with optional filters.
    """
    actions_df = data_service.get_admin_actions()
    actions_df['created_at'] = pd.to_datetime(actions_df['created_at'])

    if action_type:
        actions_df = actions_df[actions_df['action_type'] == action_type]
    if admin_user_id:
        actions_df = actions_df[actions_df['admin_user_id'] == admin_user_id]
    if target_type:
        actions_df = actions_df[actions_df['target_type'] == target_type]

    # Sort by most recent first
    actions_df = actions_df.sort_values('created_at', ascending=False)
    actions_df['created_at'] = actions_df['created_at'].astype(str)

    return actions_df.head(limit).to_dict(orient='records')


@router.get("/admin-actions/analytics")
async def get_admin_action_analytics():
    """
    Admin actions summary: by action type, by admin user, by target type.
    """
    actions_df = data_service.get_admin_actions()
    actions_df['created_at'] = pd.to_datetime(actions_df['created_at'])

    total = len(actions_df)

    # By action type
    by_action_type = actions_df['action_type'].value_counts().to_dict()

    # By admin user
    by_admin = actions_df.groupby('admin_user_id').agg(
        total_actions=('action_id', 'count'),
        last_action=('created_at', 'max')
    ).reset_index()
    by_admin['last_action'] = by_admin['last_action'].astype(str)

    # By target type
    by_target = actions_df['target_type'].value_counts().to_dict()

    # Monthly activity
    monthly = actions_df.groupby(actions_df['created_at'].dt.to_period('M')).size().reset_index(name='count')
    monthly['created_at'] = monthly['created_at'].astype(str)
    monthly = monthly.tail(6)  # Last 6 months

    return {
        'total_actions': total,
        'by_action_type': by_action_type,
        'by_admin_user': by_admin.to_dict(orient='records'),
        'by_target_type': by_target,
        'monthly_activity': monthly.to_dict(orient='records')
    }
