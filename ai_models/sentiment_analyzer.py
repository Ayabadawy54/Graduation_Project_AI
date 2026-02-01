"""
Review Sentiment Analysis
Analyzes customer review sentiment
"""
import pandas as pd
import numpy as np
from datetime import datetime
import json

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("VADER not installed. Using rule-based approach.")


class SentimentAnalyzer:
    def __init__(self):
        self.version = "1.0.0"
        
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
            self.method = "VADER"
        else:
            self.analyzer = None
            self.method = "Rule-based"
        
        # Keyword lists for rule-based approach
        self.positive_keywords = [
            'great', 'excellent', 'amazing', 'love', 'perfect', 'recommend', 
            'best', 'wonderful', 'fantastic', 'awesome', 'good', 'nice',
            'beautiful', 'quality', 'fast', 'happy', 'satisfied'
        ]
        
        self.negative_keywords = [
            'poor', 'bad', 'terrible', 'worst', 'disappointed', 'awful', 
            'waste', 'horrible', 'slow', 'late', 'broken', 'damaged',
            'fake', 'cheap', 'never', 'return', 'refund'
        ]
    
    def analyze(self, text):
        """
        Analyze sentiment of review text
        """
        if not text or pd.isna(text):
            return {
                'sentiment': 'neutral',
                'score': 0.5,
                'confidence': 0.0,
                'method': self.method
            }
        
        text = str(text).lower()
        
        if VADER_AVAILABLE and self.analyzer:
            return self._analyze_vader(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_vader(self, text):
        """
        VADER sentiment analysis
        """
        scores = self.analyzer.polarity_scores(text)
        
        # Classify based on compound score
        compound = scores['compound']
        
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Normalize score to 0-1
        normalized_score = (compound + 1) / 2  # Convert from [-1,1] to [0,1]
        
        return {
            'sentiment': sentiment,
            'score': round(normalized_score, 3),
            'confidence': round(abs(compound), 3),
            'method': 'VADER',
            'raw_scores': scores
        }
    
    def _analyze_rule_based(self, text):
        """
        Simple rule-based sentiment analysis
        """
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        negative_count = sum(1 for word in self.negative_keywords if word in text)
        
        # Calculate sentiment
        if positive_count > negative_count:
            sentiment = 'positive'
            score = 0.6 + min(positive_count * 0.1, 0.3)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = 0.4 - min(negative_count * 0.1, 0.3)
        else:
            sentiment = 'neutral'
            score = 0.5
        
        confidence = abs(positive_count - negative_count) / max(len(text.split()), 1)
        
        return {
            'sentiment': sentiment,
            'score': round(max(0, min(1, score)), 3),
            'confidence': round(min(confidence, 1.0), 3),
            'method': 'Rule-based',
            'positive_words': positive_count,
            'negative_words': negative_count
        }
    
    def analyze_batch(self, reviews_df):
        """
        Analyze sentiment for multiple reviews
        """
        print("\n" + "="*60)
        print("ANALYZING REVIEW SENTIMENTS")
        print("="*60)
        
        results = []
        
        for _, review in reviews_df.iterrows():
            sentiment_result = self.analyze(review['review_text'])
            
            results.append({
                'review_id': review['review_id'],
                'rating': review['rating'],
                'sentiment': sentiment_result['sentiment'],
                'sentiment_score': sentiment_result['score'],
                'confidence': sentiment_result['confidence']
            })
        
        results_df = pd.DataFrame(results)
        
        # Statistics
        print(f"\nSentiment Distribution:")
        print(f"   Positive: {len(results_df[results_df['sentiment'] == 'positive'])} ({len(results_df[results_df['sentiment'] == 'positive'])/len(results_df)*100:.1f}%)")
        print(f"   Neutral: {len(results_df[results_df['sentiment'] == 'neutral'])} ({len(results_df[results_df['sentiment'] == 'neutral'])/len(results_df)*100:.1f}%)")
        print(f"   Negative: {len(results_df[results_df['sentiment'] == 'negative'])} ({len(results_df[results_df['sentiment'] == 'negative'])/len(results_df)*100:.1f}%)")
        
        # Correlation with ratings
        print(f"\nSentiment vs Rating Correlation:")
        avg_score_by_rating = results_df.groupby('rating')['sentiment_score'].mean()
        for rating in sorted(avg_score_by_rating.index):
            print(f"   {rating} stars: {avg_score_by_rating[rating]:.3f} sentiment score")
        
        return results_df
    
    def save_results(self, results_df, filepath='ai_models/sentiment_analysis_results.csv'):
        """
        Save sentiment analysis results
        """
        results_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"\nResults saved to: {filepath}")


def main():
    """
    Run sentiment analysis on all reviews
    """
    # Load reviews
    print("Loading reviews...")
    reviews_df = pd.read_csv('mock_data/reviews.csv', encoding='utf-8-sig')
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    print(f"Using method: {analyzer.method}")
    
    # Analyze
    results = analyzer.analyze_batch(reviews_df)
    
    # Save
    analyzer.save_results(results)
    
    # Save metadata
    metadata = {
        'model_name': 'Sentiment Analyzer',
        'version': analyzer.version,
        'method': analyzer.method,
        'analyzed_date': datetime.now().isoformat(),
        'total_reviews': len(reviews_df),
        'sentiment_distribution': {
            'positive': int(len(results[results['sentiment'] == 'positive'])),
            'neutral': int(len(results[results['sentiment'] == 'neutral'])),
            'negative': int(len(results[results['sentiment'] == 'negative']))
        }
    }
    
    with open('ai_models/sentiment_analyzer_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
