"""Material service — OrderFrequency and PriceTrend per raw material."""


def compute_material_stats(cursor) -> list:
    """Compute OrderFrequency and PriceTrend for all raw materials."""
    cursor.execute("SELECT Id, Price FROM RawMaterials WHERE IsDeleted = 0")
    materials = cursor.fetchall()
    results = []
    for mat in materials:
        mat_id, current_price = mat[0], float(mat[1] or 0)
        try:
            # Order frequency: count orders in last 30 days
            cursor.execute("""
                SELECT COUNT(*)
                FROM MaterialOrderItems moi
                JOIN MaterialOrders mo ON mo.Id = moi.MaterialOrderId
                WHERE moi.MaterialId = ?
                AND mo.CreatedAt >= DATEADD(day, -30, GETDATE())
            """, (mat_id,))
            freq = (cursor.fetchone() or [0])[0]

            # Price trend: compare current price to avg of older orders
            cursor.execute("""
                SELECT ISNULL(AVG(CAST(moi.UnitPrice AS FLOAT)), 0)
                FROM MaterialOrderItems moi
                JOIN MaterialOrders mo ON mo.Id = moi.MaterialOrderId
                WHERE moi.MaterialId = ?
                AND mo.CreatedAt < DATEADD(day, -30, GETDATE())
            """, (mat_id,))
            old_avg_row = cursor.fetchone()
            old_avg = float(old_avg_row[0]) if old_avg_row and old_avg_row[0] else current_price

            if old_avg == 0:
                trend = "Stable"
            elif current_price > old_avg * 1.05:
                trend = "Rising"
            elif current_price < old_avg * 0.95:
                trend = "Falling"
            else:
                trend = "Stable"

            cursor.execute("""
                UPDATE RawMaterials
                SET OrderFrequency = ?, PriceTrend = ?
                WHERE Id = ?
            """, (freq, trend, mat_id))

            results.append({"material_id": mat_id, "order_frequency": freq, "price_trend": trend})
        except Exception as e:
            results.append({"material_id": mat_id, "error": str(e)})
    return results
