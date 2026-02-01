"""
Owner Risk Scoring Model
Predicts likelihood of brand causing issues (returns, complaints, fraud)
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import json
from datetime import datetime

class OwnerRiskModel:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.version = "1.0.0"
        
    def prepare_features(self, brands_df, orders_df, reviews_df):
        """
        Engineer features for risk prediction
        """
        features_list = []
        labels = []
        
        for _, brand in brands_df.iterrows():
            brand_id = brand['brand_id']
            
            # Get brand's orders
            brand_orders = orders_df[orders_df['brand_id'] == brand_id]
            
            # Skip if no orders
            if len(brand_orders) == 0:
                continue
            
            # Calculate features
            total_orders = len(brand_orders)
            cancelled_orders = len(brand_orders[brand_orders['status'] == 'cancelled'])
            completed_orders = len(brand_orders[brand_orders['status'] == 'completed'])
            
            # Return rate
            return_rate = cancelled_orders / total_orders if total_orders > 0 else 0
            
            # Fulfillment rate
            fulfillment_rate = (completed_orders + len(brand_orders[brand_orders['status'] == 'shipped'])) / total_orders if total_orders > 0 else 0
            
            # Average rating
            avg_rating = brand['avg_rating'] if pd.notna(brand['avg_rating']) else 3.5
            
            # Rating variance (stability)
            brand_reviews = reviews_df[reviews_df['brand_id'] == brand_id]
            rating_variance = brand_reviews['rating'].std() if len(brand_reviews) > 0 else 1.0
            
            # Profile completeness
            profile_complete = 1 if brand['profile_complete'] else 0
            verified = 1 if brand['verified'] else 0
            
            # Sales metrics
            total_sales = brand['total_sales_egp']
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Time on platform
            created_at = pd.to_datetime(brand['created_at'])
            days_on_platform = (datetime.now() - created_at).days
            
            # Reviews count
            review_count = brand['rating_count']
            
            features = {
                'return_rate': return_rate,
                'fulfillment_rate': fulfillment_rate,
                'avg_rating': avg_rating,
                'rating_variance': rating_variance if pd.notna(rating_variance) else 1.0,
                'profile_complete': profile_complete,
                'verified': verified,
                'total_orders': total_orders,
                'avg_order_value': avg_order_value,
                'days_on_platform': days_on_platform,
                'review_count': review_count,
                'total_sales': total_sales,
            }
            
            # Create label (high risk if return_rate > 15% OR avg_rating < 3.5 OR fulfillment_rate < 80%)
            is_high_risk = (return_rate > 0.15) or (avg_rating < 3.5) or (fulfillment_rate < 0.8)
            
            features_list.append(features)
            labels.append(1 if is_high_risk else 0)
        
        # Convert to DataFrame
        X = pd.DataFrame(features_list)
        y = pd.Series(labels)
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def train(self, X, y):
        """
        Train the risk scoring model
        """
        print("\n" + "="*60)
        print("TRAINING OWNER RISK SCORING MODEL")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nDataset split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        print(f"   High-risk brands: {sum(y_train)} ({sum(y_train)/len(y_train)*100:.1f}%)")
        
        # Train model
        print("\nTraining Random Forest Classifier...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'  # Handle class imbalance
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        print("\nModel Performance:")
        
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"   Training accuracy: {train_score:.3f}")
        print(f"   Testing accuracy: {test_score:.3f}")
        
        # Predictions
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        # ROC-AUC
        roc_auc = roc_auc_score(y_test, y_prob)
        print(f"   ROC-AUC Score: {roc_auc:.3f}")
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Low Risk', 'High Risk']))
        
        # Confusion Matrix
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"   True Negatives: {cm[0,0]}")
        print(f"   False Positives: {cm[0,1]}")
        print(f"   False Negatives: {cm[1,0]}")
        print(f"   True Positives: {cm[1,1]}")
        
        # Feature Importance
        print("\nTop 5 Feature Importance:")
        importances = self.model.feature_importances_
        feature_importance = sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (feature, importance) in enumerate(feature_importance[:5], 1):
            print(f"   {i}. {feature}: {importance:.3f}")
        
        # Save feature importance
        self.feature_importance = dict(feature_importance)
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'roc_auc': roc_auc
        }
    
    def predict(self, features_dict):
        """
        Predict risk for a single brand
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert to DataFrame
        X = pd.DataFrame([features_dict])
        
        # Ensure correct feature order
        X = X[self.feature_names]
        
        # Predict
        risk_prob = self.model.predict_proba(X)[0, 1]
        risk_class = self.model.predict(X)[0]
        
        # Determine risk level
        if risk_prob > 0.6:
            risk_level = 'high'
        elif risk_prob > 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_score': round(risk_prob, 3),
            'risk_level': risk_level,
            'is_high_risk': bool(risk_class)
        }
    
    def save(self, filepath='ai_models/owner_risk_model_v1.pkl'):
        """
        Save trained model
        """
        if self.model is None:
            raise ValueError("No model to save!")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'version': self.version,
            'trained_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")
    
    def load(self, filepath='ai_models/owner_risk_model_v1.pkl'):
        """
        Load trained model
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data['feature_importance']
        self.version = model_data['version']
        
        print(f"Model loaded from: {filepath}")
        print(f"   Version: {self.version}")
        print(f"   Trained: {model_data['trained_date']}")


def main():
    """
    Train and save the model
    """
    # Load data
    print("Loading data...")
    brands_df = pd.read_csv('mock_data/brands.csv', encoding='utf-8-sig')
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    reviews_df = pd.read_csv('mock_data/reviews.csv', encoding='utf-8-sig')
    
    # Initialize model
    model = OwnerRiskModel()
    
    # Prepare features
    print("Engineering features...")
    X, y = model.prepare_features(brands_df, orders_df, reviews_df)
    
    # Train
    metrics = model.train(X, y)
    
    # Save
    model.save()
    
    # Save metadata
    metadata = {
        'model_name': 'Owner Risk Scoring Model',
        'version': model.version,
        'trained_date': datetime.now().isoformat(),
        'total_samples': len(X),
        'features': model.feature_names,
        'performance': metrics
    }
    
    with open('ai_models/owner_risk_model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE!")
    print("="*60)
    
    # Test prediction
    print("\nTesting prediction on sample brand...")
    test_features = {
        'return_rate': 0.12,
        'fulfillment_rate': 0.88,
        'avg_rating': 4.2,
        'rating_variance': 0.8,
        'profile_complete': 1,
        'verified': 1,
        'total_orders': 50,
        'avg_order_value': 150,
        'days_on_platform': 180,
        'review_count': 35,
        'total_sales': 7500
    }
    
    prediction = model.predict(test_features)
    print(f"   Risk Score: {prediction['risk_score']}")
    print(f"   Risk Level: {prediction['risk_level']}")
    print(f"   High Risk: {prediction['is_high_risk']}")


if __name__ == "__main__":
    main()
