"""
Talentree AI - Model Training Script
=====================================
Trains 4 ML models from the CSV training data and saves them as .pkl files.

Models:
  1. Churn Prediction      - XGBoost Classifier
  2. Fraud Detection       - XGBoost Classifier (with SMOTE for imbalance)  
  3. Anomaly Detection     - Isolation Forest (unsupervised)
  4. Demand Forecasting    - Linear Regression per product (lightweight)

All models are saved to: talentree-ai/models/
"""

import pandas as pd
import numpy as np
import os
import sys
import pickle
import json
from datetime import datetime

# Sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, mean_absolute_error
)
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LinearRegression

# XGBoost
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("[WARN] XGBoost not installed, using RandomForest as fallback")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "data", "csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def save_model(model, filename, metadata=None):
    """Save model as .pkl with optional metadata JSON."""
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"  Model saved -> {path}")

    if metadata:
        meta_path = path.replace(".pkl", "_meta.json")
        metadata["saved_at"] = datetime.now().isoformat()
        metadata["filename"] = filename
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"  Metadata saved -> {meta_path}")


# ============================================================
# 1. CHURN MODEL
# ============================================================
def train_churn_model():
    print("\n" + "=" * 60)
    print("  Training Churn Prediction Model")
    print("=" * 60)

    df = pd.read_csv(os.path.join(CSV_DIR, "churn_training.csv"))
    print(f"  Dataset: {len(df)} rows, churn rate: {df['is_churned'].mean():.1%}")

    # Features and target
    feature_cols = [c for c in df.columns if c != "is_churned"]
    X = df[feature_cols]
    y = df["is_churned"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    if HAS_XGBOOST:
        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=3,  # Handle imbalance
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        )
        model.fit(X_train_scaled, y_train, verbose=False)
    else:
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=6,
            class_weight="balanced",
            random_state=42,
        )
        model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print(f"\n  Results:")
    print(f"    Accuracy:  {accuracy:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1 Score:  {f1:.4f}")

    # Save model + scaler together
    model_bundle = {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
    }
    save_model(model_bundle, "churn_model.pkl", {
        "model_type": "XGBoost" if HAS_XGBOOST else "RandomForest",
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "training_rows": len(X_train),
        "features": feature_cols,
        "data_source": "synthetic",
    })

    return accuracy


# ============================================================
# 2. FRAUD MODEL
# ============================================================
def train_fraud_model():
    print("\n" + "=" * 60)
    print("  Training Fraud Detection Model")
    print("=" * 60)

    df = pd.read_csv(os.path.join(CSV_DIR, "fraud_training.csv"))
    print(f"  Dataset: {len(df)} rows, fraud rate: {df['is_fraud'].mean():.1%}")

    feature_cols = [c for c in df.columns if c != "is_fraud"]
    X = df[feature_cols]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Handle class imbalance with higher weight for fraud class
    if HAS_XGBOOST:
        fraud_ratio = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
        model = XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            scale_pos_weight=fraud_ratio,
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        )
        model.fit(X_train_scaled, y_train, verbose=False)
    else:
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=5,
            class_weight="balanced",
            random_state=42,
        )
        model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n  Results:")
    print(f"    Accuracy:  {accuracy:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1 Score:  {f1:.4f}")

    model_bundle = {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
    }
    save_model(model_bundle, "fraud_model.pkl", {
        "model_type": "XGBoost" if HAS_XGBOOST else "RandomForest",
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "training_rows": len(X_train),
        "features": feature_cols,
        "data_source": "synthetic",
    })

    return accuracy


