"""Product service — DescriptionQuality, LowStock, Demand, AvgRating."""
import pickle
import os
import re

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")


def compute_description_quality(text: str) -> float:
    """Score product description quality 0-1 based on heuristics."""
    if not text:
        return 0.0
    score = 0.0
    word_count = len(text.split())
    if word_count >= 20:
        score += 0.3
    elif word_count >= 10:
        score += 0.15
    if word_count >= 50:
        score += 0.1
    if any(c.isupper() for c in text[:1]):
        score += 0.05
    if len(re.findall(r'[.!?]', text)) >= 2:
        score += 0.1
    if any(kw in text.lower() for kw in ["made", "quality", "material", "handmade", "premium", "natural"]):
        score += 0.15
    if any(kw in text.lower() for kw in ["features", "includes", "perfect for", "ideal"]):
        score += 0.1
    if len(text) >= 100:
        score += 0.1
    has_emoji = bool(re.search(r'[\U0001f600-\U0001f999]', text))
    if not has_emoji:
        score += 0.1
    return round(min(score, 1.0), 2)


def compute_product_metrics(cursor, product_id: int) -> dict:
    """Compute all AI metrics for a product and write to DB."""
    cursor.execute("""
        SELECT p.Id, p.Name, p.Description, p.StockQuantity, p.Price,
               p.ViewCount, p.PurchaseCount, p.BusinessOwnerProfileId
        FROM Products p WHERE p.Id = ? AND p.IsDeleted = 0
    """, (product_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Product not found"}

    pid, name, desc, stock, price, views, purchases, bo_profile_id = row
    desc = desc or ""
    stock = stock or 0
    price = float(price or 0)

    # 1. Description Quality
    quality = compute_description_quality(desc)

    # 2. Low Stock Flag (threshold: 10 units)
    low_stock = 1 if stock <= 10 else 0

    # 3. Demand Forecast
    demand_qty = 0
    try:
        with open(os.path.join(MODELS_DIR, "demand_model.pkl"), "rb") as f:
            bundle = pickle.load(f)
        # Use product_id mod 12 + 1 to map to training product
        mapped_pid = (product_id % 12) + 1
        if mapped_pid in bundle["models"]:
            import numpy as np
            from datetime import datetime
            now = datetime.now()
            features = [[52, now.month, price, 0, 1.0, views or 100]]
            m = bundle["models"][mapped_pid]
            X_scaled = m["scaler"].transform(features)
            demand_qty = max(0, int(m["model"].predict(X_scaled)[0]))
    except Exception:
        demand_qty = max(1, (purchases or 5) // 4)  # fallback

    # 4. AvgRating from reviews
    cursor.execute("""
        SELECT AVG(CAST(Rating AS FLOAT)) FROM ProductReviews WHERE ProductId = ?
    """, (product_id,))
    avg_row = cursor.fetchone()
    avg_rating = round(float(avg_row[0]), 1) if avg_row and avg_row[0] else 0.0

    # Write to DB
    cursor.execute("""
        UPDATE Products
        SET DescriptionQualityScore = ?, LowStockFlag = ?,
            DemandForecastQty = ?, AvgRating = ?
        WHERE Id = ?
    """, (quality, low_stock, demand_qty, avg_rating, product_id))

    return {
        "product_id": product_id,
        "description_quality": quality,
        "low_stock_flag": bool(low_stock),
        "demand_forecast_qty": demand_qty,
        "avg_rating": avg_rating,
    }


def compute_all_products(cursor) -> list:
    """Compute metrics for all products."""
    cursor.execute("SELECT Id FROM Products WHERE IsDeleted = 0")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for pid in ids:
        try:
            results.append(compute_product_metrics(cursor, pid))
        except Exception as e:
            results.append({"product_id": pid, "error": str(e)})
    return results
