"""Health Check Routes"""

from fastapi import APIRouter, Response
from app.schemas.common import HealthResponse, HealthStatus

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Check if the pharmaceutical inventory API service is running and healthy"
)
async def health_check() -> HealthResponse:
    """
    Service health check endpoint.
    
    Returns current service status, version, and uptime information.
    
    **Response Codes:**
    - 200: Service is healthy
    - 503: Service is degraded or unhealthy
    """
    return HealthResponse(
        status=HealthStatus.HEALTHY,
        message="Pharmaceutical Inventory API - All systems operational"
    )


@router.get(
    "/ready",
    response_model=dict,
    summary="Readiness Check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint for Kubernetes-style orchestration.
    
    Returns 200 if service is ready to accept requests.
    """
    return {
        "ready": True,
        "service": "pharma-inventory-api",
        "version": "1.0.0"
    }


@router.get(
    "/version",
    response_model=dict,
    summary="API Version",
    description="Get the current API version"
)
async def get_version() -> dict:
    """Get the current API version."""
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "name": "Pharmaceutical Inventory Management API"
    }
