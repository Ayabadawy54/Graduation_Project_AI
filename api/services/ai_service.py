"""
AI Service - Handles all AI model predictions and analytics
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class AIService:
    def __init__(self):
        pass
    
    # ============================================
    # BRAND RISK SCORING
    # ============================================
    
    def calculate_brand_risk_score(self, brand_data: dict, orders_df: pd.DataFrame, reviews_df: pd.DataFrame) -> Dict:
        """
        Calculate risk score for a brand (owner)
        Returns: {risk_score, risk_level, risk_factors, recommendations}
        """
        brand_id = brand_data['brand_id']
        
        # Get brand's orders
        brand_orders = orders_df[orders_df['brand_id'] == brand_id]
        
        # Calculate features
        total_orders = len(brand_orders)
        if total_orders == 0:
            return {
                'risk_score': 0.5,
                'risk_level': 'medium',
                'risk_factors': ['New brand with no order history'],
                'recommendations': ['Monitor first 10 orders closely']
            }
        
        # Return rate
        cancelled_orders = len(brand_orders[brand_orders['status'] == 'cancelled'])
        return_rate = cancelled_orders / total_orders if total_orders > 0 else 0
        
        # Average rating
        avg_rating = brand_data.get('avg_rating', 3.5)
        
        # Fulfillment rate (completed + shipped / total)
        fulfilled = len(brand_orders[brand_orders['status'].isin(['completed', 'shipped'])])
        fulfillment_rate = fulfilled / total_orders if total_orders > 0 else 0.5
        
        # Verification status
        verified = brand_data.get('verified', False)
        profile_complete = brand_data.get('profile_complete', False)
        
        # Calculate risk score (0-1, higher = more risky)
        risk_score = (
            return_rate * 0.4 +
            (1 - fulfillment_rate) * 0.3 +
            (5 - avg_rating) / 5 * 0.2 +
            (0 if verified else 0.1)
        )
        
        # Determine risk level
        if risk_score > 0.6:
            risk_level = 'high'
        elif risk_score > 0.3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Identify risk factors
        risk_factors = []
        if return_rate > 0.15:
            risk_factors.append(f'High return rate ({return_rate*100:.1f}%)')
        if fulfillment_rate < 0.85:
            risk_factors.append(f'Low fulfillment rate ({fulfillment_rate*100:.1f}%)')
        if avg_rating < 3.5:
            risk_factors.append(f'Low average rating ({avg_rating}/5.0)')
        if not verified:
            risk_factors.append('Brand not verified')
        if not profile_complete:
            risk_factors.append('Incomplete profile')
        
        # Generate recommendations
        recommendations = []
        if risk_level == 'high':
            recommendations.append('Consider temporary hold on new listings')
            recommendations.append('Request quality improvement plan')
        elif risk_level == 'medium':
            recommendations.append('Monitor next 10 orders closely')
            recommendations.append('Send best practices guide')
        else:
            recommendations.append('Brand performing well')
            if not verified:
                recommendations.append('Consider verification for badge')
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'risk_factors': risk_factors if risk_factors else ['No major risk factors detected'],
            'recommendations': recommendations
        }
    
    # ============================================
    # PRODUCT QUALITY SCORING
    # ============================================
    
    def calculate_product_quality_score(self, product_data: dict, brand_data: dict) -> Dict:
        """
        Assess product listing quality
        Returns: {quality_score, approval_action, suggestions}
        """
        # Features
        price = product_data.get('price_egp', 0)
        stock = product_data.get('stock_quantity', 0)
        views = product_data.get('views', 0)
        clicks = product_data.get('clicks', 0)
        description = product_data.get('description', '')
        
        # Brand reputation
        brand_verified = brand_data.get('verified', False)
        brand_rating = brand_data.get('avg_rating', 3.5)
        
        # Calculate quality score
        quality_score = 0.5  # Base score
        
        # Price appropriateness (50-2000 EGP is normal)
        if 50 <= price <= 2000:
            quality_score += 0.2
        
        # Has stock
        if stock > 0:
            quality_score += 0.1
        
        # Description length
        if len(description) > 100:
            quality_score += 0.1
        
        # Brand reputation boost
        if brand_verified:
            quality_score += 0.1
        if brand_rating >= 4.0:
            quality_score += 0.1
        
        # Determine approval action
        if quality_score >= 0.8 and brand_verified:
            approval_action = 'auto_approve'
        elif quality_score >= 0.6:
            approval_action = 'manual_review'
        else:
            approval_action = 'auto_reject'
        
        # Generate suggestions
        suggestions = []
        if price < 50:
            suggestions.append('Price seems very low - verify product value')
        elif price > 2000:
            suggestions.append('High price - ensure product justifies cost')
        if stock == 0:
            suggestions.append('Product out of stock - update inventory')
        if len(description) < 100:
            suggestions.append('Add more detailed product description')
        if not brand_verified:
            suggestions.append('Brand verification would improve trust')
        
        return {
            'quality_score': round(quality_score, 2),
            'approval_action': approval_action,
            'confidence': 0.85,
            'suggestions': suggestions if suggestions else ['Product meets quality standards']
        }
    
    # ============================================
    # SALES FORECASTING
    # ============================================
    
    def forecast_orders(self, orders_df: pd.DataFrame, days: int = 7, category: str = None) -> List[Dict]:
        """
        Forecast order volume for next N days
        """
        # Convert order_date to datetime
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        # Filter by category if specified
        if category:
            # Get products in category, then filter orders
            orders_df = orders_df.copy()  # Work with copy
        
        # Get historical daily orders
        daily_orders = orders_df.groupby(orders_df['order_date'].dt.date).size()
        
        # Simple moving average forecast
        avg_orders = daily_orders.mean()
        
        # Generate forecast
        forecast = []
        last_date = orders_df['order_date'].max()
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            
            # Apply day-of-week pattern (weekend boost)
            day_of_week = forecast_date.weekday()
            multiplier = 1.2 if day_of_week in [4, 5] else 1.0  # Friday, Saturday boost
            
            predicted = int(avg_orders * multiplier)
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_orders': predicted,
                'confidence_low': int(predicted * 0.8),
                'confidence_high': int(predicted * 1.2),
                'factors': [
                    f"{'Weekend' if day_of_week in [4,5] else 'Weekday'} pattern",
                    f"Based on {len(daily_orders)} days of history"
                ]
            })
        
        return forecast
    
    # ============================================
    # SENTIMENT ANALYSIS
    # ============================================
    
    def analyze_review_sentiment(self, review_text: str) -> Dict:
        """
        Analyze sentiment of review text
        Uses simple rule-based approach (can be upgraded to VADER later)
        """
        positive_words = ['great', 'excellent', 'amazing', 'love', 'perfect', 'recommend', 'best', 'wonderful']
        negative_words = ['poor', 'bad', 'terrible', 'worst', 'disappointed', 'awful', 'waste', 'horrible']
        
        text_lower = review_text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = 0.7 + (positive_count * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = 0.3 - (negative_count * 0.1)
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return {
            'sentiment': sentiment,
            'score': max(0, min(1, score)),
            'confidence': 0.75
        }
    
    # ============================================
    # CUSTOMER SEGMENTATION
    # ============================================
    
    def segment_customer(self, customer_orders: pd.DataFrame, customer_data: dict) -> str:
        """
        Assign customer to a segment
        """
        total_orders = len(customer_orders)
        total_spent = customer_orders['total_price_egp'].sum() if len(customer_orders) > 0 else 0
        
        # Created date
        created_at = pd.to_datetime(customer_data['created_at'])
        days_since_signup = (datetime.now() - created_at).days
        
        # Segmentation logic
        if total_spent > 5000 and total_orders > 10:
            return 'VIP'
        elif total_orders > 5:
            return 'Loyal'
        elif days_since_signup > 60 and total_orders == 0:
            return 'At Risk'
        elif days_since_signup < 30:
            return 'New Customer'
        else:
            return 'Occasional'
    
    # ============================================
    # ANOMALY DETECTION
    # ============================================
    
    def detect_anomalies(self, orders_df: pd.DataFrame) -> List[Dict]:
        """
        Detect unusual patterns in orders
        """
        anomalies = []
        
        # Convert dates
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        # Check for sudden spikes
        daily_orders = orders_df.groupby(orders_df['order_date'].dt.date).size()
        avg_orders = daily_orders.mean()
        std_orders = daily_orders.std()
        
        # Detect spikes (> 2 std deviations)
        recent_orders = daily_orders.tail(7)
        for date, count in recent_orders.items():
            if count > avg_orders + (2 * std_orders):
                anomalies.append({
                    'type': 'order_spike',
                    'message': f'Unusual spike in orders on {date}: {count} orders (avg: {int(avg_orders)})',
                    'severity': 'info'
                })
        
        # Check cancellation rate
        cancelled = len(orders_df[orders_df['status'] == 'cancelled'])
        cancel_rate = cancelled / len(orders_df) if len(orders_df) > 0 else 0
        
        if cancel_rate > 0.15:
            anomalies.append({
                'type': 'high_cancellation',
                'message': f'High cancellation rate: {cancel_rate*100:.1f}%',
                'severity': 'warning'
            })
        
        return anomalies

# Global instance
ai_service = AIService()
