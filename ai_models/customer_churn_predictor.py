"""
Customer Churn Prediction Model
Predicts which customers are likely to stop purchasing
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import json
from datetime import datetime


class CustomerChurnPredictor:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.version = "1.0.0"
        
    def prepare_features(self, users_df, orders_df):
        """
        Engineer features for churn prediction
        """
        customers = users_df[users_df['user_type'] == 'customer'].copy()
        
        features_list = []
        labels = []
        
        for _, customer in customers.iterrows():
            customer_id = customer['user_id']
            customer_orders = orders_df[orders_df['customer_user_id'] == customer_id]
            
            # Skip if no orders
            if len(customer_orders) == 0:
                continue
            
            # Convert dates
            customer_orders['order_date'] = pd.to_datetime(customer_orders['order_date'])
            customer['created_at'] = pd.to_datetime(customer['created_at'])
            
            # Calculate features
            total_orders = len(customer_orders)
            total_spent = customer_orders['total_price_egp'].sum()
            avg_order_value = total_spent / total_orders if total_orders > 0 else 0
            
            # Recency - days since last order
            last_order_date = customer_orders['order_date'].max()
            days_since_last_order = (datetime.now() - last_order_date).days
            
            # Frequency - orders per month
            customer_age_days = (datetime.now() - customer['created_at']).days
            orders_per_month = (total_orders / max(customer_age_days, 1)) * 30
            
            # Monetary - average spend
            avg_monthly_spend = (total_spent / max(customer_age_days, 1)) * 30
            
            # Order consistency (std of days between orders)
            if len(customer_orders) > 1:
                order_dates_sorted = customer_orders['order_date'].sort_values()
                days_between = order_dates_sorted.diff().dt.days.dropna()
                order_consistency = days_between.std() if len(days_between) > 0 else 0
            else:
                order_consistency = 0
            
            # Cancelled order rate
            cancelled_count = len(customer_orders[customer_orders['status'] == 'cancelled'])
            cancellation_rate = cancelled_count / total_orders if total_orders > 0 else 0
            
            # Category diversity (how many categories purchased from)
            try:
                products_df = pd.read_csv('mock_data/products.csv', encoding='utf-8-sig')
                customer_products = products_df[products_df['product_id'].isin(customer_orders['product_id'])]
                category_diversity = customer_products['category'].nunique()
            except:
                category_diversity = 1
            
            # Trend - comparing recent vs older orders
            if len(customer_orders) >= 4:
                mid_point = len(customer_orders) // 2
                recent_orders = customer_orders.nlargest(mid_point, 'order_date')
                older_orders = customer_orders.nsmallest(mid_point, 'order_date')
                
                recent_avg = recent_orders['total_price_egp'].mean()
                older_avg = older_orders['total_price_egp'].mean()
                spending_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            else:
                spending_trend = 0
            
            features = {
                'days_since_last_order': days_since_last_order,
                'total_orders': total_orders,
                'orders_per_month': orders_per_month,
                'avg_order_value': avg_order_value,
                'total_spent': total_spent,
                'avg_monthly_spend': avg_monthly_spend,
                'order_consistency': order_consistency if not np.isnan(order_consistency) else 0,
                'cancellation_rate': cancellation_rate,
                'category_diversity': category_diversity,
                'customer_age_days': customer_age_days,
                'spending_trend': spending_trend
            }
            
            # Define churn: No order in 60+ days AND had at least 2 orders
            is_churned = (days_since_last_order > 60) and (total_orders >= 2)
            
            features_list.append(features)
            labels.append(1 if is_churned else 0)
        
        X = pd.DataFrame(features_list)
        y = pd.Series(labels)
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def train(self, X, y):
        """
        Train churn prediction model
        """
        print("\n" + "="*60)
        print("TRAINING CUSTOMER CHURN PREDICTION MODEL")
        print("="*60)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nDataset split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        print(f"   Churned customers: {sum(y_train)} ({sum(y_train)/len(y_train)*100:.1f}%)")
        
        # Train
        print("\nTraining Gradient Boosting Classifier...")
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        print("\nModel Performance:")
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"   Training accuracy: {train_score:.3f}")
        print(f"   Testing accuracy: {test_score:.3f}")
        
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        roc_auc = roc_auc_score(y_test, y_prob)
        print(f"   ROC-AUC Score: {roc_auc:.3f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Active', 'Churned']))
        
        # Feature Importance
        print("\nTop 5 Churn Indicators:")
        importances = self.model.feature_importances_
        feature_importance = sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (feature, importance) in enumerate(feature_importance[:5], 1):
            print(f"   {i}. {feature}: {importance:.3f}")
        
        self.feature_importance = dict(feature_importance)
        
        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'roc_auc': roc_auc
        }
    
    def predict_churn_risk(self, features_dict):
        """
        Predict churn probability for a customer
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        X = pd.DataFrame([features_dict])
        X = X[self.feature_names]
        
        churn_prob = self.model.predict_proba(X)[0, 1]
        
        if churn_prob > 0.7:
            risk_level = 'high'
            action = 'Send win-back offer immediately'
        elif churn_prob > 0.4:
            risk_level = 'medium'
            action = 'Engage with personalized campaign'
        else:
            risk_level = 'low'
            action = 'Continue regular engagement'
        
        return {
            'churn_probability': round(churn_prob, 3),
            'risk_level': risk_level,
            'recommended_action': action
        }
    
    def save(self, filepath='ai_models/churn_predictor_v1.pkl'):
        """Save model"""
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'version': self.version,
            'trained_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")


def main():
    print("Loading data...")
    users_df = pd.read_csv('mock_data/users.csv', encoding='utf-8-sig')
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    
    model = CustomerChurnPredictor()
    
    print("Engineering features...")
    X, y = model.prepare_features(users_df, orders_df)
    
    metrics = model.train(X, y)
    model.save()
    
    # Save metadata
    metadata = {
        'model_name': 'Customer Churn Predictor',
        'version': model.version,
        'trained_date': datetime.now().isoformat(),
        'performance': metrics
    }
    
    with open('ai_models/churn_predictor_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("CHURN PREDICTION MODEL COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
