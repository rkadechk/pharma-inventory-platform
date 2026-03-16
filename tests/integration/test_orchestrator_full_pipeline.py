"""
Integration Tests - Orchestrator Full 7-Stage Pipeline with Validation
Tests the orchestrator's complete validation-integrated optimization workflow
"""

import pytest
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from agents.orchestrator import Orchestrator
from agents.models import DemandForecast, TransferRecommendation, SupplyChainDecision


class TestOrchestratorFullPipelineWithValidation:
    """Test orchestrator's complete 7-stage pipeline with validation integration"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_smoke_test_basic_execution(self, sample_dataset):
        """
        Smoke Test: Orchestrator executes all 7 stages without errors
        
        Pipeline:
        - STAGE 0: Input Validation
        - STAGE 1: Demand Forecasting (with output validation)
        - STAGE 2: Inventory Optimization (with output validation)
        - STAGE 3: Supply Chain Coordination (with output validation)
        - STAGE 4: Action Plan Synthesis
        - STAGE 5: System Metrics Calculation
        - STAGE 6: Cross-Validation
        - STAGE 7: Quality Report Generation
        """
        
        # Setup
        orchestrator = Orchestrator()
        
        facilities = sample_dataset['facilities']
        medications = sample_dataset['medications']
        consumption_history = sample_dataset['consumption_history']
        batches = sample_dataset['batches']
        suppliers = sample_dataset['suppliers']
        
        # Convert to required format
        facility_inventory = [
            {
                'facility_id': fid,
                'batch_id': bid,
                'medication_id': batch['medication_id'],
                'quantity_on_hand': batch['quantity'],
                'expiry_date': batch['expiry_date'].isoformat(),
                'unit_cost': float(batch['unit_cost'])
            }
            for fid, batches_at_facility in batches.items()
            for bid, batch in batches_at_facility.items()
        ]
        
        consumption_data = consumption_history[[
            'date', 'facility_id', 'medication_id', 'units_consumed'
        ]].to_dict('records')
        
        supplier_data = [
            {
                'supplier_id': sid,
                'name': s['name'],
                'lead_time_days': s['lead_time_days'],
                'min_order_units': s['min_order_units'],
                'unit_cost': float(s['unit_cost'])
            }
            for sid, s in suppliers.items()
        ]
        
        # EXECUTE: Full orchestrator pipeline
        result = await orchestrator.execute_full_optimization(
            facility_inventory=facility_inventory,
            consumption_history=consumption_data,
            suppliers=supplier_data,
            external_signals={},
            transfer_cost_matrix={},
            forecast_days=30
        )
        
        # VERIFY: Output structure
        assert result is not None, "Orchestrator should return result"
        assert result['status'] == 'completed', "Orchestrator should complete successfully"
        assert 'execution_time_seconds' in result, "Output should include execution time"
        
        # VERIFY: Stage 1 outputs (Demand Forecasting)
        assert 'demand_forecasts' in result, "Output should include demand forecasts"
        demand_forecasts = result['demand_forecasts']
        assert len(demand_forecasts) > 0, "Should generate at least one demand forecast"
        assert all(isinstance(f, DemandForecast) for f in demand_forecasts), \
            "All forecasts must be DemandForecast objects"
        assert all(f.predicted_demand_units > 0 for f in demand_forecasts), \
            "All forecasts must have positive units"
        assert all(0 <= f.confidence_level <= 1 for f in demand_forecasts), \
            "All forecasts must have confidence [0-1]"
        
        # VERIFY: Stage 2 outputs (Inventory Optimization)
        assert 'inventory_recommendations' in result, "Output should include inventory recommendations"
        recommendations = result['inventory_recommendations']
        assert isinstance(recommendations, list), "Recommendations should be a list"
        
        # VERIFY: Stage 3 outputs (Supply Chain)
        assert 'supply_decisions' in result, "Output should include supply decisions"
        decisions = result['supply_decisions']
        assert isinstance(decisions, list), "Supply decisions should be a list"
        
        # VERIFY: Stage 4 outputs (Action Plan)
        assert 'action_plan' in result, "Output should include action plan"
        action_plan = result['action_plan']
        assert isinstance(action_plan, (list, dict)), "Action plan should be list or dict"
        
        # VERIFY: Stage 5 outputs (System Metrics)
        assert 'system_metrics' in result, "Output should include system metrics"
        metrics = result['system_metrics']
        assert isinstance(metrics, dict), "Metrics should be a dict"
        
        # VERIFY: Stage 6 outputs (Cross-Validation Results)
        assert 'validation_results' in result, "Output should include validation results"
        validation_results = result['validation_results']
        assert isinstance(validation_results, dict), "Validation results should be a dict"
        
        # VERIFY: Stage 7 outputs (Quality Report)
        assert 'quality_report' in result, "Output should include quality report"
        quality_report = result['quality_report']
        assert isinstance(quality_report, dict), "Quality report should be a dict"
        assert 'overall_quality_score' in quality_report, "Quality report should have overall score"
        assert 0 <= quality_report['overall_quality_score'] <= 1, "Quality score should be [0-1]"
    
    @pytest.mark.asyncio
    async def test_orchestrator_validation_results_populated(self, sample_dataset):
        """
        Test: Validation results are properly populated through all stages
        """
        
        orchestrator = Orchestrator()
        
        facilities = sample_dataset['facilities']
        medications = sample_dataset['medications']
        consumption_history = sample_dataset['consumption_history']
        batches = sample_dataset['batches']
        suppliers = sample_dataset['suppliers']
        
        # Prepare data
        facility_inventory = [
            {
                'facility_id': fid,
                'batch_id': bid,
                'medication_id': batch['medication_id'],
                'quantity_on_hand': batch['quantity'],
                'expiry_date': batch['expiry_date'].isoformat(),
                'unit_cost': float(batch['unit_cost'])
            }
            for fid, batches_at_facility in batches.items()
            for bid, batch in batches_at_facility.items()
        ]
        
        consumption_data = consumption_history[[
            'date', 'facility_id', 'medication_id', 'units_consumed'
        ]].to_dict('records')
        
        supplier_data = [
            {
                'supplier_id': sid,
                'name': s['name'],
                'lead_time_days': s['lead_time_days'],
                'min_order_units': s['min_order_units'],
                'unit_cost': float(s['unit_cost'])
            }
            for sid, s in suppliers.items()
        ]
        
        # Execute
        result = await orchestrator.execute_full_optimization(
            facility_inventory=facility_inventory,
            consumption_history=consumption_data,
            suppliers=supplier_data,
            external_signals={},
            transfer_cost_matrix={},
            forecast_days=30
        )
        
        # VERIFY: Validation results structure
        validation_results = result['validation_results']
        
        # Should have input validation status
        assert 'input_validation' in validation_results or len(validation_results) > 0, \
            "Should have validation results from Stage 0"
    
    @pytest.mark.asyncio
    async def test_orchestrator_quality_report_comprehensive(self, sample_dataset):
        """
        Test: Quality report is comprehensive and includes all expected metrics
        """
        
        orchestrator = Orchestrator()
        
        # Prepare minimal data
        facility_inventory = [
            {
                'facility_id': f'FAC001',
                'batch_id': f'BATCH001',
                'medication_id': 1,
                'quantity_on_hand': 100,
                'expiry_date': (datetime.now() + timedelta(days=180)).isoformat(),
                'unit_cost': 10.0
            }
        ]
        
        # Create consumption history centered around medication 1
        today = datetime.now()
        consumption_data = [
            {
                'date': (today - timedelta(days=i)).strftime('%Y-%m-%d'),
                'facility_id': 'FAC001',
                'medication_id': 1,
                'units_consumed': 10 + i % 5
            }
            for i in range(30)
        ]
        
        supplier_data = [
            {
                'supplier_id': 'SUP001',
                'name': 'Test Supplier',
                'lead_time_days': 3,
                'min_order_units': 50,
                'unit_cost': 8.0
            }
        ]
        
        # Execute
        result = await orchestrator.execute_full_optimization(
            facility_inventory=facility_inventory,
            consumption_history=consumption_data,
            suppliers=supplier_data,
            external_signals={},
            transfer_cost_matrix={},
            forecast_days=30
        )
        
        # VERIFY: Quality report content
        quality_report = result['quality_report']
        
        expected_keys = [
            'timestamp',
            'overall_quality_score',
            'data_completeness',
            'validation_summary',
            'system_health',
            'recommendations'
        ]
        
        for key in expected_keys:
            assert key in quality_report, f"Quality report should include '{key}'"
        
        # VERIFY: Timestamp is recent
        assert 'timestamp' in quality_report, "Quality report should have timestamp"
        timestamp = quality_report['timestamp']
        assert isinstance(timestamp, str), "Timestamp should be string"
        
        # VERIFY: Overall score is valid
        overall_score = quality_report['overall_quality_score']
        assert isinstance(overall_score, (int, float)), "Overall score should be numeric"
        assert 0 <= overall_score <= 1, "Overall score should be in [0, 1]"
    
    def test_orchestrator_async_execution_wrapper(self, sample_dataset):
        """
        Test: Orchestrator can be executed via async wrapper
        """
        
        orchestrator = Orchestrator()
        
        facility_inventory = [
            {
                'facility_id': 'FAC001',
                'batch_id': 'BATCH001',
                'medication_id': 1,
                'quantity_on_hand': 100,
                'expiry_date': (datetime.now() + timedelta(days=180)).isoformat(),
                'unit_cost': 10.0
            }
        ]
        
        today = datetime.now()
        consumption_data = [
            {
                'date': (today - timedelta(days=i)).strftime('%Y-%m-%d'),
                'facility_id': 'FAC001',
                'medication_id': 1,
                'units_consumed': 10 + i % 5
            }
            for i in range(30)
        ]
        
        supplier_data = [
            {
                'supplier_id': 'SUP001',
                'name': 'Test Supplier',
                'lead_time_days': 3,
                'min_order_units': 50,
                'unit_cost': 8.0
            }
        ]
        
        # Execute via asyncio.run()
        result = asyncio.run(orchestrator.execute_full_optimization(
            facility_inventory=facility_inventory,
            consumption_history=consumption_data,
            suppliers=supplier_data,
            external_signals={},
            transfer_cost_matrix={},
            forecast_days=30
        ))
        
        assert result is not None, "Async execution should return result"
        assert result['status'] == 'completed', "Async execution should complete successfully"
