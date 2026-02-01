"""
Vendors and raw materials endpoints
"""
from fastapi import APIRouter, HTTPException
import pandas as pd

from api.services.data_service import data_service

router = APIRouter()

@router.get("/vendors")
async def get_vendors():
    """
    Get all static vendors
    """
    vendors_df = data_service.get_vendors()
    return vendors_df.to_dict(orient='records')

@router.get("/vendors/{vendor_id}")
async def get_vendor_detail(vendor_id: str):
    """
    Get vendor details with performance metrics
    """
    vendors_df = data_service.get_vendors()
    vendor = vendors_df[vendors_df['vendor_id'] == vendor_id]
    
    if len(vendor) == 0:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    vendor_dict = vendor.iloc[0].to_dict()
    
    # Get materials
    materials_df = data_service.get_materials()
    vendor_materials = materials_df[materials_df['vendor_id'] == vendor_id]
    
    # Get requests
    requests_df = data_service.get_material_requests()
    vendor_requests = requests_df[requests_df['vendor_id'] == vendor_id]
    
    return {
        **vendor_dict,
        'total_materials': len(vendor_materials),
        'total_requests': len(vendor_requests),
        'total_sales_egp': round(vendor_requests['total_price_egp'].sum(), 2)
    }

@router.get("/raw-materials")
async def get_raw_materials():
    """
    Get all raw materials
    """
    materials_df = data_service.get_materials()
    return materials_df.to_dict(orient='records')

@router.get("/raw-materials/demand-forecast")
async def get_material_demand_forecast():
    """
    Forecast material demand
    """
    requests_df = data_service.get_material_requests()
    materials_df = data_service.get_materials()
    
    # Group by material
    demand_by_material = requests_df.groupby('material_id').agg({
        'quantity': 'sum',
        'request_id': 'count'
    }).reset_index()
    
    demand_by_material.columns = ['material_id', 'total_quantity_ordered', 'total_requests']
    
    # Merge with material names
    demand_with_names = demand_by_material.merge(
        materials_df[['material_id', 'name', 'category']], 
        on='material_id'
    )
    
    # Sort by demand
    demand_with_names = demand_with_names.sort_values('total_quantity_ordered', ascending=False)
    
    return demand_with_names.head(20).to_dict(orient='records')
