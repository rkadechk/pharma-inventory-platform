"""
Data Models for Agent Processing
Pydantic schemas for validation and type-safety
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationAction(str, Enum):
    """Possible agent actions"""
    TRANSFER = "TRANSFER"
    DISPOSE = "DISPOSE"
    REORDER = "REORDER"
    HOLD = "HOLD"


class ConfidenceLevel(str, Enum):
    """Confidence levels for recommendations"""
    HIGH = "HIGH"      # 90%+
    MEDIUM = "MEDIUM"  # 70-89%
    LOW = "LOW"        # <70%


# =========================================================================
# INVENTORY OPTIMIZATION AGENT MODELS
# =========================================================================

class InventoryBatch(BaseModel):
    """Represents a medication batch in inventory"""
    batch_id: str
    medication_id: str
    medication_name: str
    facility_id: str
    facility_name: str
    quantity: int
    unit_of_measure: str
    expiry_date: datetime
    storage_location: str
    storage_temperature: float
    last_updated: datetime
    supplier_batch_code: str
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiration"""
        return (self.expiry_date - datetime.now()).days
    
    @property
    def is_at_risk(self, risk_window_days: int = 14) -> bool:
        """Check if batch is at expiration risk"""
        return self.days_until_expiry <= risk_window_days
    
    @property
    def disposal_cost_estimate(self) -> float:
        """Estimate disposal cost (default $18K per batch)"""
        return 18000.0


class TransferRecommendation(BaseModel):
    """Agent recommendation to transfer a batch"""
    batch_id: str
    medication_id: str
    action: RecommendationAction
    reason: str
    
    # Transfer details
    target_facility_id: Optional[str] = None
    target_facility_name: Optional[str] = None
    transfer_cost: Optional[float] = None
    transfer_lead_time_hours: Optional[int] = None
    
    # Disposal details
    disposal_cost: Optional[float] = None
    disposal_method: Optional[str] = None
    
    # Metrics
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.85)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    cost_benefit_analysis: Optional[Dict[str, Any]] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class FacilityInfo(BaseModel):
    """Information about a facility"""
    facility_id: str
    facility_name: str
    facility_type: str  # Hospital, Clinic, Pharmacy
    storage_capacity: int
    current_utilization: int
    utilization_percentage: float
    has_refrigeration: bool
    refrigeration_capacity: int
    can_receive_transfers: bool
    can_send_transfers: bool
    transfer_lead_time_hours: int
    regulatory_certifications: List[str]
    
    @property
    def available_capacity(self) -> int:
        """Calculate available storage capacity"""
        return self.storage_capacity - self.current_utilization


# =========================================================================
# DEMAND FORECASTING AGENT MODELS
# =========================================================================

class ConsumptionData(BaseModel):
    """Historical consumption data for a medication"""
    medication_id: str
    medication_name: str
    facility_id: str
    date: datetime
    quantity_dispensed: int
    patient_count: int
    prescriber_count: int
    indication: Optional[str] = None


class DemandForecast(BaseModel):
    """ML-generated demand forecast"""
    medication_id: int
    medication_name: str
    facility_id: Optional[str] = None
    forecast_date: datetime
    forecast_days: int = 30
    
    # Forecast values
    forecast_points: List[Dict[str, Any]] = Field(default_factory=list)  # List of {date, predicted_demand, confidence_lower, confidence_upper}
    
    # Model performance
    model_type: str = "Prophet"  # or ARIMA, LSTM, etc
    model_accuracy_mape: float = Field(default=0.15, ge=0.0, le=1.0)  # Mean Absolute Percentage Error
    training_window_days: int = 90
    
    # Anomalies detected
    anomalies_detected: List[Dict[str, Any]] = Field(default_factory=list)
    
    # External signals used
    external_signals_used: List[str] = Field(default_factory=list)
    
    # Predictions
    total_predicted_demand_30d: int = 0
    min_predicted_demand: int = 0
    max_predicted_demand: int = 0
    average_daily_demand: float = 0.0
    
    # Test-expected fields
    predicted_demand_units: Optional[int] = None
    confidence_level: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def is_accurate(self, threshold: float = 0.15) -> bool:
        """Check if forecast accuracy meets threshold"""
        return self.model_accuracy_mape <= threshold


