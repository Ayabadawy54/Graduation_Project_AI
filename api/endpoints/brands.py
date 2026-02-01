"""
Brands (Owners) management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd

from api.services.data_service import data_service
from api.services.ai_service import ai_service
from api.models.schemas import BrandDetail, OwnerRiskAnalysis

router = APIRouter()

@router.get("/brands")
async def get_brands(
    category: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Get list of brands with filters
    """
    brands_df = data_service.get_brands(category=category, verified=verified)
    orders_df = data_service.get_orders()
    reviews_df = data_service.get_reviews()
    
    # Calculate risk scores for all brands
    brands_with_risk = []
    for _, brand in brands_df.iterrows():
        brand_dict = brand.to_dict()
        risk_analysis = ai_service.calculate_brand_risk_score(brand_dict, orders_df, reviews_df)
        
        brand_dict['risk_score'] = risk_analysis['risk_score']
        brand_dict['risk_level'] = risk_analysis['risk_level']
        
        # Filter by risk level if specified
        if risk_level and risk_analysis['risk_level'] != risk_level.lower():
            continue
        
        brands_with_risk.append(brand_dict)
    
    # Limit results
    return brands_with_risk[:limit]

@router.get("/brands/{brand_id}", response_model=BrandDetail)
async def get_brand_detail(brand_id: str):
    """
    Get detailed brand information with AI insights
    """
    brand = data_service.get_brand_by_id(brand_id)
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    orders_df = data_service.get_orders()
    reviews_df = data_service.get_reviews()
    
    # Calculate risk analysis
    risk_analysis = ai_service.calculate_brand_risk_score(brand, orders_df, reviews_df)
    
    # Generate AI insights
    ai_insights = [
        f"Brand has {brand['total_orders']} total orders",
        f"Average rating: {brand['avg_rating']}/5.0",
        f"Total revenue: {brand['total_sales_egp']:.2f} EGP"
    ]
    
    if brand['verified']:
        ai_insights.append("✅ Verified brand - eligible for premium features")
    else:
        ai_insights.append("⚠️ Not verified - recommend completing verification")
    
    ai_insights.extend(risk_analysis['recommendations'])
    
    return {
        **brand,
        'risk_score': risk_analysis['risk_score'],
        'risk_level': risk_analysis['risk_level'],
        'ai_insights': ai_insights
    }

@router.get("/brands/analytics/risk-analysis", response_model=List[OwnerRiskAnalysis])
async def get_risk_analysis():
    """
    Get all high and medium risk brands
    """
    brands_df = data_service.get_brands()
    orders_df = data_service.get_orders()
    reviews_df = data_service.get_reviews()
    
    risky_brands = []
    
    for _, brand in brands_df.iterrows():
        brand_dict = brand.to_dict()
        risk_analysis = ai_service.calculate_brand_risk_score(brand_dict, orders_df, reviews_df)
        
        if risk_analysis['risk_level'] in ['high', 'medium']:
            risky_brands.append({
                'brand_id': brand['brand_id'],
                'business_name': brand['business_name'],
                'risk_score': risk_analysis['risk_score'],
                'risk_level': risk_analysis['risk_level'],
                'risk_factors': risk_analysis['risk_factors'],
                'recommendations': risk_analysis['recommendations']
            })
    
    # Sort by risk score (highest first)
    risky_brands.sort(key=lambda x: x['risk_score'], reverse=True)
    
    return risky_brands
