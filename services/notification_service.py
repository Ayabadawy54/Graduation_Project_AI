"""Notification service — AI-triggered notifications."""


THRESHOLDS = {
    "churn_risk": 0.7,
    "fraud_score": 0.5,
    "low_stock": True,
    "anomaly": True,
    "negative_sentiment": "Negative",
}


def _insert_notification(cursor, user_id, title, message, entity_type=None, entity_id=None):
    # RelatedEntityId is int — safely convert; UUID strings become None
    try:
        rel_id = int(entity_id) if entity_id is not None else None
    except (ValueError, TypeError):
        rel_id = None
    cursor.execute("""
        INSERT INTO Notifications (UserId, Type, Title, Message,
            RelatedEntityType, RelatedEntityId, IsRead, Priority,
            CreatedAt, UpdatedAt, CreatedBy)
        VALUES (?, 0, ?, ?, ?, ?, 0, 1, GETDATE(), GETDATE(), 'AI-Service')
    """, (user_id, title, message, entity_type, rel_id))


def check_and_notify_bo(cursor, bo_user_id: str) -> dict:
    """Check all AI thresholds for a BO and fire notifications if triggered."""
    fired = []

    # 1. Churn Risk
    cursor.execute("SELECT ChurnRiskScore FROM AspNetUsers WHERE Id = ?", (bo_user_id,))
    row = cursor.fetchone()
    if row and row[0] and float(row[0]) >= THRESHOLDS["churn_risk"]:
        _insert_notification(cursor, bo_user_id,
            "High Churn Risk Detected",
            f"Your account churn risk score is {round(float(row[0])*100)}%. Log in regularly and complete your profile to stay active.",
            "User", bo_user_id)
        fired.append("churn_risk")

    # 2. Low Stock Products
    cursor.execute("""
        SELECT p.Id, p.Name FROM Products p
        JOIN BusinessOwnerProfile bop ON bop.Id = p.BusinessOwnerProfileId
        WHERE bop.UserId = ? AND p.LowStockFlag = 1 AND p.IsDeleted = 0
    """, (bo_user_id,))
    low_stock_products = cursor.fetchall()
    for prod in low_stock_products:
        _insert_notification(cursor, bo_user_id,
            "Low Stock Alert",
            f"Product '{prod[1]}' is running low on stock. Consider restocking soon.",
            "Product", prod[0])
        fired.append(f"low_stock_{prod[0]}")

    # 3. Fraud Alerts
    cursor.execute("""
        SELECT Id, Title FROM BoProductionRequests
        WHERE BusinessOwnerId = ? AND IsFraudFlag = 1
        AND Id NOT IN (
            SELECT CAST(RelatedEntityId AS INT) FROM Notifications
            WHERE UserId = ? AND Title = 'Fraud Alert on Request'
            AND RelatedEntityId IS NOT NULL
        )
    """, (bo_user_id, bo_user_id))
    fraud_requests = cursor.fetchall()
    for req in fraud_requests:
        _insert_notification(cursor, bo_user_id,
            "Fraud Alert on Request",
            f"Production request '{req[1]}' has been flagged as potentially fraudulent and is under review.",
            "ProductionRequest", req[0])
        fired.append(f"fraud_{req[0]}")

    # 4. Anomalous Transactions
    cursor.execute("""
        SELECT Id, Amount FROM Transactions
        WHERE BusinessOwnerId = ? AND AnomalyFlag = 1
        AND Id NOT IN (
            SELECT CAST(RelatedEntityId AS INT) FROM Notifications
            WHERE UserId = ? AND Title = 'Unusual Transaction Detected'
            AND RelatedEntityId IS NOT NULL
        )
    """, (bo_user_id, bo_user_id))
    anomalies = cursor.fetchall()
    for tx in anomalies:
        _insert_notification(cursor, bo_user_id,
            "Unusual Transaction Detected",
            f"A transaction of {abs(float(tx[1])):.2f} EGP has been flagged as unusual. Please verify.",
            "Transaction", tx[0])
        fired.append(f"anomaly_tx_{tx[0]}")

    # 5. Negative Reviews
    cursor.execute("""
        SELECT pr.Id, p.Name FROM ProductReviews pr
        JOIN Products p ON p.Id = pr.ProductId
        JOIN BusinessOwnerProfile bop ON bop.Id = p.BusinessOwnerProfileId
        WHERE bop.UserId = ? AND pr.SentimentLabel = 'Negative'
        AND pr.Id NOT IN (
            SELECT CAST(RelatedEntityId AS INT) FROM Notifications
            WHERE UserId = ? AND Title = 'New Negative Review'
            AND RelatedEntityId IS NOT NULL
        )
    """, (bo_user_id, bo_user_id))
    neg_reviews = cursor.fetchall()
    for rev in neg_reviews:
        _insert_notification(cursor, bo_user_id,
            "New Negative Review",
            f"A negative review was posted on '{rev[1]}'. Consider responding to address customer concerns.",
            "Review", rev[0])
        fired.append(f"neg_review_{rev[0]}")

    return {"user_id": bo_user_id, "notifications_fired": len(fired), "types": fired}


def check_and_notify_all(cursor) -> list:
    """Check all BOs and fire notifications."""
    cursor.execute("SELECT UserId FROM BusinessOwnerProfile WHERE IsDeleted=0")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for uid in ids:
        try:
            results.append(check_and_notify_bo(cursor, uid))
        except Exception as e:
            results.append({"user_id": uid, "error": str(e)})
    return results
