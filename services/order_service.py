"""Order service — FulfillmentTimeHours computation."""
from datetime import datetime


def compute_fulfillment_time(cursor, request_id: int) -> dict:
    """Compute fulfillment time in hours for a completed production request."""
    cursor.execute("""
        SELECT Id, CreatedAt, CompletedAt, Status
        FROM BoProductionRequests WHERE Id = ?
    """, (request_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Request not found"}

    rid, created_at, completed_at, status = row
    if status != "Completed" or not completed_at:
        return {"request_id": rid, "skipped": "Not completed yet"}

    hours = round((completed_at - created_at).total_seconds() / 3600, 1)

    cursor.execute("""
        UPDATE BoProductionRequests SET FulfillmentTimeHours = ? WHERE Id = ?
    """, (hours, rid))

    return {"request_id": rid, "fulfillment_hours": hours}


def compute_all_fulfillment(cursor) -> list:
    """Compute fulfillment for all completed requests."""
    cursor.execute("""
        SELECT Id FROM BoProductionRequests
        WHERE Status = 'Completed' AND CompletedAt IS NOT NULL
        AND (FulfillmentTimeHours IS NULL OR FulfillmentTimeHours = 0)
    """)
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for rid in ids:
        try:
            results.append(compute_fulfillment_time(cursor, rid))
        except Exception as e:
            results.append({"request_id": rid, "error": str(e)})
    return results
