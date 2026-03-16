"""API Schemas - Request and Response Models"""

from .common import (
    HealthResponse,
    ErrorResponse,
    PaginationParams,
    StatusResponse,
)
from .demand import DemandForecastRequest, DemandForecastResponse
from .inventory import InventoryAnalysisRequest, InventoryAnalysisResponse
from .supply_chain import SupplyChainOptimizationRequest, SupplyChainOptimizationResponse
from .optimization import FullOptimizationRequest, FullOptimizationResponse

__all__ = [
    "HealthResponse",
    "ErrorResponse",
    "PaginationParams",
    "StatusResponse",
    "DemandForecastRequest",
    "DemandForecastResponse",
    "InventoryAnalysisRequest",
    "InventoryAnalysisResponse",
    "SupplyChainOptimizationRequest",
    "SupplyChainOptimizationResponse",
    "FullOptimizationRequest",
    "FullOptimizationResponse",
]
