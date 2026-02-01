"""
Product Recommendation Engine
Collaborative filtering for product recommendations
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import json
from datetime import datetime
import joblib


class ProductRecommender:
    def __init__(self):
        self.version = "1.0.0"
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.product_features = None
        
    def build_user_item_matrix(self, orders_df):
        """
        Create user-item interaction matrix
        """
        print("\nBuilding user-item interaction matrix...")
        
        # Create matrix: users x products
        interactions = orders_df.groupby(['customer_user_id', 'product_id']).size().reset_index(name='purchases')
        
        self.user_item_matrix = interactions.pivot(
            index='customer_user_id',
            columns='product_id',
            values='purchases'
        ).fillna(0)
        
        print(f"   Matrix shape: {self.user_item_matrix.shape}")
        print(f"   Users: {self.user_item_matrix.shape[0]}")
        print(f"   Products: {self.user_item_matrix.shape[1]}")
        
        return self.user_item_matrix
    
    def calculate_similarity(self):
        """
        Calculate item-item similarity
        """
        print("\nCalculating product similarity...")
        
        # Transpose to get item-item similarity
        item_matrix = self.user_item_matrix.T
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(item_matrix)
        
        print(f"   Similarity matrix shape: {self.similarity_matrix.shape}")
        
        return self.similarity_matrix
    
    def recommend_for_user(self, customer_user_id, n_recommendations=5):
        """
        Recommend products for a specific user
        """
        if customer_user_id not in self.user_item_matrix.index:
            return []
        
        # Get user's purchase history
        user_purchases = self.user_item_matrix.loc[customer_user_id]
        purchased_items = user_purchases[user_purchases > 0].index.tolist()
        
        # Calculate scores for all products
        scores = defaultdict(float)
        
        for purchased_item in purchased_items:
            if purchased_item in self.user_item_matrix.columns:
                item_idx = self.user_item_matrix.columns.get_loc(purchased_item)
                
                # Get similar items
                similar_items = self.similarity_matrix[item_idx]
                
                for idx, score in enumerate(similar_items):
                    product_id = self.user_item_matrix.columns[idx]
                    
                    # Don't recommend already purchased items
                    if product_id not in purchased_items:
                        scores[product_id] += score
        
        # Sort and get top N
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        return [{'product_id': pid, 'score': round(score, 3)} for pid, score in recommendations]
    
    def recommend_similar_products(self, product_id, n_recommendations=5):
        """
        Find similar products (for "Customers also viewed" feature)
        """
        if product_id not in self.user_item_matrix.columns:
            return []
        
        item_idx = self.user_item_matrix.columns.get_loc(product_id)
        similarities = self.similarity_matrix[item_idx]
        
        # Get top similar (excluding itself)
        similar_indices = similarities.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            similar_product_id = self.user_item_matrix.columns[idx]
            recommendations.append({
                'product_id': similar_product_id,
                'similarity_score': round(similarities[idx], 3)
            })
        
        return recommendations
    
    def get_trending_products(self, orders_df, days=7, n_products=10):
        """
        Get trending products based on recent sales velocity
        """
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        cutoff_date = orders_df['order_date'].max() - pd.Timedelta(days=days)
        
        recent_orders = orders_df[orders_df['order_date'] >= cutoff_date]
        
        trending = recent_orders.groupby('product_id').size().reset_index(name='recent_sales')
        trending = trending.sort_values('recent_sales', ascending=False).head(n_products)
        
        return trending.to_dict(orient='records')
    
    def save(self, filepath='ai_models/product_recommender_v1.pkl'):
        """Save recommendation engine"""
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'similarity_matrix': self.similarity_matrix,
            'version': self.version,
            'trained_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nRecommender saved to: {filepath}")


def main():
    print("\n" + "="*60)
    print("TRAINING PRODUCT RECOMMENDATION ENGINE")
    print("="*60)
    
    # Load data
    print("Loading data...")
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    products_df = pd.read_csv('mock_data/products.csv', encoding='utf-8-sig')
    
    # Initialize recommender
    recommender = ProductRecommender()
    
    # Build matrices
    recommender.build_user_item_matrix(orders_df)
    recommender.calculate_similarity()
    
    # Test recommendations
    print("\nTesting recommendations...")
    sample_customer = orders_df['customer_user_id'].iloc[0]
    recommendations = recommender.recommend_for_user(sample_customer, n_recommendations=5)
    
    print(f"\n   Recommendations for {sample_customer}:")
    for i, rec in enumerate(recommendations, 1):
        product = products_df[products_df['product_id'] == rec['product_id']]
        product_name = product.iloc[0]['name'] if len(product) > 0 else 'Unknown'
        print(f"   {i}. {product_name} (score: {rec['score']})")
    
    # Get trending
    print("\nTop 5 Trending Products (last 7 days):")
    trending = recommender.get_trending_products(orders_df, days=7, n_products=5)
    for i, item in enumerate(trending, 1):
        product = products_df[products_df['product_id'] == item['product_id']]
        product_name = product.iloc[0]['name'] if len(product) > 0 else 'Unknown'
        print(f"   {i}. {product_name} ({item['recent_sales']} sales)")
    
    # Save
    recommender.save()
    
    # Metadata
    metadata = {
        'model_name': 'Product Recommender',
        'version': recommender.version,
        'trained_date': datetime.now().isoformat(),
        'total_users': recommender.user_item_matrix.shape[0],
        'total_products': recommender.user_item_matrix.shape[1],
        'sparsity': round(1 - (recommender.user_item_matrix.astype(bool).sum().sum() / recommender.user_item_matrix.size), 3)
    }
    
    with open('ai_models/product_recommender_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("RECOMMENDATION ENGINE COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
