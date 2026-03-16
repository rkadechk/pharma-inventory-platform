"""Supply Chain Optimization Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SupplierInfo(BaseModel):
    """Supplier information"""
    supplier_id: str = Field(description="Supplier identifier")
    name: str = Field(description="Supplier name")
    lead_time_days: int = Field(ge=1, description="Lead time in days")
    min_order_units: int = Field(ge=1, description="Minimum order quantity")
    unit_cost: float = Field(ge=0, description="Unit cost ($)")
    on_time_delivery_rate: float = Field(ge=0.0, le=1.0, description="On-time delivery rate [0-1]")
    reliability_score: Optional[float] = Field(None, description="Supplier reliability [0-1]")


class SupplyChainOptimizationRequest(BaseModel):
    """Supply chain optimization API request"""
    facility_id: str = Field(description="Facility to optimize for")
    inventory_at_risk: List[Dict[str, Any]] = Field(
        description="At-risk medications requiring supply decisions"
    )
    demand_forecasts: List[Dict[str, Any]] = Field(
        description="Demand forecasts for next 30 days"
    )
    available_suppliers: List[SupplierInfo] = Field(
        description="Available suppliers with pricing and lead times"
    )
    transfer_costs: Optional[Dict[str, float]] = Field(
        default=None,
        description="Transfer costs between facilities"
    )
    budget_constraint: Optional[float] = Field(
        None,
        description="Maximum budget for supply decisions ($)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": "FAC001",
                "inventory_at_risk": [],
                "demand_forecasts": [],
                "available_suppliers": [
                    {
                        "supplier_id": "SUP001",
                        "name": "Global Pharma",
                        "lead_time_days": 3,
                        "min_order_units": 50,
                        "unit_cost": 8.50,
                        "on_time_delivery_rate": 0.98,
                        "reliability_score": 0.95
                    }
                ],
                "transfer_costs": None,
                "budget_constraint": None
            }
        }


class SupplyDecision(BaseModel):
    """Single supply chain decision"""
    order_id: str = Field(description="Unique order identifier")
    medication_id: int = Field(description="Medication to supply")
    decision_type: str = Field(description="Decision: REORDER or TRANSFER")
    quantity: int = Field(ge=1, description="Quantity to order/transfer")
    supplier_id: Optional[str] = Field(None, description="Supplier ID if reorder")
    source_facility_id: Optional[str] = Field(None, description="Source facility if transfer")
    estimated_cost: float = Field(description="Estimated cost ($)")
    expected_delivery_date: Optional[str] = Field(None, description="Expected delivery date")
    rationale: str = Field(description="Reason for this decision")
    cost_benefit_score: float = Field(ge=0.0, le=1.0, description="Cost-benefit score [0-1]")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD001",
                "medication_id": 1,
                "decision_type": "REORDER",
                "quantity": 500,
                "supplier_id": "SUP001",
                "source_facility_id": None,
                "estimated_cost": 4250.00,
                "expected_delivery_date": "2026-02-22",
                "rationale": "Demand forecast indicates need, cost-effective supplier",
                "cost_benefit_score": 0.88
            }
        }


class SupplyChainOptimizationResponse(BaseModel):
    """Supply chain optimization API response"""
    facility_id: str = Field(description="Facility optimized for")
    optimization_date: datetime = Field(description="When optimization was performed")
    decisions: List[SupplyDecision] = Field(description="Supply chain decisions")
    total_estimated_cost: float = Field(description="Total cost of all decisions ($)")
    total_estimated_savings: float = Field(description="Total savings from optimization ($)")
    expected_improvement: float = Field(ge=0.0, le=100.0, description="Expected improvement (%)")
    risk_mitigation: str = Field(description="Risk mitigation summary")
    implementation_priority: List[str] = Field(description="Priority order for implementation")

    class Config:
        json_schema_extra = {
            "example": {
                "facility_id": "FAC001",
                "optimization_date": "2026-02-19T21:35:00",
                "decisions": [],
                "total_estimated_cost": 4250.00,
                "total_estimated_savings": 2000.00,
                "expected_improvement": 15.5,
                "risk_mitigation": "Reduced stockout risk by 45%, optimized expiration losses",
                "implementation_priority": ["ORD001", "ORD002"]
            }
        }
