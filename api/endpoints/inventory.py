"""
Inventory management endpoints
"""
from fastapi import APIRouter, Query
import pandas as pd

from api.services.data_service import data_service

router = APIRouter()


@router.get("/inventory/overview")
async def get_inventory_overview():
    """
    Platform-wide stock health overview.
    """
    products_df = data_service.get_products(status='approved')

    total_products = len(products_df)
    out_of_stock = len(products_df[products_df['stock_quantity'] == 0])
    low_stock = len(products_df[(products_df['stock_quantity'] > 0) & (products_df['stock_quantity'] <= 10)])
    healthy_stock = len(products_df[products_df['stock_quantity'] > 10])

    total_stock_units = int(products_df['stock_quantity'].sum())
    avg_stock_per_product = round(products_df['stock_quantity'].mean(), 1)

    # Stock value estimate (units × price)
    products_df = products_df.copy()
    products_df['stock_value_egp'] = products_df['stock_quantity'] * products_df['price_egp']
    total_stock_value = round(products_df['stock_value_egp'].sum(), 2)

    # By category
    by_category = products_df.groupby('category').agg(
        total_units=('stock_quantity', 'sum'),
        products=('product_id', 'count'),
        avg_stock=('stock_quantity', 'mean')
    ).reset_index()
    by_category['avg_stock'] = by_category['avg_stock'].round(1)

    return {
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'healthy_stock': healthy_stock,
        'total_stock_units': total_stock_units,
        'avg_stock_per_product': avg_stock_per_product,
        'estimated_stock_value_egp': total_stock_value,
        'health_summary': {
            'out_of_stock_pct': round(out_of_stock / total_products * 100, 1) if total_products > 0 else 0,
            'low_stock_pct': round(low_stock / total_products * 100, 1) if total_products > 0 else 0,
            'healthy_pct': round(healthy_stock / total_products * 100, 1) if total_products > 0 else 0
        },
        'by_category': by_category.to_dict(orient='records')
    }


@router.get("/inventory/low-stock")
async def get_low_stock_products(
    threshold: int = Query(10, ge=1, le=100, description="Stock quantity threshold — products at or below this value are returned"),
    limit: int = Query(50, le=200)
):
    """
    Return products below the stock threshold. Admin should flag these for restocking.
    """
    products_df = data_service.get_products(status='approved')
    low = products_df[products_df['stock_quantity'] <= threshold].copy()
    low = low.sort_values('stock_quantity')  # Most critical (0 stock) first

    brands_df = data_service.get_brands()
    brand_names = brands_df.set_index('brand_id')['business_name'].to_dict()
    low['brand_name'] = low['brand_id'].map(brand_names)

    cols = ['product_id', 'brand_id', 'brand_name', 'name', 'category', 'price_egp', 'stock_quantity', 'sku']
    available_cols = [c for c in cols if c in low.columns]

    result = low[available_cols].head(limit).to_dict(orient='records')

    return {
        'threshold': threshold,
        'total_affected': len(low),
        'out_of_stock': int((low['stock_quantity'] == 0).sum()),
        'products': result
    }


@router.get("/inventory/analytics")
async def get_inventory_analytics():
    """
    Inventory analytics: stock value, restocking needs, category breakdown.
    """
    products_df = data_service.get_products()  # All statuses

    products_df = products_df.copy()
    products_df['stock_value_egp'] = products_df['stock_quantity'] * products_df['price_egp']

    # By status
    by_status = products_df.groupby('status').agg(
        count=('product_id', 'count'),
        total_stock=('stock_quantity', 'sum'),
        stock_value=('stock_value_egp', 'sum')
    ).reset_index()
    by_status['stock_value'] = by_status['stock_value'].round(2)

    # Top 10 most stocked products (by value)
    top_by_value = (
        products_df[products_df['status'] == 'approved']
        .nlargest(10, 'stock_value_egp')[['product_id', 'name', 'category', 'stock_quantity', 'price_egp', 'stock_value_egp']]
    )
    top_by_value['stock_value_egp'] = top_by_value['stock_value_egp'].round(2)

    # Restocking urgency score: sales_count / stock_quantity (higher = needs restock sooner)
    approved = products_df[products_df['status'] == 'approved'].copy()
    approved['restock_urgency'] = approved.apply(
        lambda r: round(r['sales_count'] / r['stock_quantity'], 2) if r['stock_quantity'] > 0 else 999,
        axis=1
    )
    urgent_restock = approved.nlargest(10, 'restock_urgency')[['product_id', 'name', 'category', 'stock_quantity', 'sales_count', 'restock_urgency']]

    return {
        'by_status': by_status.to_dict(orient='records'),
        'top_stocked_by_value': top_by_value.to_dict(orient='records'),
        'urgent_restock_needed': urgent_restock.to_dict(orient='records')
    }
