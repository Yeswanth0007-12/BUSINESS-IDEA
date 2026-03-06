from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.config import settings
from app.api import auth, products, boxes, optimization, analytics, history, subscriptions, admin, export, monitoring, orders, tasks, bulk_upload, warehouse
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="PackOptima AI API",
    description="""
## Enterprise-grade packaging optimization SaaS platform

PackOptima provides intelligent packaging optimization to reduce costs and improve efficiency.

### Key Features

* **Single Product Optimization**: Find the optimal box for individual products
* **Multi-Product Orders**: Pack multiple products using advanced bin packing algorithms
* **Shipping Cost Optimization**: Calculate volumetric weight and optimize total fulfillment costs
* **Bulk Upload Processing**: Process hundreds of orders via CSV upload
* **Warehouse Integration**: RESTful API with webhooks for seamless WMS integration
* **Advanced Analytics**: Track savings, space utilization, and shipping costs over time
* **Asynchronous Processing**: Queue system for handling large workloads

### Authentication

* **JWT Tokens**: For user authentication (most endpoints)
* **API Keys**: For warehouse integration endpoints

### Rate Limits

* Standard tier: 100 requests/minute
* Premium tier: 500 requests/minute
* Enterprise tier: 2000 requests/minute

### Support

For integration support, contact: support@packoptima.ai
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and JWT token management"
        },
        {
            "name": "Products",
            "description": "Manage product catalog with dimensions, weight, and handling characteristics"
        },
        {
            "name": "Boxes",
            "description": "Manage box inventory with dimensions, costs, and weight limits"
        },
        {
            "name": "Optimization",
            "description": "Run packaging optimization for single or multiple products"
        },
        {
            "name": "Orders",
            "description": "Create and optimize multi-product orders using bin packing"
        },
        {
            "name": "Bulk Upload",
            "description": "Upload and process multiple orders via CSV files"
        },
        {
            "name": "Tasks",
            "description": "Track status of asynchronous optimization tasks"
        },
        {
            "name": "Analytics",
            "description": "View savings, space utilization, and shipping cost analytics"
        },
        {
            "name": "warehouse",
            "description": "Warehouse integration API with API key authentication and webhooks"
        },
        {
            "name": "Subscriptions",
            "description": "Manage company subscriptions and billing"
        },
        {
            "name": "Admin",
            "description": "Administrative endpoints for user and company management"
        },
        {
            "name": "Export",
            "description": "Export optimization results and analytics data"
        },
        {
            "name": "Monitoring",
            "description": "System health and performance monitoring"
        }
    ]
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware (60 requests per minute)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(boxes.router)
app.include_router(optimization.router)
app.include_router(analytics.router)
app.include_router(history.router)
app.include_router(subscriptions.router)
app.include_router(admin.router)
app.include_router(export.router)
app.include_router(monitoring.router)
app.include_router(orders.router)
app.include_router(tasks.router)
app.include_router(bulk_upload.router)
app.include_router(warehouse.router)

@app.get("/")
async def root():
    return {"message": "PackOptima AI API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
