"""
Fraud Detection Model
Detects suspicious orders and fake reviews
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json
import joblib


class FraudDetector:
    def __init__(self):
        self.version = "1.0.0"
        self.order_fraud_model = None
        self.review_fraud_rules = None
        
    def detect_suspicious_orders(self, orders_df, users_df):
        """
        Detect potentially fraudulent orders using anomaly detection
        """
        print("\n" + "="*60)
        print("TRAINING FRAUD DETECTION MODEL")
        print("="*60)
        
        # Merge with user data (rename to avoid confusion)
        users_info = users_df[['user_id', 'created_at']].copy()
        users_info.rename(columns={'created_at': 'user_created_at'}, inplace=True)
        
        orders_with_users = orders_df.merge(
            users_info,
            left_on='customer_user_id',
            right_on='user_id',
            how='left'
        )
        
        orders_with_users['order_date'] = pd.to_datetime(orders_with_users['order_date'])
        orders_with_users['user_created_at'] = pd.to_datetime(orders_with_users['user_created_at'])
        
        # Feature engineering for anomaly detection
        features = []
        
        for _, order in orders_with_users.iterrows():
            # Account age at time of order
            account_age_days = (order['order_date'] - order['user_created_at']).days
            
            feat = {
                'order_amount': order['total_price_egp'],
                'quantity': order['quantity'],
                'account_age_days': max(account_age_days, 0),
                'hour_of_day': order['order_date'].hour,
                'is_cancelled': 1 if order['status'] == 'cancelled' else 0
            }
            
            features.append(feat)
        
        X = pd.DataFrame(features)
        
        # Train Isolation Forest
        print("\nTraining Isolation Forest...")
        self.order_fraud_model = IsolationForest(
            contamination=0.05,  # Assume 5% are anomalies
            random_state=42
        )
        
        predictions = self.order_fraud_model.fit_predict(X)
        anomaly_scores = self.order_fraud_model.score_samples(X)
        
        # Add results to orders
        orders_df['fraud_score'] = -anomaly_scores  # Convert to fraud score (higher = more suspicious)
        orders_df['is_suspicious'] = predictions == -1
        
        suspicious_count = sum(predictions == -1)
        print(f"\nDetected {suspicious_count} suspicious orders ({suspicious_count/len(orders_df)*100:.1f}%)")
        
        # Analyze suspicious patterns
        suspicious_orders = orders_df[orders_df['is_suspicious']]
        
        print(f"\nSuspicious Order Patterns:")
        print(f"   Average amount: {suspicious_orders['total_price_egp'].mean():.2f} EGP")
        print(f"   Cancellation rate: {len(suspicious_orders[suspicious_orders['status']=='cancelled'])/len(suspicious_orders)*100:.1f}%")
        
        return orders_df
    
    def detect_fake_reviews(self, reviews_df, users_df, orders_df):
        """
        Detect potentially fake reviews using rule-based approach
        """
        print("\nDetecting Fake Reviews...")
        
        fake_indicators = []
        
        for _, review in reviews_df.iterrows():
            score = 0
            reasons = []
            
            # Check 1: Review length (too short or too generic)
            review_length = len(review['review_text'].split())
            if review_length < 5:
                score += 0.3
                reasons.append('Very short review')
            
            # Check 2: Rating inconsistency (5 stars but minimal text)
            if review['rating'] == 5 and len(review['review_text']) < 10:
                score += 0.2
                reasons.append('Minimal 5-star review')
                
            # Check 3: User account age (if we have the data)
            user = users_df[users_df['user_id'] == review['customer_user_id']]
            if len(user) > 0:
                user_created = pd.to_datetime(user.iloc[0]['created_at'])
                review_created = pd.to_datetime(review['created_at'])
                account_age = (review_created - user_created).days
                
                if account_age < 1:
                    score += 0.4
                    reasons.append('New account (< 1 day old)')
            
            # Check 4: Multiple reviews in short time
            user_reviews = reviews_df[reviews_df['customer_user_id'] == review['customer_user_id']]
            if len(user_reviews) > 5:
                review_dates = pd.to_datetime(user_reviews['created_at'])
                if (review_dates.max() - review_dates.min()).days < 7:
                    score += 0.3
                    reasons.append('Multiple reviews in short period')
            
            # Check 5: Verified purchase (if column exists)
            if 'verified_purchase' in review.index and not review.get('verified_purchase', True):
                score += 0.5
                reasons.append('Not a verified purchase')
            
            fake_indicators.append({
                'review_id': review['review_id'],
                'fake_score': min(score, 1.0),
                'is_suspicious': score > 0.6,
                'reasons': reasons
            })
        
        fake_df = pd.DataFrame(fake_indicators)
        suspicious_reviews = len(fake_df[fake_df['is_suspicious']])
        
        print(f"   Suspicious reviews: {suspicious_reviews} ({suspicious_reviews/len(reviews_df)*100:.1f}%)")
        
        return fake_df
    
    def save(self, filepath='ai_models/fraud_detector_v1.pkl'):
        """Save model"""
        model_data = {
            'order_fraud_model': self.order_fraud_model,
            'version': self.version,
            'trained_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")


def main():
    print("Loading data...")
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    users_df = pd.read_csv('mock_data/users.csv', encoding='utf-8-sig')
    reviews_df = pd.read_csv('mock_data/reviews.csv', encoding='utf-8-sig')
    
    detector = FraudDetector()
    
    # Detect suspicious orders
    orders_with_fraud = detector.detect_suspicious_orders(orders_df, users_df)
    
    # Detect fake reviews
    review_fraud = detector.detect_fake_reviews(reviews_df, users_df, orders_df)
    
    # Save results
    orders_with_fraud.to_csv('ai_models/orders_with_fraud_scores.csv', index=False, encoding='utf-8-sig')
    review_fraud.to_csv('ai_models/review_fraud_scores.csv', index=False, encoding='utf-8-sig')
    
    detector.save()
    
    # Metadata
    metadata = {
        'model_name': 'Fraud Detector',
        'version': detector.version,
        'trained_date': datetime.now().isoformat(),
        'suspicious_orders': int(orders_with_fraud['is_suspicious'].sum()),
        'suspicious_reviews': int(review_fraud['is_suspicious'].sum())
    }
    
    with open('ai_models/fraud_detector_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("FRAUD DETECTION COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
