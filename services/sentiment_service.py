"""Sentiment analysis service — scores reviews."""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def predict_sentiment_for_review(cursor, review_id: int) -> dict:
    """Analyze sentiment of a review and write results + update AvgRating."""
    cursor.execute("""
        SELECT Id, ProductId, ReviewText, Rating FROM ProductReviews WHERE Id = ?
    """, (review_id,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Review not found"}

    rid, product_id, text, rating = row
    text = text or ""

    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # Simple toxicity check (keyword-based for now)
    toxic_words = ["hate", "terrible", "worst", "scam", "fraud", "disgusting", "awful"]
    is_toxic = 1 if any(w in text.lower() for w in toxic_words) else 0

    cursor.execute("""
        UPDATE ProductReviews
        SET SentimentScore = ?, SentimentLabel = ?, FlaggedToxic = ?
        WHERE Id = ?
    """, (round(compound, 4), label, is_toxic, review_id))

    # Update product AvgRating
    cursor.execute("""
        SELECT AVG(CAST(Rating AS FLOAT)) FROM ProductReviews WHERE ProductId = ?
    """, (product_id,))
    avg_row = cursor.fetchone()
    if avg_row and avg_row[0]:
        cursor.execute("UPDATE Products SET AvgRating = ? WHERE Id = ?",
                       (round(float(avg_row[0]), 1), product_id))

    return {
        "review_id": review_id,
        "sentiment_score": round(compound, 4),
        "sentiment_label": label,
        "flagged_toxic": bool(is_toxic),
    }


def predict_sentiment_all(cursor) -> list:
    """Score all reviews."""
    cursor.execute("SELECT Id FROM ProductReviews")
    ids = [r[0] for r in cursor.fetchall()]
    results = []
    for rid in ids:
        try:
            results.append(predict_sentiment_for_review(cursor, rid))
        except Exception as e:
            results.append({"review_id": rid, "error": str(e)})
    return results
