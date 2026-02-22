"""
Data access layer - loads and manages CSV data
"""
import pandas as pd
from typing import Optional
import os

class DataService:
    def __init__(self, data_path='mock_data'):
        self.data_path = data_path
        self._cache = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all CSV files into memory"""
        files = {
            'users': 'users.csv',
            'brands': 'brands.csv',
            'products': 'products.csv',
            'orders': 'orders.csv',
            'payments': 'payments.csv',
            'reviews': 'reviews.csv',
            'vendors': 'static_vendors.csv',
            'materials': 'raw_material_marketplace.csv',
            'material_requests': 'material_requests.csv',
            'support_tickets': 'support_tickets.csv',
            'admin_actions': 'admin_actions.csv',
            'analytics_snapshots': 'analytics_snapshots.csv'
        }
        
        for key, filename in files.items():
            filepath = os.path.join(self.data_path, filename)
            if os.path.exists(filepath):
                self._cache[key] = pd.read_csv(filepath, encoding='utf-8-sig')
                print(f"[OK] Loaded {filename}: {len(self._cache[key])} records")
            else:
                print(f"[WARNING] {filename} not found")
                self._cache[key] = pd.DataFrame()
    
    def get_users(self, user_type: Optional[str] = None) -> pd.DataFrame:
        """Get users, optionally filtered by type"""
        df = self._cache['users'].copy()
        if user_type:
            df = df[df['user_type'] == user_type]
        return df
    
    def get_brands(self, category: Optional[str] = None, verified: Optional[bool] = None) -> pd.DataFrame:
        """Get brands with optional filters"""
        df = self._cache['brands'].copy()
        if category:
            df = df[df['category'] == category]
        if verified is not None:
            df = df[df['verified'] == verified]
        return df
    
    def get_brand_by_id(self, brand_id: str) -> Optional[dict]:
        """Get single brand by ID"""
        df = self._cache['brands']
        result = df[df['brand_id'] == brand_id]
        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None
    
    def get_products(self, status: Optional[str] = None, category: Optional[str] = None) -> pd.DataFrame:
        """Get products with optional filters"""
        df = self._cache['products'].copy()
        if status:
            df = df[df['status'] == status]
        if category:
            df = df[df['category'] == category]
        return df
    
    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """Get single product by ID"""
        df = self._cache['products']
        result = df[df['product_id'] == product_id]
        if len(result) > 0:
            return result.iloc[0].to_dict()
        return None
    
    def get_orders(self, status: Optional[str] = None) -> pd.DataFrame:
        """Get orders with optional status filter"""
        df = self._cache['orders'].copy()
        if status:
            df = df[df['status'] == status]
        return df
    
    def get_reviews(self) -> pd.DataFrame:
        """Get all reviews"""
        return self._cache['reviews'].copy()
    
    def get_vendors(self) -> pd.DataFrame:
        """Get all vendors"""
        return self._cache['vendors'].copy()
    
    def get_materials(self) -> pd.DataFrame:
        """Get all raw materials"""
        return self._cache['materials'].copy()
    
    def get_material_requests(self) -> pd.DataFrame:
        """Get all material requests"""
        return self._cache['material_requests'].copy()
    
    def get_support_tickets(self) -> pd.DataFrame:
        """Get all support tickets"""
        return self._cache['support_tickets'].copy()
    
    def get_analytics_snapshots(self) -> pd.DataFrame:
        """Get analytics snapshots"""
        return self._cache['analytics_snapshots'].copy()

    def get_payments(self) -> pd.DataFrame:
        """Get all payments"""
        return self._cache['payments'].copy()

    def get_admin_actions(self) -> pd.DataFrame:
        """Get all admin actions log"""
        return self._cache['admin_actions'].copy()

# Global instance
data_service = DataService()
