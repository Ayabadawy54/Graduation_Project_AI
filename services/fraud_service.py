"""Fraud detection service — scores production requests."""
import pickle
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

def _load_model():
    with open(os.path.join(MODELS_DIR, "fraud_model.pkl"), "rb") as f:
        return pickle.load(f)

def predict_fraud_for_request(cursor, request_id: int) -> dict:
    """Predict fraud risk for a single production request and write to DB."""
    cursor.execute("""
        SELECT r.BusinessOwnerId, r.QuotedPrice, r.CreatedAt, r.Title, r.Notes,
               DATEDIFF(day, u.LockoutEnd, GETDATE()) AS acct_age,
               (SELECT COUNT(*) FROM BoProductionRequests WHERE BusinessOwnerId = r.BusinessOwnerId) AS total_orders,
               DATEPART(HOUR, r.CreatedAt) AS order_hour,
               LEN(r.Title) AS title_length,
               CASE WHEN r.PaymentStatus = 'Unpaid' THEN 1 ELSE 0 END AS is_unpaid
        FROM BoProductionRequests r
        JOIN AspNetUsers u ON u.Id = r.BusinessOwnerId
        WHERE r.Id = ?
    """, (request_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Request not found"}

    bo_id, amount, created_at, title, notes, acct_age, total_orders, order_hour, title_len, is_unpaid = row
    amount = float(amount or 0)

    cursor.execute("""
        SELECT ISNULL(AVG(CAST(QuotedPrice AS FLOAT)), 5000)
        FROM BoProductionRequests
        WHERE BusinessOwnerId = ? AND QuotedPrice IS NOT NULL
    """, (bo_id,))
    avg_val_row = cursor.fetchone()
    bo_avg = float(avg_val_row[0]) if avg_val_row else 5000.0

    amount_dev = round(amount / max(bo_avg, 1), 2)

    # Get time since last order
    cursor.execute("""
        SELECT TOP 1 DATEDIFF(HOUR, CreatedAt, GETDATE())
        FROM BoProductionRequests
        WHERE BusinessOwnerId = ? AND Id != ?
        ORDER BY CreatedAt DESC
    """, (bo_id, request_id))
    gap_row = cursor.fetchone()
    time_since_last = int(gap_row[0]) if gap_row else 720

    features = [[
        amount,
        max(acct_age or 30, 1),
        total_orders or 1,
        order_hour or 10,
        title_len or 30,
        1 if notes else 0,
        bo_avg,
        amount_dev,
        time_since_last,
        is_unpaid or 0,
        1,   # status_changes_count placeholder
        1,   # items_count placeholder
        1 if total_orders <= 1 else 0,
    ]]

    bundle = _load_model()
    X_scaled = bundle["scaler"].transform(features)
    fraud_score = float(bundle["model"].predict_proba(X_scaled)[0][1])
    fraud_score = round(fraud_score, 4)
    is_fraud = 1 if fraud_score >= 0.5 else 0

    cursor.execute("""
        UPDATE BoProductionRequests
        SET FraudScore = ?, IsFraudFlag = ?
        WHERE Id = ?
    """, (fraud_score, is_fraud, request_id))

    return {"request_id": request_id, "fraud_score": fraud_score, "is_fraud": bool(is_fraud)}


def predict_fraud_all(cursor) -> list:
    """Score all production requests."""
    cursor.execute("SELECT Id FROM BoProductionRequests WHERE FraudScore IS NULL OR FraudScore = 0")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for rid in ids:
        try:
            result = predict_fraud_for_request(cursor, rid)
            results.append(result)
        except Exception as e:
            results.append({"request_id": rid, "error": str(e)})
    return results
