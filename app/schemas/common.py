"""Common API Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """API health check response"""
    status: HealthStatus = Field(description="Current service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(default="1.0.0", description="API version")
    message: str = Field(default="Service operational", description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-02-19T21:35:00",
                "version": "1.0.0",
                "message": "Service operational"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str = Field(description="Error code identifier")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_INPUT",
                "message": "Invalid medication_id provided",
                "details": {"field": "medication_id", "value": -1},
                "timestamp": "2026-02-19T21:35:00"
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items to return")


class StatusResponse(BaseModel):
    """Generic status response"""
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"items_processed": 42},
                "timestamp": "2026-02-19T21:35:00"
            }
        }


class ConsumptionDataPoint(BaseModel):
    """Single consumption data point"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    facility_id: str = Field(description="Facility identifier")
    medication_id: int = Field(gt=0, description="Medication ID")
    units_consumed: int = Field(ge=0, description="Units consumed")


class MetricsData(BaseModel):
    """System metrics data"""
    total_medications: int = Field(description="Total medications in system")
    total_facilities: int = Field(description="Total facilities")
    total_inventory_value: float = Field(description="Total inventory value ($)")
    average_expiry_days: float = Field(description="Average days to expiry")
    medications_at_risk: int = Field(description="Medications with expiration risk")
    forecast_accuracy_mape: float = Field(description="Model accuracy (MAPE %)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_medications": 205,
                "total_facilities": 8,
                "total_inventory_value": 2500000.50,
                "average_expiry_days": 127,
                "medications_at_risk": 12,
                "forecast_accuracy_mape": 0.145
            }
        }
