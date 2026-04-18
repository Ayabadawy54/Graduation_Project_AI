"""Benchmark service — compare BO metrics vs category average."""


def get_benchmark(cursor, bo_user_id: str) -> dict:
    """Return BO vs category percentile rankings."""
    # Get BO's category
    cursor.execute("""
        SELECT BusinessCategory FROM BusinessOwnerProfile WHERE UserId = ? AND IsDeleted=0
    """, (bo_user_id,))
    cat_row = cursor.fetchone()
    category_id = cat_row[0] if cat_row else None

    # BO metrics
    cursor.execute("""
        SELECT
            ISNULL(AVG(CAST(r.FulfillmentTimeHours AS FLOAT)), 0) AS avg_fulfillment,
            ISNULL(COUNT(r.Id), 0) AS total_orders,
            ISNULL(SUM(CASE WHEN r.QuotedPrice IS NOT NULL THEN r.QuotedPrice ELSE 0 END), 0) AS total_revenue
        FROM BoProductionRequests r
        WHERE r.BusinessOwnerId = ? AND r.Status = 'Completed'
    """, (bo_user_id,))
    bo_row = cursor.fetchone()
    bo_fulfillment = float(bo_row[0] or 0)
    bo_total_orders = int(bo_row[1] or 0)
    bo_total_revenue = float(bo_row[2] or 0)

    cursor.execute("""
        SELECT ISNULL(AVG(CAST(p.DescriptionQualityScore AS FLOAT)), 0)
        FROM Products p
        JOIN BusinessOwnerProfile bop ON bop.Id = p.BusinessOwnerProfileId
        WHERE bop.UserId = ? AND p.IsDeleted = 0
    """, (bo_user_id,))
    bo_quality = float((cursor.fetchone() or [0])[0] or 0)

    cursor.execute("""
        SELECT ISNULL(AVG(CAST(p.AvgRating AS FLOAT)), 0)
        FROM Products p
        JOIN BusinessOwnerProfile bop ON bop.Id = p.BusinessOwnerProfileId
        WHERE bop.UserId = ? AND p.IsDeleted = 0
    """, (bo_user_id,))
    bo_rating = float((cursor.fetchone() or [0])[0] or 0)

    # Platform average metrics (all BOs)
    cursor.execute("""
        SELECT
            ISNULL(AVG(CAST(FulfillmentTimeHours AS FLOAT)), 0),
            COUNT(DISTINCT BusinessOwnerId),
            ISNULL(AVG(CAST(QuotedPrice AS FLOAT)), 0)
        FROM BoProductionRequests WHERE Status = 'Completed'
    """)
    plat_row = cursor.fetchone()
    plat_fulfillment = float(plat_row[0] or 1)
    bo_count = int(plat_row[1] or 1)
    plat_avg_order = float(plat_row[2] or 1)

    cursor.execute("""
        SELECT ISNULL(AVG(CAST(DescriptionQualityScore AS FLOAT)), 0) FROM Products WHERE IsDeleted=0
    """)
    plat_quality = float((cursor.fetchone() or [0])[0] or 0)

    cursor.execute("""
        SELECT ISNULL(AVG(CAST(AvgRating AS FLOAT)), 0) FROM Products WHERE IsDeleted=0
    """)
    plat_rating = float((cursor.fetchone() or [0])[0] or 0)

    # Compute percentile ranks (0=worst, 100=best)
    def pct_rank(bo_val, plat_val, lower_is_better=False):
        if plat_val == 0:
            return 50
        ratio = bo_val / plat_val
        if lower_is_better:
            score = max(0, min(100, int((2 - ratio) * 50)))
        else:
            score = max(0, min(100, int(ratio * 50)))
        return score

    fulfillment_rank = pct_rank(bo_fulfillment, plat_fulfillment, lower_is_better=True)
    quality_rank = pct_rank(bo_quality, plat_quality)
    rating_rank = pct_rank(bo_rating, plat_rating)

    def rank_label(pct):
        if pct >= 80:
            return "top 20%"
        elif pct >= 60:
            return "top 40%"
        elif pct >= 40:
            return "average"
        elif pct >= 20:
            return "bottom 40%"
        return "bottom 20%"

    benchmark = {
        "user_id": bo_user_id,
        "fulfillment_rank": rank_label(fulfillment_rank),
        "fulfillment_rank_pct": fulfillment_rank,
        "quality_rank": rank_label(quality_rank),
        "quality_rank_pct": quality_rank,
        "rating_rank": rank_label(rating_rank),
        "rating_rank_pct": rating_rank,
        "bo_fulfillment_hours": round(bo_fulfillment, 1),
        "platform_avg_fulfillment_hours": round(plat_fulfillment, 1),
        "bo_quality_score": round(bo_quality, 2),
        "platform_avg_quality": round(plat_quality, 2),
    }
    return benchmark


def get_all_benchmarks(cursor) -> list:
    cursor.execute("SELECT UserId FROM BusinessOwnerProfile WHERE IsDeleted=0")
    ids = [r[0] for r in cursor.fetchall()]
    return [get_benchmark(cursor, uid) for uid in ids]
