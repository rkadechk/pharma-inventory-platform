"""Full Optimization Pipeline Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .demand import DemandForecastResponse
from .inventory import InventoryRecommendation
from .supply_chain import SupplyDecision


class FacilityBatchData(BaseModel):
    """Facility batch data for optimization"""
    facility_id: str = Field(description="Facility identifier")
    batch_id: str = Field(description="Batch identifier")
    medication_id: int = Field(gt=0, description="Medication ID")
    quantity_on_hand: int = Field(ge=0, description="Current quantity")
    expiry_date: str = Field(description="Expiry date (YYYY-MM-DD)")
    unit_cost: float = Field(ge=0, description="Cost per unit ($)")


class ConsumptionHistoryData(BaseModel):
    """Consumption history data point"""
    date: str = Field(description="Date (YYYY-MM-DD)")
    facility_id: str = Field(description="Facility identifier")
    medication_id: int = Field(gt=0, description="Medication ID")
    units_consumed: int = Field(ge=0, description="Units consumed")


class SupplierData(BaseModel):
    """Supplier data for optimization"""
    supplier_id: str = Field(description="Supplier identifier")
    name: str = Field(description="Supplier name")
    lead_time_days: int = Field(ge=1, description="Lead time in days")
    min_order_units: int = Field(ge=1, description="Minimum order quantity")
    unit_cost: float = Field(ge=0, description="Unit cost ($)")


class FullOptimizationRequest(BaseModel):
    """Full pharmaceutical inventory optimization request"""
    facility_inventory: List[FacilityBatchData] = Field(
        description="Current inventory data across all facilities"
    )
    consumption_history: List[ConsumptionHistoryData] = Field(
        description="Historical consumption data (typically 90 days)"
    )
    suppliers: List[SupplierData] = Field(
        description="Available suppliers"
    )
    external_signals: Optional[Dict[str, Any]] = Field(
        default=None,
        description="External signals (weather, disease outbreaks, seasonal data)"
    )
    transfer_cost_matrix: Optional[Dict[str, float]] = Field(
        default=None,
        description="Transfer costs between facility pairs"
    )
    forecast_days: int = Field(
        default=30,
        ge=7,
        le=365,
        description="Number of days to forecast"
    )
    budget_constraint: Optional[float] = Field(
        None,
        description="Maximum budget for supply optimization ($)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "facility_inventory": [
                    {
                        "facility_id": "FAC001",
                        "batch_id": "B001",
                        "medication_id": 1,
                        "quantity_on_hand": 100,
                        "expiry_date": "2026-03-15",
                        "unit_cost": 10.50
                    }
                ],
                "consumption_history": [
                    {
                        "date": "2026-02-19",
                        "facility_id": "FAC001",
                        "medication_id": 1,
                        "units_consumed": 45
                    }
                ],
                "suppliers": [
                    {
                        "supplier_id": "SUP001",
                        "name": "Global Pharma",
                        "lead_time_days": 3,
                        "min_order_units": 50,
                        "unit_cost": 8.50
                    }
                ],
                "external_signals": None,
                "transfer_cost_matrix": None,
                "forecast_days": 30,
                "budget_constraint": None
            }
        }


class QualityReport(BaseModel):
    """Quality report from optimization pipeline"""
    timestamp: datetime = Field(description="Report generation time")
    overall_quality_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall data quality score [0-1]"
    )
    data_completeness: Dict[str, float] = Field(
        description="Completeness of each data category"
    )
    validation_summary: Dict[str, str] = Field(
        description="Summary of validation checks"
    )
    system_health: Dict[str, Any] = Field(
        description="System health metrics"
    )
    recommendations: List[str] = Field(
        description="Recommendations for data quality improvement"
    )


class OptimizationMetrics(BaseModel):
    """Metrics from optimization execution"""
    total_medications: int = Field(description="Total medications analyzed")
    total_facilities: int = Field(description="Total facilities")
    total_inventory_value: float = Field(description="Total inventory value ($)")
    medications_at_risk: int = Field(description="Medications at expiration risk")
    potential_waste_value: float = Field(description="Potential waste value ($)")
    estimated_savings: float = Field(description="Estimated savings from recommendations ($)")
    forecast_accuracy_mape: float = Field(description="Forecast accuracy (MAPE)")


class FullOptimizationResponse(BaseModel):
    """Full optimization pipeline response"""
    status: str = Field(description="Execution status: 'completed' or 'failed'")
    execution_time_seconds: float = Field(description="Total execution time")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    # Stage outputs
    demand_forecasts: List[DemandForecastResponse] = Field(
        description="Demand forecasts for all medications"
    )
    inventory_recommendations: List[InventoryRecommendation] = Field(
        description="Inventory optimization recommendations"
    )
    supply_decisions: List[SupplyDecision] = Field(
        description="Supply chain optimization decisions"
    )
    
    # Integrated outputs
    action_plan: Dict[str, Any] = Field(
        description="Consolidated action plan with priorities"
    )
    system_metrics: OptimizationMetrics = Field(
        description="System metrics and KPIs"
    )
    
    # Validation outputs
    quality_report: QualityReport = Field(
        description="Data quality and validation report"
    )
    validation_results: Dict[str, Any] = Field(
        description="Detailed validation results from each stage"
    )
    
    # Metadata
    agent_metrics: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Performance metrics for each agent"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical warnings from execution"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Errors encountered during execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "execution_time_seconds": 2.45,
                "timestamp": "2026-02-19T21:35:00",
                "demand_forecasts": [],
                "inventory_recommendations": [],
                "supply_decisions": [],
                "action_plan": {},
                "system_metrics": {
                    "total_medications": 205,
                    "total_facilities": 8,
                    "total_inventory_value": 2500000.50,
                    "medications_at_risk": 12,
                    "potential_waste_value": 200000.00,
                    "estimated_savings": 180000.00,
                    "forecast_accuracy_mape": 0.145
                },
                "quality_report": {
                    "timestamp": "2026-02-19T21:35:00",
                    "overall_quality_score": 0.87,
                    "data_completeness": {},
                    "validation_summary": {},
                    "system_health": {},
                    "recommendations": []
                },
                "validation_results": {},
                "agent_metrics": None,
                "warnings": [],
                "errors": []
            }
        }
