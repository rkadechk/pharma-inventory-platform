"""Demand Forecasting Schemas"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class DemandForecastRequest(BaseModel):
    """Demand forecasting API request"""
    medication_id: int = Field(gt=0, description="Medication ID to forecast")
    consumption_data: List[Dict[str, Any]] = Field(
        description="Historical consumption data points with date, facility_id, units_consumed"
    )
    external_signals: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional external signals (weather, disease outbreaks, seasonal trends)"
    )
    forecast_days: int = Field(default=30, ge=7, le=365, description="Number of days to forecast")
    model_type: Optional[str] = Field(
        default="auto",
        description="Model type: 'prophet', 'arima', or 'auto' for automatic selection"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "medication_id": 1,
                "consumption_data": [
                    {"date": "2026-02-19", "facility_id": "FAC001", "units_consumed": 45},
                    {"date": "2026-02-18", "facility_id": "FAC001", "units_consumed": 48},
                ],
                "external_signals": [
                    {"signal_type": "disease_outbreak", "intensity": "high", "impact": 1.3}
                ],
                "forecast_days": 30,
                "model_type": "auto"
            }
        }


class ForecastPoint(BaseModel):
    """Single forecast point"""
    day: int = Field(description="Day number in forecast period")
    predicted_demand: int = Field(ge=0, description="Predicted demand units")
    confidence_lower: Optional[int] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[int] = Field(None, description="Upper confidence bound")


class AnomalyDetected(BaseModel):
    """Detected anomaly in consumption"""
    index: int = Field(description="Index in dataset")
    date: str = Field(description="Date of anomaly")
    type: str = Field(description="Anomaly type: SPIKE or DIP")
    magnitude: float = Field(description="Magnitude of anomaly (percentage change)")


class DemandForecastResponse(BaseModel):
    """Demand forecasting API response"""
    medication_id: int = Field(description="Medication ID")
    medication_name: str = Field(description="Medication name")
    forecast_date: datetime = Field(description="When forecast was generated")
    forecast_days: int = Field(description="Forecast horizon")
    predicted_demand_units: int = Field(ge=0, description="Total predicted 30-day demand")
    confidence_level: float = Field(ge=0.0, le=1.0, description="Forecast confidence [0-1]")
    model_type: str = Field(description="Model used: PROPHET, ARIMA, or BASELINE")
    model_accuracy_mape: float = Field(description="Model accuracy (Mean Absolute Percentage Error)")
    forecast_points: List[ForecastPoint] = Field(description="Daily forecast points")
    anomalies_detected: List[AnomalyDetected] = Field(description="Detected anomalies in data")
    external_signals_used: List[str] = Field(default_factory=list, description="External signals applied")
    recommendation: Optional[str] = Field(
        None,
        description="Recommendation based on forecast (e.g., 'Monitor for demand spike')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "medication_id": 1,
                "medication_name": "Med_1",
                "forecast_date": "2026-02-19T21:35:00",
                "forecast_days": 30,
                "predicted_demand_units": 1500,
                "confidence_level": 0.85,
                "model_type": "PROPHET",
                "model_accuracy_mape": 0.145,
                "forecast_points": [
                    {"day": 1, "predicted_demand": 50, "confidence_lower": 45, "confidence_upper": 55}
                ],
                "anomalies_detected": [],
                "external_signals_used": [],
                "recommendation": "Demand stable, monitor for seasonal changes"
            }
        }
