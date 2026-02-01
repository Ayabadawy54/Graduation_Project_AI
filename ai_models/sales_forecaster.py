"""
Sales Forecasting Model
Predicts future order volumes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib


class SalesForecaster:
    def __init__(self):
        self.version = "1.0.0"
        self.model = None
        
    def prepare_time_series(self, orders_df, category=None):
        """
        Prepare time series data for forecasting
        """
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        
        # Filter by category if specified
        if category:
            products_df = pd.read_csv('mock_data/products.csv', encoding='utf-8-sig')
            cat_products = products_df[products_df['category'] == category]
            orders_df = orders_df[orders_df['product_id'].isin(cat_products['product_id'])]
        
        # Group by date
        daily_orders = orders_df.groupby(orders_df['order_date'].dt.date).agg({
            'order_id': 'count',
            'total_price_egp': 'sum'
        }).reset_index()
        
        daily_orders.columns = ['date', 'orders', 'revenue']
        daily_orders['date'] = pd.to_datetime(daily_orders['date'])
        
        # Add time features
        daily_orders['day_of_week'] = daily_orders['date'].dt.dayofweek
        daily_orders['is_weekend'] = daily_orders['day_of_week'].isin([4, 5]).astype(int)  # Friday, Saturday
        daily_orders['day_of_month'] = daily_orders['date'].dt.day
        
        return daily_orders
    
    def train(self, time_series_df):
        """
        Train simple forecasting model
        """
        print("\n" + "="*60)
        print("TRAINING SALES FORECASTING MODEL")
        print("="*60)
        
        # Features
        X = time_series_df[['day_of_week', 'is_weekend', 'day_of_month']].values
        y = time_series_df['orders'].values
        
        print(f"\nTraining on {len(X)} days of data")
        
        # Train
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Evaluate
        y_pred = self.model.predict(X)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        print(f"\nModel Performance:")
        print(f"   Mean Absolute Error: {mae:.2f} orders/day")
        print(f"   Root Mean Squared Error: {rmse:.2f} orders/day")
        print(f"   Average daily orders: {y.mean():.2f}")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'avg_orders': float(y.mean())
        }
    
    def forecast(self, days=7):
        """
        Forecast next N days
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        forecasts = []
        last_date = datetime.now()
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            
            # Create features
            features = np.array([[
                forecast_date.weekday(),
                1 if forecast_date.weekday() in [4, 5] else 0,
                forecast_date.day
            ]])
            
            # Predict
            predicted_orders = self.model.predict(features)[0]
            
            # Add some randomness for confidence interval
            std_dev = predicted_orders * 0.15
            
            forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_orders': int(max(0, predicted_orders)),
                'confidence_low': int(max(0, predicted_orders - std_dev)),
                'confidence_high': int(predicted_orders + std_dev),
                'day_of_week': forecast_date.strftime('%A')
            })
        
        return forecasts
    
    def save(self, filepath='ai_models/sales_forecaster_v1.pkl'):
        """
        Save model
        """
        if self.model is None:
            raise ValueError("No model to save!")
        
        model_data = {
            'model': self.model,
            'version': self.version,
            'trained_date': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")


def main():
    """
    Train and test forecasting model
    """
    # Load data
    print("Loading orders data...")
    orders_df = pd.read_csv('mock_data/orders.csv', encoding='utf-8-sig')
    
    # Initialize forecaster
    forecaster = SalesForecaster()
    
    # Prepare data
    print("Preparing time series...")
    time_series = forecaster.prepare_time_series(orders_df)
    
    # Train
    metrics = forecaster.train(time_series)
    
    # Forecast
    print("\nGenerating 7-day forecast...")
    forecast = forecaster.forecast(days=7)
    
    print("\nForecast:")
    for day in forecast:
        print(f"   {day['date']} ({day['day_of_week']}): {day['predicted_orders']} orders (range: {day['confidence_low']}-{day['confidence_high']})")
    
    # Save
    forecaster.save()
    
    # Save forecast
    forecast_df = pd.DataFrame(forecast)
    forecast_df.to_csv('ai_models/sales_forecast_7day.csv', index=False)
    
    # Metadata
    metadata = {
        'model_name': 'Sales Forecaster',
        'version': forecaster.version,
        'trained_date': datetime.now().isoformat(),
        'performance': metrics,
        'forecast_horizon': '7 days'
    }
    
    with open('ai_models/sales_forecaster_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("SALES FORECASTING COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
