"""
Pharmaceutical Inventory Management API

A production-ready FastAPI application for optimizing pharmaceutical inventory
across multi-facility networks using AI agents and advanced analytics.

Features:
- Demand forecasting (Prophet/ARIMA/Baseline models)
- Inventory optimization (Expiration risk analysis)
- Supply chain coordination (Reorder vs transfer decisions)
- Full validation pipeline with quality metrics
- Interactive Swagger/OpenAPI documentation
- Health checks and system metrics

API Version: 1.0.0
Python Version: 3.8+
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from app.routes import api_router
from app.schemas.common import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Pharmaceutical Inventory Management API",
    description="""
    Production-ready API for pharmaceutical inventory optimization using AI agents.
    
    ## Overview
    This API provides comprehensive pharmaceutical inventory management through:
    - **Demand Forecasting**: ML-powered demand prediction (Prophet/ARIMA models)
    - **Inventory Analysis**: Risk detection for expiration and stockouts
    - **Supply Optimization**: Intelligent reorder vs transfer decisions
    - **System Integration**: 7-stage validation pipeline with quality metrics
    
    ## Key Features
    - Multi-facility network support
    - Real-time demand forecasting
    - Expiration risk management
    - Cost-benefit optimization
    - Comprehensive data validation
    - Interactive API documentation
    
    ## Getting Started
    1. Check health: `GET /api/v1/health`
    2. Run optimization: `POST /api/v1/optimization/run` with your data
    3. View results: Response includes all recommendations and metrics
    
    ## Authentication
    (Note: Would add API key authentication in production)
    
    ## Rate Limiting
    (Note: Would add rate limiting in production)
    
    ## Contact
    For questions or issues, contact: support@pharma-inventory.local
    """,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI spec
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={"path": str(request.url), "method": request.method}
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Welcome to the Pharmaceutical Inventory Management API"
)
async def root():
    """
    Root endpoint providing API information.
    
    Use `/docs` for interactive Swagger documentation.
    Use `/redoc` for ReDoc documentation.
    """
    return {
        "name": "Pharmaceutical Inventory Management API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/v1/health",
            "optimization": "/api/v1/optimization/run",
            "demand": "/api/v1/demand/forecast",
            "inventory": "/api/v1/inventory/analyze",
            "supply": "/api/v1/supply/optimize"
        }
    }


# Include all API routes
app.include_router(api_router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("=" * 80)
    logger.info("Pharmaceutical Inventory Management API Starting")
    logger.info("=" * 80)
    logger.info("Version: 1.0.0")
    logger.info("Environment: Production-Ready")
    logger.info(f"Startup Time: {datetime.now().isoformat()}")
    logger.info("Documentation: http://localhost:8000/docs")
    logger.info("=" * 80)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("=" * 80)
    logger.info("Pharmaceutical Inventory Management API Shutting Down")
    logger.info("=" * 80)


# Metadata for OpenAPI spec
tags_metadata = [
    {
        "name": "Root",
        "description": "Root endpoints for API information and documentation"
    },
    {
        "name": "Health",
        "description": "Service health and readiness checks"
    },
    {
        "name": "Optimization",
        "description": "Full pharmaceutical inventory optimization pipeline"
    },
    {
        "name": "Demand Forecasting",
        "description": "Demand prediction using ML models (Prophet, ARIMA)"
    },
    {
        "name": "Inventory",
        "description": "Inventory analysis and risk detection"
    },
    {
        "name": "Supply Chain",
        "description": "Supply chain optimization and ordering decisions"
    }
]

app.openapi_tags = tags_metadata


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
