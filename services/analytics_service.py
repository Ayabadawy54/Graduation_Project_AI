"""Analytics service — revenue trends and review sentiment trends over time."""


def get_revenue_trend(cursor, bo_user_id: str, period: str = "weekly") -> dict:
    """Return revenue time series by week or month."""
    if period == "monthly":
        cursor.execute("""
            SELECT
                FORMAT(CreatedAt, 'yyyy-MM') AS period_label,
                ISNULL(SUM(CASE WHEN Amount > 0 THEN Amount ELSE 0 END), 0) AS revenue,
                COUNT(CASE WHEN Amount > 0 THEN 1 END) AS orders,
                ISNULL(AVG(CASE WHEN Amount > 0 THEN Amount END), 0) AS avg_order
            FROM Transactions
            WHERE BusinessOwnerId = ? AND Type = 'Sale'
            AND CreatedAt >= DATEADD(month, -12, GETDATE())
            GROUP BY FORMAT(CreatedAt, 'yyyy-MM')
            ORDER BY period_label ASC
        """, (bo_user_id,))
    else:
        cursor.execute("""
            SELECT
                FORMAT(CreatedAt, 'yyyy-') + CAST(DATEPART(WEEK, CreatedAt) AS NVARCHAR) AS period_label,
                ISNULL(SUM(CASE WHEN Amount > 0 THEN Amount ELSE 0 END), 0) AS revenue,
                COUNT(CASE WHEN Amount > 0 THEN 1 END) AS orders,
                ISNULL(AVG(CASE WHEN Amount > 0 THEN Amount END), 0) AS avg_order
            FROM Transactions
            WHERE BusinessOwnerId = ? AND Type = 'Sale'
            AND CreatedAt >= DATEADD(week, -16, GETDATE())
            GROUP BY FORMAT(CreatedAt, 'yyyy-') + CAST(DATEPART(WEEK, CreatedAt) AS NVARCHAR)
            ORDER BY period_label ASC
        """, (bo_user_id,))

    rows = cursor.fetchall()
    data = [
        {
            "period": row[0],
            "revenue": round(float(row[1]), 2),
            "orders": int(row[2]),
            "avg_order_value": round(float(row[3] or 0), 2),
        }
        for row in rows
    ]

    # Determine overall trend from last 4 vs prior 4 periods
    overall_trend = "Stable"
    if len(data) >= 8:
        recent = sum(d["revenue"] for d in data[-4:])
        prior = sum(d["revenue"] for d in data[-8:-4])
        if prior > 0:
            if recent > prior * 1.05:
                overall_trend = "Rising"
            elif recent < prior * 0.95:
                overall_trend = "Falling"

    return {
        "user_id": bo_user_id,
        "period": period,
        "overall_trend": overall_trend,
        "data": data,
    }


def get_review_trends(cursor, bo_user_id: str, period: str = "monthly") -> dict:
    """Return sentiment trend over time for a BO's products.
    Note: ProductReviews has no CreatedAt — we bucket by review Id ranges to simulate time."""
    # Get all reviews for this BO's products, ordered by Id
    cursor.execute("""
        SELECT pr.Id, pr.SentimentScore, pr.SentimentLabel
        FROM ProductReviews pr
        JOIN Products p ON p.Id = pr.ProductId
        JOIN BusinessOwnerProfile bop ON bop.Id = p.BusinessOwnerProfileId
        WHERE bop.UserId = ?
        ORDER BY pr.Id ASC
    """, (bo_user_id,))
    rows = cursor.fetchall()

    if not rows:
        return {"user_id": bo_user_id, "period": period, "data": []}

    # Bucket into groups of ~10 reviews to simulate time periods
    bucket_size = max(1, len(rows) // 6) if period == "monthly" else max(1, len(rows) // 10)
    data = []
    for i in range(0, len(rows), bucket_size):
        bucket = rows[i:i + bucket_size]
        avg_sent = sum(float(r[1] or 0) for r in bucket) / len(bucket)
        neg_count = sum(1 for r in bucket if r[2] == "Negative")
        data.append({
            "period": f"Period {len(data)+1}",
            "avg_sentiment": round(avg_sent, 4),
            "review_count": len(bucket),
            "negative_count": neg_count,
            "negative_pct": round(neg_count / len(bucket) * 100, 1),
        })

    return {"user_id": bo_user_id, "period": period, "data": data}
