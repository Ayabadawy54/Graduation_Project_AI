"""
Dynamic Pricing Optimizer
Suggests optimal pricing based on demand elasticity
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from datetime import datetime


class PriceOptimizer:
    def __init__(self):
        self.version = "1.0.0"
        self.elasticity_models = {}
        
    def calculate_price_elasticity(self, products_df, orders_df):
        """
        Calculate price elasticity of demand for each category
        """
        print("\n" + "="*60)
        print("CALCULATING PRICE ELASTICITY")
        print("="*60)
        
        # Merge products with orders
        orders_with_price = orders_df.merge(
            products_df[['product_id', 'category', 'price_egp']],
            on='product_id',
            how='left'
        )
        
        elasticities = {}
        
        for category in products_df['category'].unique():
            cat_data = orders_with_price[orders_with_price['category'] == category]
            
            # Group by price ranges
            cat_data['price_bin'] = pd.cut(cat_data['price_egp'], bins=10)
            
            price_demand = cat_data.groupby('price_bin').agg({
                'order_id': 'count',
                'price_egp': 'mean'
            }).dropna()
            
            if len(price_demand) < 3:
                continue
            
            # Calculate elasticity (% change in quantity / % change in price)
            # Using log-log regression
            X = np.log(price_demand['price_egp'].values).reshape(-1, 1)
            y = np.log(price_demand['order_id'].values)
            
            model = LinearRegression()
            model.fit(X, y)
            
            elasticity = model.coef_[0]  # Slope = elasticity
            
            elasticities[category] = {
                'elasticity': round(elasticity, 3),
                'type': 'elastic' if abs(elasticity) > 1 else 'inelastic',
                'avg_price': round(cat_data['price_egp'].mean(), 2),
                'total_orders': len(cat_data)
            }
            
            print(f"\n{category}:")
            print(f"   Elasticity: {elasticity:.3f} ({'elastic' if abs(elasticity) > 1 else 'inelastic'})")
            print(f"   Average price: {cat_data['price_egp'].mean():.2f} EGP")
            print(f"   Total orders: {len(cat_data)}")
        
        return elasticities
    
    def suggest_optimal_price(self, product_data, category_elasticity, competitor_prices=None):
        """
        Suggest optimal price for a product
        """
        current_price = product_data['price_egp']
        category = product_data['category']
        
        if category not in category_elasticity:
            return {
                'current_price': current_price,
                'suggested_price': current_price,
                'reason': 'Insufficient data for optimization',
                'expected_impact': 'Unknown'
            }
        
        elasticity = category_elasticity[category]['elasticity']
        category_avg = category_elasticity[category]['avg_price']
        
        # Simple pricing strategy
        if current_price < category_avg * 0.7:
            # Price is too low
            suggested_price = current_price * 1.15  # Increase by 15%
            reason = f'Price is {((category_avg - current_price) / category_avg * 100):.0f}% below category average'
            impact = '+10-15% revenue (assuming demand stays constant)'
            
        elif current_price > category_avg * 1.3:
            # Price is too high
            suggested_price = current_price * 0.9  # Decrease by 10%
            reason = f'Price is {((current_price - category_avg) / category_avg * 100):.0f}% above category average'
            impact = '+5-10% sales volume'
            
        else:
            # Price is reasonable
            if abs(elasticity) > 1:
                # Elastic demand - small price decrease can boost revenue
                suggested_price = current_price * 0.95
                reason = 'Demand is elastic - small decrease could boost volume significantly'
                impact = '+8-12% total revenue'
            else:
                # Inelastic demand - can increase price
                suggested_price = current_price * 1.05
                reason = 'Demand is inelastic - price increase has minimal impact on sales'
                impact = '+4-6% revenue per unit'
        
        return {
            'current_price': round(current_price, 2),
            'suggested_price': round(suggested_price, 2),
            'category_average': round(category_avg, 2),
            'price_change_pct': round(((suggested_price - current_price) / current_price * 100), 1),
            'reason': reason,
            'expected_impact': impact,
            'elasticity': elasticity,
            'confidence': 'medium'
        }
    
    def analyze_category_pricing(self, products_df, orders_df):
        """
        Comprehensive pricing analysis by category
        """
        print("\nCategory Pricing Analysis:")
        
        results = []
        
        for category in products_df['category'].unique():
            cat_products = products_df[products_df['category'] == category]
            cat_product_ids = cat_products['product_id'].tolist()
            cat_orders = orders_df[orders_df['product_id'].isin(cat_product_ids)]
            
            analysis = {
                'category': category,
                'total_products': len(cat_products),
                'avg_price': round(cat_products['price_egp'].mean(), 2),
                'min_price': round(cat_products['price_egp'].min(), 2),
                'max_price': round(cat_products['price_egp'].max(), 2),
                'total_revenue': round(cat_orders['total_price_egp'].sum(), 2),
                'avg_units_sold': round(cat_products['sales_count'].mean(), 1)
            }
            
            results.append(analysis)
            
            print(f"\n   {category}:")
            print(f"      Price range: {analysis['min_price']} - {analysis['max_price']} EGP")
            print(f"      Average: {analysis['avg_price']} EGP")
            print(f"      Total revenue: {analysis['total_revenue']:.2f} EGP")
        
        return results


def main():
    print("Loading data...")
    products_df = pd.read_csv('mock_data/products.csv', encoding='utf-8-sig')
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    
    optimizer = PriceOptimizer()
    
    # Calculate elasticity
    elasticities = optimizer.calculate_price_elasticity(products_df, orders_df)
    
    # Category analysis
    category_analysis = optimizer.analyze_category_pricing(products_df, orders_df)
    
    # Test price suggestion
    print("\nTesting price optimization...")
    sample_product = products_df.sample(1).iloc[0]
    suggestion = optimizer.suggest_optimal_price(
        sample_product.to_dict(),
        elasticities
    )
    
    print(f"\n   Product: {sample_product['name']}")
    print(f"   Current price: {suggestion['current_price']} EGP")
    print(f"   Suggested price: {suggestion['suggested_price']} EGP ({suggestion['price_change_pct']:+.1f}%)")
    print(f"   Reason: {suggestion['reason']}")
    print(f"   Expected impact: {suggestion['expected_impact']}")
    
    # Save results
    results = {
        'elasticities': elasticities,
        'category_analysis': category_analysis,
        'version': optimizer.version,
        'analyzed_date': datetime.now().isoformat()
    }
    
    with open('ai_models/price_optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("PRICE OPTIMIZATION COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
