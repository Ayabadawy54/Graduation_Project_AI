"""
Products management endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd

from api.services.data_service import data_service
from api.services.ai_service import ai_service
from api.models.schemas import ProductDetail, ProductApproval

router = APIRouter()

@router.get("/products")
async def get_products(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Get list of products with filters
    """
    products_df = data_service.get_products(status=status, category=category)
    
    if brand_id:
        products_df = products_df[products_df['brand_id'] == brand_id]
    
    products_list = products_df.head(limit).to_dict(orient='records')
    return products_list

# ⚠️ IMPORTANT: All static routes MUST come before /{product_id} to avoid routing conflicts
@router.get("/products/pending-approval")
async def get_pending_products():
    """
    Get all products pending approval with AI recommendations
    """
    products_df = data_service.get_products(status='pending')
    brands_df = data_service.get_brands()
    
    pending_with_analysis = []
    
    for _, product in products_df.iterrows():
        product_dict = product.to_dict()
        
        # Get brand
        brand = brands_df[brands_df['brand_id'] == product['brand_id']]
        if len(brand) == 0:
            continue
        brand_dict = brand.iloc[0].to_dict()
        
        # Quality assessment
        quality_analysis = ai_service.calculate_product_quality_score(product_dict, brand_dict)
        
        pending_with_analysis.append({
            **product_dict,
            'quality_score': quality_analysis['quality_score'],
            'approval_recommendation': quality_analysis['approval_action'],
            'suggestions': quality_analysis['suggestions'],
            'brand_name': brand_dict['business_name']
        })
    
    # Sort by quality score (highest first for quick approval)
    pending_with_analysis.sort(key=lambda x: x['quality_score'], reverse=True)
    
    return pending_with_analysis

@router.get("/products/analytics/trending")
async def get_trending_products(limit: int = 10):
    """
    Get trending products based on view velocity
    """
    products_df = data_service.get_products(status='approved')
    
    # Calculate trend score (views + clicks * 2)
    products_df['trend_score'] = products_df['views'] + (products_df['clicks'] * 2)
    
    # Sort and get top
    trending = products_df.nlargest(limit, 'trend_score')
    
    return trending[['product_id', 'name', 'category', 'price_egp', 'views', 'clicks', 'trend_score']].to_dict(orient='records')

@router.get("/products/analytics/pricing-analysis")
async def get_pricing_analysis():
    """
    Analyze product pricing across categories
    """
    products_df = data_service.get_products(status='approved')
    
    categories = products_df['category'].unique()
    analysis = []
    
    for category in categories:
        cat_products = products_df[products_df['category'] == category]
        
        analysis.append({
            'category': category,
            'avg_price_egp': round(cat_products['price_egp'].mean(), 2),
            'min_price_egp': round(cat_products['price_egp'].min(), 2),
            'max_price_egp': round(cat_products['price_egp'].max(), 2),
            'total_products': len(cat_products)
        })
    
    return analysis

@router.get("/products/{product_id}", response_model=ProductDetail)
async def get_product_detail(product_id: str):
    """
    Get detailed product information with AI quality assessment
    """
    product = data_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get brand info
    brand = data_service.get_brand_by_id(product['brand_id'])
    
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found for this product")
    
    # Calculate quality score
    quality_analysis = ai_service.calculate_product_quality_score(product, brand)
    
    return {
        'product_id': product['product_id'],
        'brand_id': product['brand_id'],
        'name': product['name'],
        'category': product['category'],
        'price_egp': product['price_egp'],
        'stock_quantity': product['stock_quantity'],
        'status': product['status'],
        'quality_score': quality_analysis['quality_score'],
        'approval_recommendation': quality_analysis['approval_action'],
        'suggestions': quality_analysis['suggestions']
    }

@router.post("/products/{product_id}/approve")
async def approve_product(product_id: str, approval: ProductApproval):
    """
    Approve or reject a product
    """
    product = data_service.get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        'success': True,
        'product_id': product_id,
        'action': approval.action,
        'message': f"Product {approval.action}d successfully"
    }
