"""Demand Forecasting Route"""

from fastapi import APIRouter, HTTPException
import logging

from agents.demand_agent import DemandForecastingAgent
from app.schemas.demand import DemandForecastRequest, DemandForecastResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/forecast",
    response_model=DemandForecastResponse,
    summary="Demand Forecasting",
    description="Generate demand forecast for a specific medication"
)
async def forecast_demand(request: DemandForecastRequest) -> DemandForecastResponse:
    """
    Generate a demand forecast for a specific medication.
    
    **Forecasting Models:**
    - **Prophet:** Facebook's time-series forecasting with seasonality (default)
    - **ARIMA:** Autoregressive Integrated Moving Average for stationary series
    - **Baseline:** Simple historical average (fallback)
    
    **Key Features:**
    - Multiple model fallback (Prophet → ARIMA → Baseline)
    - Confidence interval estimation
    - Anomaly detection (spikes and dips)
    - External signal integration (weather, disease, seasonal)
    - Model accuracy metrics (MAPE - Mean Absolute Percentage Error)
    
    **Input Data Requirements:**
    - medication_id: Positive integer identifier
    - consumption_data: Historical consumption with date, facility_id, units_consumed
    - Recommendation: minimum 30 days of historical data
    
    **Response Includes:**
    - Predicted demand for forecast period
    - Confidence levels and intervals
    - Model type used and accuracy
    - Detected anomalies in consumption
    - Actionable recommendations
    
    **Model Selection Logic:**
    1. Try Prophet (most accurate with seasonality)
    2. If Prophet fails, use ARIMA (better for stationary data)
    3. If both fail, use historical mean (always works)
    
    **Typical Response Time:** 1-3 seconds
    
    **Error Handling:**
    - 400: Invalid medication_id or insufficient data
    - 422: Validation error in request schema
    - 500: Forecasting model failed
    """
    try:
        # Validate input
        if not isinstance(request.medication_id, int) or request.medication_id <= 0:
            raise ValueError(f"Invalid medication_id: {request.medication_id}")
        
        if not request.consumption_data:
            raise ValueError("No consumption data provided")
        
        logger.info(f"Starting demand forecast for medication {request.medication_id}")
        
        # Create agent
        agent = DemandForecastingAgent()
        
        # Generate forecast
        forecast = agent.generate_forecasts(
            medication_id=request.medication_id,
            consumption_data=request.consumption_data,
            external_signals=request.external_signals or []
        )
        
        if not forecast:
            raise ValueError("Failed to generate forecast")
        
        logger.info(f"Forecast generated: {forecast.predicted_demand_units} units, confidence: {forecast.confidence_level:.1%}")
        
        return forecast
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Forecasting failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Demand forecasting failed: {str(e)}"
        )


@router.post(
    "/forecast-batch",
    response_model=dict,
    summary="Batch Demand Forecasting",
    description="Generate demand forecasts for multiple medications"
)
async def forecast_demand_batch(request: dict) -> dict:
    """
    Generate demand forecasts for multiple medications at once.
    
    **Input:**
    - medications: List of medication IDs
    - consumption_history: Shared consumption history for all medications
    - external_signals: Optional external signals
    
    **Response:**
    - forecasts: List of DemandForecastResponse objects
    - total_demand_30d: Sum of all medication demand predictions
    - execution_time_seconds: Total processing time
    
    **Typical Response Time:** 3-10 seconds (depending on medication count)
    """
    return {
        "message": "Batch forecasting endpoint - use /optimization/run for full pipeline",
        "note": "This endpoint would batch multiple forecasts together"
    }
