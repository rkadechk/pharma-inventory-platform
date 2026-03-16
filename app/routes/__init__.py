"""API Routes"""

from fastapi import APIRouter

# Import routers
from .health import router as health_router
from .optimization import router as optimization_router
from .demand import router as demand_router
from .inventory import router as inventory_router
from .supply_chain import router as supply_chain_router
from .powerbi import router as powerbi_router

# Create main API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(optimization_router, prefix="/optimization", tags=["Optimization"])
api_router.include_router(demand_router, prefix="/demand", tags=["Demand"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(supply_chain_router, prefix="/supply-chain", tags=["Supply Chain"])
api_router.include_router(powerbi_router, prefix="/powerbi", tags=["PowerBI Exports"])
