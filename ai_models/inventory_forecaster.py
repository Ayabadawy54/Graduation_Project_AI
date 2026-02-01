"""
Inventory Demand Forecaster
Predicts raw material demand for vendors
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json


class InventoryForecaster:
    def __init__(self):
        self.version = "1.0.0"
        
    def forecast_material_demand(self, material_requests_df, materials_df, days_ahead=30):
        """
        Forecast demand for each material
        """
        print("\n" + "="*60)
        print("FORECASTING INVENTORY DEMAND")
        print("="*60)
        
        material_requests_df['request_date'] = pd.to_datetime(material_requests_df['request_date'])
        
        forecasts = []
        
        for material_id in materials_df['material_id'].unique():
            material_orders = material_requests_df[material_requests_df['material_id'] == material_id]
            
            if len(material_orders) == 0:
                continue
            
            # Calculate historical average
            total_quantity = material_orders['quantity'].sum()
            total_days = (material_orders['request_date'].max() - material_orders['request_date'].min()).days
            
            if total_days == 0:
                continue
            
            daily_avg = total_quantity / max(total_days, 1)
            forecasted_demand = daily_avg * days_ahead
            
            # Get material info
            material_info = materials_df[materials_df['material_id'] == material_id].iloc[0]
            
            # Check stock sufficiency
            current_stock = material_info['stock_available']
            stock_shortage = max(0, forecasted_demand - current_stock)
            
            forecasts.append({
                'material_id': material_id,
                'material_name': material_info['name'],
                'category': material_info['category'],
                'current_stock': int(current_stock),
                'forecasted_demand_30d': int(forecasted_demand),
                'daily_avg_demand': round(daily_avg, 2),
                'stock_shortage': int(stock_shortage),
                'needs_restock': stock_shortage > 0,
                'days_until_stockout': int(current_stock / daily_avg) if daily_avg > 0 else 999
            })
        
        forecast_df = pd.DataFrame(forecasts)
        forecast_df = forecast_df.sort_values('stock_shortage', ascending=False)
        
        # Statistics
        needs_restock = len(forecast_df[forecast_df['needs_restock']])
        print(f"\nForecast Summary:")
        print(f"   Materials analyzed: {len(forecast_df)}")
        print(f"   Needs restocking: {needs_restock}")
        
        print(f"\nTop 5 Materials Needing Restock:")
        top_shortage = forecast_df[forecast_df['needs_restock']].head(5)
        for _, material in top_shortage.iterrows():
            print(f"   - {material['material_name']}: Shortage of {material['stock_shortage']} units")
            print(f"     Days until stockout: {material['days_until_stockout']}")
        
        return forecast_df


def main():
    print("Loading data...")
    material_requests_df = pd.read_csv('mock_data/material_requests.csv', encoding='utf-8-sig')
    materials_df = pd.read_csv('mock_data/raw_material_marketplace.csv', encoding='utf-8-sig')
    
    forecaster = InventoryForecaster()
    
    # Generate forecast
    forecast = forecaster.forecast_material_demand(material_requests_df, materials_df, days_ahead=30)
    
    # Save
    forecast.to_csv('ai_models/inventory_forecast_30d.csv', index=False, encoding='utf-8-sig')
    
    # Metadata
    metadata = {
        'model_name': 'Inventory Demand Forecaster',
        'version': forecaster.version,
        'forecast_date': datetime.now().isoformat(),
        'forecast_horizon': '30 days',
        'materials_needing_restock': int(forecast['needs_restock'].sum())
    }
    
    with open('ai_models/inventory_forecaster_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*60)
    print("INVENTORY FORECASTING COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
