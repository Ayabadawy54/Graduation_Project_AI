"""Anomaly detection service — flags unusual transactions."""
import pickle
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

def _load_model():
    with open(os.path.join(MODELS_DIR, "anomaly_model.pkl"), "rb") as f:
        return pickle.load(f)

TX_TYPES = ["Sale", "MaterialPurchase", "Refund", "Fee", "Payout"]

def predict_anomaly_for_tx(cursor, tx_id: int) -> dict:
    """Detect if a transaction is anomalous and write result to DB."""
    cursor.execute("""
        SELECT t.BusinessOwnerId, t.Amount, t.Type, t.BalanceAfter,
               DATEPART(HOUR, t.CreatedAt) AS tx_hour,
               DATEDIFF(day, t.CreatedAt, GETDATE()) AS days_ago,
               DATEPART(WEEKDAY, t.CreatedAt) AS weekday
        FROM Transactions t
        WHERE t.Id = ?
    """, (tx_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Transaction not found"}

    bo_id, amount, tx_type, balance_after, tx_hour, days_ago, weekday = row
    amount = float(amount or 0)
    balance = float(balance_after or 1)

    # User's average transaction amount
    cursor.execute("""
        SELECT ISNULL(AVG(ABS(CAST(Amount AS FLOAT))), 3000),
               COUNT(*)
        FROM Transactions
        WHERE BusinessOwnerId = ? AND Id != ?
    """, (bo_id, tx_id))
    avg_row = cursor.fetchone()
    bo_avg = float(avg_row[0]) if avg_row else 3000.0
    bo_count = int(avg_row[1]) if avg_row else 1

    amount_zscore = round((abs(amount) - bo_avg) / max(bo_avg * 0.3, 1), 2)
    amount_to_balance = round(abs(amount) / max(balance, 1), 4)
    is_weekend = 1 if weekday in (1, 7) else 0
    type_encoded = TX_TYPES.index(tx_type) if tx_type in TX_TYPES else 0

    # Days since last transaction
    cursor.execute("""
        SELECT TOP 1 DATEDIFF(day, CreatedAt, GETDATE())
        FROM Transactions
        WHERE BusinessOwnerId = ? AND Id != ?
        ORDER BY CreatedAt DESC
    """, (bo_id, tx_id))
    gap_row = cursor.fetchone()
    days_since_last = int(gap_row[0]) if gap_row else 7

    features = [[
        abs(amount),
        amount_zscore,
        tx_hour or 10,
        bo_avg,
        bo_count,
        days_since_last,
        is_weekend,
        amount_to_balance,
        type_encoded,
    ]]

    bundle = _load_model()
    X_scaled = bundle["scaler"].transform(features)

    # scores() gives negative values for anomalies (more negative = more anomalous)
    raw_score = float(bundle["model"].score_samples(X_scaled)[0])
    # Normalize to 0-1 range where 1 = most anomalous
    anomaly_score = round(max(0.0, min(1.0, (-raw_score - 0.1) / 0.4)), 4)
    is_anomaly = 1 if anomaly_score >= 0.5 else 0

    cursor.execute("""
        UPDATE Transactions
        SET AnomalyFlag = ?, AnomalyScore = ?
        WHERE Id = ?
    """, (is_anomaly, anomaly_score, tx_id))

    return {"tx_id": tx_id, "anomaly_score": anomaly_score, "is_anomaly": bool(is_anomaly)}


def predict_anomaly_all(cursor) -> list:
    """Score all transactions."""
    cursor.execute("SELECT Id FROM Transactions WHERE AnomalyScore IS NULL OR AnomalyScore = 0")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for tid in ids:
        try:
            result = predict_anomaly_for_tx(cursor, tid)
            results.append(result)
        except Exception as e:
            results.append({"tx_id": tid, "error": str(e)})
    return results
