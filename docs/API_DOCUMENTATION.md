# 🚀 TalentTree Admin Dashboard API Documentation

## Overview

The TalentTree Admin Dashboard API is a comprehensive FastAPI application with AI-powered analytics for managing an Egyptian handmade marketplace.

## 🎯 Key Features

- **AI-Powered Risk Scoring**: Brand risk assessment with automated recommendations
- **Product Quality Analysis**: Automated product approval suggestions
- **Sales Forecasting**: Predictive analytics for order volumes
- **Sentiment Analysis**: Review sentiment detection
- **Egyptian Context**: Governorate-based analytics and Egyptian business patterns

## 📡 API Endpoints

### Dashboard Endpoints

#### GET /api/dashboard/overview
Get complete dashboard overview with metrics and AI insights.

**Response:**
```json
{
  "total_owners": 100,
  "active_owners": 95,
  "total_customers": 500,
  "total_orders": 2000,
  "total_revenue_egp": 1234567.89,
  "sales_trend": "↑ 15.3%",
  "high_risk_brands": 5,
  "pending_approvals": 25,
  "top_recommendations": [
    "Platform performing normally - no urgent actions"
  ],
  "alerts": [
    {
      "type": "info",
      "message": "No anomalies detected",
      "severity": "info"
    }
  ]
}
```

#### GET /api/dashboard/category-performance
Get sales performance by product category.

**Response:**
```json
[
  {
    "category": "Fashion & Accessories",
    "total_sales_egp": 450000.00,
    "total_orders": 800,
    "avg_order_value_egp": 562.50,
    "growth_trend": "→ 5%",
    "active_brands": 33
  }
]
```

### Brands Endpoints

#### GET /api/brands
Get list of brands with optional filters.

**Query Parameters:**
- `category` (optional): Filter by category
- `risk_level` (optional): Filter by risk level (low/medium/high)
- `verified` (optional): Filter by verification status
- `limit` (default: 50): Maximum results to return

**Example:**
```
GET /api/brands?category=Fashion%20%26%20Accessories&limit=10
```

#### GET /api/brands/{brand_id}
Get detailed information about a specific brand.

**Response:**
```json
{
  "brand_id": "BRAND0001",
  "owner_user_id": "USER00002",
  "business_name": "Style Studio",
  "category": "Fashion & Accessories",
  "verified": true,
  "total_sales_egp": 17418.41,
  "total_orders": 206,
  "avg_rating": 4.3,
  "rating_count": 22,
  "risk_score": 0.25,
  "risk_level": "low",
  "ai_insights": [
    "Brand has 206 total orders",
    "Average rating: 4.3/5.0",
    "Total revenue: 17418.41 EGP",
    "✅ Verified brand - eligible for premium features",
    "Brand performing well"
  ]
}
```

#### GET /api/brands/analytics/risk-analysis
Get all high and medium risk brands sorted by risk score.

### Products Endpoints

#### GET /api/products
Get list of products with filters.

**Query Parameters:**
- `status` (optional): Filter by status (pending/approved/rejected)
- `category` (optional): Filter by category
- `limit` (default: 50): Maximum results to return

#### GET /api/products/{product_id}
Get detailed product information with AI quality assessment.

**Response:**
```json
{
  "product_id": "PROD00001",
  "brand_id": "BRAND0001",
  "name": "Leather Tote Bag",
  "category": "Fashion & Accessories",
  "price_egp": 450.00,
  "stock_quantity": 25,
  "status": "approved",
  "quality_score": 0.85,
  "approval_recommendation": "auto_approve",
  "suggestions": [
    "Product meets quality standards"
  ]
}
```

#### GET /api/products/pending/queue
Get products awaiting approval, sorted by quality score.

### Analytics Endpoints

#### GET /api/analytics/forecast/orders
Forecast order volume for next N days.

**Query Parameters:**
- `days` (default: 7, max: 30): Number of days to forecast
- `category` (optional): Filter by category

**Response:**
```json
[
  {
    "date": "2026-02-01",
    "predicted_orders": 12,
    "confidence_low": 10,
    "confidence_high": 14,
    "factors": [
      "Weekend pattern",
      "Based on 180 days of history"
    ]
  }
]
```

#### GET /api/analytics/sales/trends
Get sales trends over time.

**Query Parameters:**
- `period` (daily/weekly/monthly): Aggregation period

#### GET /api/analytics/reviews/sentiment
Analyze sentiment distribution of all reviews.

#### GET /api/analytics/governorates/performance
Get sales performance by Egyptian governorate.

## 🚀 Running the API

### Start the Server

```bash
cd c:\Users\MAI\Talentree-Admin-Dashboard
python main.py
```

The API will start on `http://localhost:8000`

### Test the API

```bash
python scripts/test_api.py
```

### Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Data Loading

The API automatically loads all 12 CSV files on startup:

- ✅ users.csv (600 records)
- ✅ brands.csv (100 records)
- ✅ products.csv (500 records)
- ✅ orders.csv (2,000 records)
- ✅ payments.csv (2,000 records)
- ✅ reviews.csv (400 records)
- ✅ static_vendors.csv (10 records)
- ✅ raw_material_marketplace.csv (50 records)
- ✅ material_requests.csv (200 records)
- ✅ support_tickets.csv (150 records)
- ✅ admin_actions.csv (200 records)
- ✅ analytics_snapshots.csv (180 records)

## 🤖 AI Features

### 1. Brand Risk Scoring
- Calculates risk based on return rate, fulfillment rate, ratings
- Provides actionable recommendations
- Classifies as low/medium/high risk

### 2. Product Quality Assessment
- Evaluates listing quality
- Recommends auto-approve/manual-review/auto-reject
- Provides improvement suggestions

### 3. Sales Forecasting
- Predicts order volume
- Accounts for day-of-week patterns
- Provides confidence intervals

### 4. Sentiment Analysis
- Analyzes review sentiment (positive/neutral/negative)
- Calculates sentiment scores
- Aggregates sentiment distribution

### 5. Anomaly Detection
- Detects unusual order spikes
- Identifies high cancellation rates
- Alerts admins to issues

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.109.0
- **Data Processing**: Pandas 2.1.4
- **AI/ML**: NumPy, custom algorithms
- **Server**: Uvicorn 0.27.0
- **Validation**: Pydantic 2.5.3

## 📝 Environment

- **Platform**: Windows
- **Python**: 3.12+
- **Port**: 8000
- **CORS**: Enabled for all origins (configure for production)

## 🔧 API Structure

```
api/
├── __init__.py
├── endpoints/
│   ├── __init__.py
│   ├── dashboard.py      # Dashboard metrics
│   ├── brands.py          # Brand management
│   ├── products.py        # Product management
│   └── analytics.py       # Analytics & forecasting
├── services/
│   ├── __init__.py
│   ├── data_service.py    # CSV data access
│   └── ai_service.py      # AI algorithms
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
└── utils/
    ├── __init__.py
    └── egyptian_context.py # Egyptian utilities
```

## 📈 Next Steps

After the API is running, you can:

1. Build a frontend dashboard (React/Vue/Streamlit)
2. Integrate advanced ML models (saved .pkl files)
3. Add authentication and authorization
4. Deploy to cloud (AWS/Azure/Heroku)
5. Add WebSocket support for real-time updates

---

**Status**: ✅ API READY FOR USE
**Version**: 1.0.0
**Last Updated**: January 31, 2026
