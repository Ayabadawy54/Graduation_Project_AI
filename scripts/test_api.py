"""
Quick test script for the API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("\n" + "="*60)
    print("🧪 Testing TalentTree API Endpoints")
    print("="*60 + "\n")
    
    try:
        # Test health check
        print("1. Testing health check...")
        response = requests.get(f"{BASE_URL}/health")
        print(f"   ✅ Health: {response.json()}\n")
        
        # Test dashboard overview
        print("2. Testing dashboard overview...")
        response = requests.get(f"{BASE_URL}/api/dashboard/overview")
        data = response.json()
        print(f"   ✅ Total Orders: {data['total_orders']}")
        print(f"   ✅ Total Revenue: {data['total_revenue_egp']:.2f} EGP")
        print(f"   ✅ Sales Trend: {data['sales_trend']}")
        print(f"   ✅ High Risk Brands: {data['high_risk_brands']}\n")
        
        # Test category performance
        print("3. Testing category performance...")
        response = requests.get(f"{BASE_URL}/api/dashboard/category-performance")
        categories = response.json()
        for cat in categories:
            print(f"   ✅ {cat['category']}: {cat['total_sales_egp']:.2f} EGP ({cat['total_orders']} orders)")
        print()
        
        # Test brands
        print("4. Testing brands list...")
        response = requests.get(f"{BASE_URL}/api/brands?limit=5")
        brands = response.json()
        print(f"   ✅ Retrieved {len(brands)} brands")
        if brands:
            print(f"   ✅ First brand: {brands[0]['business_name']} (Risk: {brands[0]['risk_level']})\n")
        
        # Test risk analysis
        print("5. Testing risk analysis...")
        response = requests.get(f"{BASE_URL}/api/brands/analytics/risk-analysis")
        risky = response.json()
        print(f"   ✅ Found {len(risky)} risky brands")
        if risky:
            print(f"   ✅ Highest risk: {risky[0]['business_name']} (Score: {risky[0]['risk_score']})\n")
        
        # Test products
        print("6. Testing products...")
        response = requests.get(f"{BASE_URL}/api/products?limit=5")
        products = response.json()
        print(f"   ✅ Retrieved {len(products)} products\n")
        
        # Test forecast
        print("7. Testing order forecast...")
        response = requests.get(f"{BASE_URL}/api/analytics/forecast/orders?days=7")
        forecast = response.json()
        print(f"   ✅ Forecast for next {len(forecast)} days")
        if forecast:
            print(f"   ✅ Next day prediction: {forecast[0]['predicted_orders']} orders\n")
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API. Make sure the server is running.")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_api()