class ExternalSignal(BaseModel):
    """External signal affecting demand (weather, disease, seasonal)"""
    signal_type: str  # weather, disease_outbreak, seasonal, event
    signal_name: str
    signal_value: float
    intensity: str  # low, medium, high
    affected_medications: List[str]
    expected_demand_impact: float  # e.g., 1.4 = 40% increase
    date_detected: datetime
    duration_days: int


# =========================================================================
# SUPPLY CHAIN COORDINATION AGENT MODELS
# =========================================================================

class Supplier(BaseModel):
    """Supplier information"""
    supplier_id: str
    supplier_name: str
    medications_supplied: List[str]
    unit_price: float
    minimum_order_quantity: int
    lead_time_days: int
    on_time_delivery_rate: float  # 0.0 to 1.0
    reliability_score: float  # 0.0 to 1.0
    last_delivery_date: Optional[datetime] = None


class SupplyOption(BaseModel):
    """Option for fulfilling supply need"""
    option_type: str  # REORDER, TRANSFER
    
    # For REORDER
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    unit_price: Optional[float] = None
    quantity_needed: Optional[int] = None
    total_cost: Optional[float] = None
    lead_time_days: Optional[int] = None
    
    # For TRANSFER
    from_facility_id: Optional[str] = None
    from_facility_name: Optional[str] = None
    transfer_cost: Optional[float] = None
    transfer_lead_time_hours: Optional[int] = None
    
    # Ranking
    confidence_score: float
    reliability_score: float
    overall_score: float  # Used for ranking


class SupplyChainDecision(BaseModel):
    """Agent decision on supply chain action"""
    medication_id: str
    facility_id: str
    decision_type: RecommendationAction  # REORDER or TRANSFER
    
    current_stock: int
    forecasted_demand_30d: int
    deficit: int
    
    recommended_action: Dict[str, Any]
    alternative_options: List[SupplyOption]
    
    reason: str
    confidence_score: float
    cost_estimate: float
    lead_time_estimate: float  # in hours or days
    risk_assessment: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)


# =========================================================================
# AGENT COMMUNICATION MODELS
# =========================================================================

class AgentMessage(BaseModel):
    """Message published by agents to Kafka topics"""
    source_agent: str
    target_agents: List[str]
    message_type: str  # recommendation, alert, signal, decision
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: str = "normal"  # low, normal, high, critical


class AgentMetrics(BaseModel):
    """Metrics about agent performance"""
    agent_name: str
    decisions_made: int = 0
    average_confidence: float = 0.0
    accuracy_score: float = 0.0  # How many recommendations were acted upon
    last_decision_timestamp: Optional[datetime] = None
    error_count: int = 0
    processing_time_ms: float = 0.0
    
    class Config:
        use_enum_values = True


# =========================================================================
# AGGREGATED METRICS
# =========================================================================

class SystemMetrics(BaseModel):
    """Overall system performance metrics"""
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Inventory metrics
    total_batches_monitored: int
    at_risk_batches: int
    waste_prevented_value: float
    total_disposal_cost_avoided: float
    
    # Demand metrics
    forecast_accuracy_mape: float
    stockout_incidents: int
    prevent_rate: float
    
    # Supply chain metrics
    average_transfer_cost: float
    average_reorder_cost: float
    cost_optimization_percentage: float
    
    # Agent health
    inventory_agent_status: str  # active, error, offline
    demand_agent_status: str
    supply_chain_agent_status: str
    
    recent_decisions: List[Dict[str, Any]]
