"""
TalentTree Admin Dashboard API
Main application file
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers
from api.endpoints import dashboard, brands, products, orders, analytics, customers, vendors, support

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*60)
    print("[STARTUP] TALENTREE ADMIN API STARTING")
    print("="*60)
    print("[INFO] Loading data...")
    
    from api.services.data_service import data_service
    print("[OK] Data loaded successfully")
    
    print("\n[INFO] API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n[SHUTDOWN] Shutting down TalentTree API")

# Create FastAPI app
app = FastAPI(
    title="TalentTree Admin Dashboard API",
    description="AI-powered admin dashboard for TalentTree Egyptian e-commerce platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow Angular frontend and any localhost origin
# Note: allow_credentials=True requires explicit origins (not "*")
ALLOWED_ORIGINS = [
    # Angular default dev server
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    # Common alternative ports
    "http://localhost:3000",
    "http://localhost:4000",
    "http://localhost:8080",
    "http://localhost:8100",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:4000",
    "http://127.0.0.1:8080",
    # Same origin (direct browser access)
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1",
    # ngrok or any other tunnel (for team sharing)
    "https://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",  # Any localhost port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/admin", tags=["Dashboard"])
app.include_router(brands.router, prefix="/api/admin", tags=["Brands"])
app.include_router(products.router, prefix="/api/admin", tags=["Products"])
app.include_router(orders.router, prefix="/api/admin", tags=["Orders"])
app.include_router(analytics.router, prefix="/api/admin", tags=["Analytics"])
app.include_router(customers.router, prefix="/api/admin", tags=["Customers"])
app.include_router(vendors.router, prefix="/api/admin", tags=["Vendors & Materials"])
app.include_router(support.router, prefix="/api/admin", tags=["Support"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TalentTree Admin Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "dashboard": "/api/admin/dashboard/overview",
            "brands": "/api/admin/brands",
            "products": "/api/admin/products",
            "orders": "/api/admin/orders",
            "analytics": "/api/admin/analytics/sales-trends",
            "customers": "/api/admin/customers"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "talentree-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
