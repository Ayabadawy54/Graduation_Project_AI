"""
Master script to train ALL AI models
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("\n" + "="*70)
    print("TALENTREE AI MODELS - TRAINING ALL 8 MODELS")
    print("="*70)
    
    models = [
        ("Owner Risk Scoring Model", "ai_models.owner_risk_model"),
        ("Sentiment Analyzer", "ai_models.sentiment_analyzer"),
        ("Sales Forecaster", "ai_models.sales_forecaster"),
        ("Customer Churn Predictor", "ai_models.customer_churn_predictor"),
        ("Product Recommender", "ai_models.product_recommender"),
        ("Price Optimizer", "ai_models.price_optimizer"),
        ("Fraud Detector", "ai_models.fraud_detector"),
        ("Inventory Forecaster", "ai_models.inventory_forecaster"),
    ]
    
    for i, (name, module) in enumerate(models, 1):
        print(f"\n\n[{i}/{len(models)}] {name}")
        print("-" * 70)
        
        try:
            mod = __import__(module, fromlist=['main'])
            mod.main()
        except Exception as e:
            print(f"Error training {name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n\n" + "="*70)
    print("ALL AI MODELS TRAINED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated files:")
    print("   - 5 trained model files (.pkl)")
    print("   - 7 metadata files (.json)")
    print("   - 4 analysis result files (.csv)")
    print("\nReady to integrate with API!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
