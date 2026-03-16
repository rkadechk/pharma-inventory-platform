"""Inventory Analysis Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class InventoryBatchInfo(BaseModel):
    """Information about a medication batch"""
    batch_id: str = Field(description="Batch identifier")
    medication_id: int = Field(gt=0, description="Medication ID")
    facility_id: str = Field(description="Facility ID")
    quantity_on_hand: int = Field(ge=0, description="Current quantity")
    expiry_date: str = Field(description="Expiry date (YYYY-MM-DD)")
    unit_cost: float = Field(ge=0, description="Cost per unit ($)")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiration")
    is_at_risk: Optional[bool] = Field(None, description="Whether batch is at expiration risk")


class InventoryAnalysisRequest(BaseModel):
    """Inventory analysis API request"""
    facility_batches: List[InventoryBatchInfo] = Field(
        description="List of current medication batches at facility"
    )
    demand_forecasts: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional demand forecasts to cross-reference"
    )
    risk_window_days: int = Field(
        default=14,
        ge=1,
        le=90,
        description="Days until expiry considered at-risk"
    )
    analyze_stockout_risk: bool = Field(
        default=True,
        description="Whether to analyze stockout risk based on demand"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "facility_batches": [
                    {
                        "batch_id": "B001",
                        "medication_id": 1,
                        "facility_id": "FAC001",
                        "quantity_on_hand": 100,
                        "expiry_date": "2026-03-15",
                        "unit_cost": 10.50
                    }
                ],
                "demand_forecasts": None,
                "risk_window_days": 14,
                "analyze_stockout_risk": True
            }
        }


class InventoryRecommendation(BaseModel):
    """Inventory recommendation"""
    batch_id: str = Field(description="Batch to act on")
    medication_id: int = Field(description="Medication ID")
    action: str = Field(description="Recommended action: TRANSFER, DISPOSE, REORDER, or HOLD")
    reason: str = Field(description="Reason for recommendation")
    urgency: str = Field(description="Urgency level: LOW, MEDIUM, or HIGH")
    estimated_cost_impact: float = Field(description="Financial impact ($)")
    target_facility_id: Optional[str] = Field(None, description="Target facility if transfer")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "B001",
                "medication_id": 1,
                "action": "TRANSFER",
                "reason": "Expiring in 8 days, high stock at FAC001",
                "urgency": "HIGH",
                "estimated_cost_impact": -500.00,
                "target_facility_id": "FAC002",
                "confidence_score": 0.92
            }
        }


class InventoryAnalysisResponse(BaseModel):
    """Inventory analysis API response"""
    facility_id: str = Field(description="Facility analyzed")
    analysis_date: datetime = Field(description="When analysis was performed")
    total_batches_analyzed: int = Field(description="Number of batches reviewed")
    batches_at_risk: int = Field(description="Batches at expiration risk")
    stockout_risk_medications: int = Field(description="Medications with stockout risk")
    estimated_disposal_cost: float = Field(description="Estimated disposal cost ($)")
    estimated_transfer_cost: float = Field(description="Estimated transfer cost ($)")
    estimated_potential_savings: float = Field(description="Potential savings from actions ($)")
    recommendations: List[InventoryRecommendation] = Field(description="Recommended actions")
    summary: str = Field(description="Executive summary of analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": "FAC001",
                "analysis_date": "2026-02-19T21:35:00",
                "total_batches_analyzed": 45,
                "batches_at_risk": 3,
                "stockout_risk_medications": 2,
                "estimated_disposal_cost": 54000.00,
                "estimated_transfer_cost": 500.00,
                "estimated_potential_savings": 53500.00,
                "recommendations": [],
                "summary": "3 batches at expiration risk, recommend immediate action"
            }
        }
