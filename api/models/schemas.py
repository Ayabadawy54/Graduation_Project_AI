"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================
# RESPONSE MODELS
# ============================================

class DashboardOverview(BaseModel):
    total_owners: int
    active_owners: int
    total_customers: int
    total_orders: int
    total_revenue_egp: float
    sales_trend: str
    high_risk_brands: int
    pending_approvals: int
    top_recommendations: List[str]
    alerts: List[dict]

class CategoryPerformance(BaseModel):
    category: str
    total_sales_egp: float
    total_orders: int
    avg_order_value_egp: float
    growth_trend: str
    active_brands: int

class BrandDetail(BaseModel):
    brand_id: str
    owner_user_id: str
    business_name: str
    category: str
    verified: bool
    total_sales_egp: float
    total_orders: int
    avg_rating: float
    rating_count: int
    risk_score: float
    risk_level: str
    ai_insights: List[str]

class ProductDetail(BaseModel):
    product_id: str
    brand_id: str
    name: str
    category: str
    price_egp: float
    stock_quantity: int
    status: str
    quality_score: float
    approval_recommendation: str
    suggestions: List[str]

class OrderForecast(BaseModel):
    date: str
    predicted_orders: int
    confidence_low: int
    confidence_high: int
    factors: List[str]

class OwnerRiskAnalysis(BaseModel):
    brand_id: str
    business_name: str
    risk_score: float
    risk_level: str
    risk_factors: List[str]
    recommendations: List[str]

# ============================================
# REQUEST MODELS
# ============================================

class ProductApproval(BaseModel):
    product_id: str
    action: str  # approve / reject
    reason: Optional[str] = None

class BrandVerification(BaseModel):
    brand_id: str
    verified: bool
    reason: Optional[str] = None
