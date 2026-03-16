"""Full Optimization Pipeline Route"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import asyncio
import logging
from datetime import datetime

from agents.orchestrator import Orchestrator
from app.schemas.optimization import FullOptimizationRequest, FullOptimizationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/run",
    response_model=FullOptimizationResponse,
    summary="Run Full Pharmaceutical Inventory Optimization",
    description="Execute the complete 7-stage optimization pipeline"
)
async def run_full_optimization(request: FullOptimizationRequest) -> FullOptimizationResponse:
    """
    Execute the complete pharmaceutical inventory optimization pipeline.
    
    This endpoint runs all three agents (Demand Forecasting, Inventory Optimization, 
    Supply Chain Coordination) in sequence with full validation at each stage.
    
    **Pipeline Stages:**
    1. **STAGE 0** - Input Data Validation
    2. **STAGE 1** - Demand Forecasting (Prophet/ARIMA/Baseline)
    3. **STAGE 2** - Inventory Optimization (Risk detection, expiration analysis)
    4. **STAGE 3** - Supply Chain Coordination (Reorder vs transfer decisions)
    5. **STAGE 4** - Action Plan Synthesis (Integrated recommendations)
    6. **STAGE 5** - System Metrics (KPI calculation)
    7. **STAGE 6** - Cross-Validation (Output consistency checks)
    8. **STAGE 7** - Quality Report Generation (Data quality scoring)
    
    **Input Requirements:**
    - facility_inventory: Current medication batches across facilities
    - consumption_history: Historical consumption data (min 30 days recommended)
    - suppliers: Available suppliers with pricing and lead times
    
    **Response Includes:**
    - Demand forecasts for all medications
    - Inventory recommendations (transfer/dispose/hold/reorder)
    - Supply chain optimization decisions
    - Comprehensive action plan with priorities
    - System metrics and KPIs
    - Data quality report
    - Validation results from all stages
    
    **Typical Response Time:** 2-5 seconds
    
    **Error Handling:**
    - 400: Invalid request data
    - 422: Validation error in request schema
    - 500: Server error during optimization
    """
    try:
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        logger.info(f"Starting optimization pipeline with {len(request.facility_inventory)} batches")
        
        # Execute optimization
        result = await orchestrator.execute_full_optimization(
            facility_inventory=request.facility_inventory,
            consumption_history=request.consumption_history,
            suppliers=request.suppliers,
            external_signals=request.external_signals or {},
            transfer_cost_matrix=request.transfer_cost_matrix or {},
            forecast_days=request.forecast_days
        )
        
        logger.info(f"Optimization completed successfully in {result['execution_time_seconds']:.2f}s")
        
        # Construct response
        response = FullOptimizationResponse(
            status=result.get('status', 'completed'),
            execution_time_seconds=result.get('execution_time_seconds', 0),
            demand_forecasts=result.get('demand_forecasts', []),
            inventory_recommendations=result.get('inventory_recommendations', []),
            supply_decisions=result.get('supply_decisions', []),
            action_plan=result.get('action_plan', {}),
            system_metrics=result.get('system_metrics', {}),
            quality_report=result.get('quality_report', {}),
            validation_results=result.get('validation_results', {}),
            agent_metrics=result.get('agent_metrics', None)
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Optimization pipeline failed: {str(e)}"
        )


@router.post(
    "/status/{execution_id}",
    response_model=dict,
    summary="Check Optimization Status",
    description="Get the status of an ongoing optimization (for async execution)"
)
async def check_optimization_status(execution_id: str) -> dict:
    """
    Check the status of an optimization execution.
    
    This endpoint is useful for tracking long-running optimizations.
    (Currently returns placeholder - would be implemented with job queue)
    
    **Response Statuses:**
    - queued: Job is queued but not started
    - running: Job is currently executing
    - completed: Job finished successfully
    - failed: Job encountered an error
    """
    return {
        "execution_id": execution_id,
        "status": "completed",
        "progress": 100,
        "message": "Optimization result ready"
    }