# ============================================================
# 3. ANOMALY DETECTION MODEL
# ============================================================
def train_anomaly_model():
    print("\n" + "=" * 60)
    print("  Training Anomaly Detection Model")
    print("=" * 60)

    df = pd.read_csv(os.path.join(CSV_DIR, "anomaly_training.csv"))
    print(f"  Dataset: {len(df)} rows, anomaly rate: {df['is_anomaly'].mean():.1%}")

    feature_cols = [c for c in df.columns if c != "is_anomaly"]
    X = df[feature_cols]
    y_true = df["is_anomaly"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Isolation Forest (unsupervised)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,  # Match our 5% anomaly rate
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    # Evaluate: IsolationForest returns -1 for anomalies, 1 for normal
    y_pred_raw = model.predict(X_scaled)
    y_pred = (y_pred_raw == -1).astype(int)  # Convert to 0/1

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"\n  Results:")
    print(f"    Accuracy:  {accuracy:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1 Score:  {f1:.4f}")

    model_bundle = {
        "model": model,
        "scaler": scaler,
        "feature_cols": feature_cols,
    }
    save_model(model_bundle, "anomaly_model.pkl", {
        "model_type": "IsolationForest",
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "training_rows": len(X),
        "features": feature_cols,
        "data_source": "synthetic",
    })

    return accuracy


# ============================================================
# 4. DEMAND FORECASTING MODEL
# ============================================================
def train_demand_model():
    print("\n" + "=" * 60)
    print("  Training Demand Forecasting Model")
    print("=" * 60)

    df = pd.read_csv(os.path.join(CSV_DIR, "demand_training.csv"))
    print(f"  Dataset: {len(df)} rows, {df['product_id'].nunique()} products")

    feature_cols = ["week_number", "month", "avg_price", "promotion_active",
                    "seasonal_factor", "views_count"]
    target_col = "units_sold"

    # Train one model per product for better accuracy
    models = {}
    total_mae = 0
    n_products = 0

    for pid in df["product_id"].unique():
        pdf = df[df["product_id"] == pid]

        X = pdf[feature_cols]
        y = pdf[target_col]

        # Use last 8 weeks as test
        X_train, X_test = X.iloc[:-8], X.iloc[-8:]
        y_train, y_test = y.iloc[:-8], y.iloc[-8:]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        total_mae += mae
        n_products += 1

        models[pid] = {
            "model": model,
            "scaler": scaler,
        }

    avg_mae = total_mae / max(n_products, 1)
    print(f"\n  Results:")
    print(f"    Products trained: {n_products}")
    print(f"    Avg MAE: {avg_mae:.2f} units")

    demand_bundle = {
        "models": models,
        "feature_cols": feature_cols,
    }
    save_model(demand_bundle, "demand_model.pkl", {
        "model_type": "LinearRegression (per product)",
        "avg_mae": round(avg_mae, 2),
        "products_trained": n_products,
        "features": feature_cols,
        "data_source": "synthetic",
    })

    return avg_mae


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  Talentree AI - Model Training")
    print("  Training from CSV files in data/csv/")
    print("=" * 60)

    results = {}

    churn_acc = train_churn_model()
    results["churn"] = churn_acc

    fraud_acc = train_fraud_model()
    results["fraud"] = fraud_acc

    anomaly_acc = train_anomaly_model()
    results["anomaly"] = anomaly_acc

    demand_mae = train_demand_model()
    results["demand_mae"] = demand_mae

    print("\n" + "=" * 60)
    print("  [OK] ALL MODELS TRAINED!")
    print("=" * 60)
    print(f"  Churn Model:   {results['churn']:.1%} accuracy")
    print(f"  Fraud Model:   {results['fraud']:.1%} accuracy")
    print(f"  Anomaly Model: {results['anomaly']:.1%} accuracy")
    print(f"  Demand Model:  {results['demand_mae']:.2f} MAE")
    print("=" * 60)

    # List saved models
    print("\nSaved models:")
    for f in sorted(os.listdir(MODELS_DIR)):
        size = os.path.getsize(os.path.join(MODELS_DIR, f))
        print(f"  {f:30s} {size/1024:.1f} KB")


if __name__ == "__main__":
    main()
