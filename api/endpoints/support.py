"""
Support tickets endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.services.data_service import data_service

router = APIRouter()

@router.get("/support-tickets")
async def get_support_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """
    Get support tickets with filters
    """
    tickets_df = data_service.get_support_tickets()
    
    if status:
        tickets_df = tickets_df[tickets_df['status'] == status]
    if priority:
        tickets_df = tickets_df[tickets_df['priority'] == priority]
    
    return tickets_df.head(limit).to_dict(orient='records')

# ⚠️ IMPORTANT: analytics route MUST come before /{ticket_id} to avoid routing conflict
@router.get("/support-tickets/analytics/summary")
async def get_ticket_summary():
    """
    Get support ticket analytics summary
    """
    tickets_df = data_service.get_support_tickets()
    
    total = len(tickets_df)
    by_status = tickets_df.groupby('status').size().to_dict()
    by_priority = tickets_df.groupby('priority').size().to_dict()
    by_category = tickets_df.groupby('category').size().to_dict()
    
    return {
        'total_tickets': total,
        'by_status': by_status,
        'by_priority': by_priority,
        'by_category': by_category
    }

@router.get("/support-tickets/{ticket_id}")
async def get_ticket_detail(ticket_id: str):
    """
    Get ticket details
    """
    tickets_df = data_service.get_support_tickets()
    ticket = tickets_df[tickets_df['ticket_id'] == ticket_id]
    
    if len(ticket) == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket.iloc[0].to_dict()
