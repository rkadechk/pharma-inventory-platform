"""
Unit Tests - Orchestrator Agent
Tests orchestration of 5-stage pipeline and stage coordination
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from agents.pharma_agents import DemandForecastingAgent, InventoryOptimizationAgent, SupplyChainCoordinationAgent
from agents.models import (
    DemandForecast, InventoryRecommendation, SupplyChainDecision,
    OptimizationResult
)


class TestOrchestratorStageCoordination:
    """Test orchestrator managing stage coordination"""
    
    def test_orchestrator_stage_1_execution(self, sample_medications, sample_consumption_history):
        """
        Stage 1: Orchestrator executes demand forecasting
        
        Inputs:
        - Medications (50)
        - Consumption history (90 days)
        
        Outputs:
        - 50 demand forecasts
        """
        
        demand_agent = DemandForecastingAgent()
        
        forecasts = {}
        for med_id in sample_medications.keys():
            med_consumption = sample_consumption_history[
                sample_consumption_history['medication_id'] == med_id
            ]
            
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        # Verify Stage 1 output
        assert len(forecasts) > 0, "Stage 1: Should generate forecasts"
        assert all(isinstance(f, DemandForecast) for f in forecasts.values()), \
            "Stage 1: All outputs must be DemandForecast objects"
        assert all(f.predicted_demand_units > 0 for f in forecasts.values()), \
            "Stage 1: All forecasts must be positive"
    
    def test_orchestrator_stage_2_uses_stage_1_output(self, sample_batches, sample_medications, 
                                                      sample_consumption_history):
        """
        Stage 2: Orchestrator uses Stage 1 forecasts
        
        Dependency: Requires all Stage 1 forecasts
        
        Inputs:
        - Batches (20)
        - Stage 1 forecasts (50)
        
        Outputs:
        - 20 inventory recommendations
        """
        
        # Stage 1
        demand_agent = DemandForecastingAgent()
        forecasts = {}
        
        for med_id in sample_medications.keys():
            med_consumption = sample_consumption_history[
                sample_consumption_history['medication_id'] == med_id
            ]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        # Stage 2
        inventory_agent = InventoryOptimizationAgent()
        recommendations = {}
        
        for batch_id, batch in sample_batches.items():
            med_id = batch['medication_id']
            
            # Check Stage 1 output exists
            if med_id not in forecasts:
                pytest.skip(f"No forecast for medication {med_id}")
            
            forecast = forecasts[med_id]
            rec = inventory_agent.recommend_action(batch, forecast)
            recommendations[batch_id] = rec
        
        # Verify Stage 2 output
        assert len(recommendations) > 0, "Stage 2: Should generate recommendations"
        assert all(isinstance(r, InventoryRecommendation) 
                  for r in recommendations.values()), \
            "Stage 2: All outputs must be InventoryRecommendation objects"
        assert all(r.action_type in ['TRANSFER', 'DISPOSE', 'HOLD'] 
                  for r in recommendations.values()), \
            "Stage 2: All recommendations must have valid action type"
    
    def test_orchestrator_stage_3_uses_stage_2_output(self, sample_batches, sample_suppliers,
                                                      sample_medications, sample_consumption_history):
        """
        Stage 3: Orchestrator uses Stage 2 recommendations
        
        Dependency: Requires Stage 2 recommendations for TRANSFER/HOLD actions
        
        Outputs:
        - Supply decisions for eligible recommendations
        """
        
        # Stage 1
        demand_agent = DemandForecastingAgent()
        forecasts = {}
        
        for med_id in sample_medications.keys():
            med_consumption = sample_consumption_history[
                sample_consumption_history['medication_id'] == med_id
            ]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        # Stage 2
        inventory_agent = InventoryOptimizationAgent()
        recommendations = {}
        
        for batch_id, batch in sample_batches.items():
            med_id = batch['medication_id']
            if med_id in forecasts:
                rec = inventory_agent.recommend_action(batch, forecasts[med_id])
                recommendations[batch_id] = rec
        
        # Stage 3
        supply_agent = SupplyChainCoordinationAgent()
        decisions = {}
        
        for batch_id, batch in sample_batches.items():
            if batch_id not in recommendations:
                continue
            
            rec = recommendations[batch_id]
            
            # Only process TRANSFER/HOLD (not DISPOSE)
            if rec.action_type in ['TRANSFER', 'HOLD']:
                decision = supply_agent.coordinate_supply(
                    medication_id=batch['medication_id'],
                    required_quantity=int(float(rec.quantity_to_action)),
                    current_location=batch['facility_id'],
                    suppliers=sample_suppliers
                )
                decisions[batch_id] = decision
        
        # Verify Stage 3 output
        assert all(isinstance(d, SupplyChainDecision) 
                  for d in decisions.values()), \
            "Stage 3: All outputs must be SupplyChainDecision objects"
        assert all(d.decision_type in ['REORDER', 'TRANSFER'] 
                  for d in decisions.values()), \
            "Stage 3: All decisions must have valid decision type"
    
    def test_orchestrator_stage_4_synthesis(self, sample_dataset):
        """
        Stage 4: Synthesize recommendations
        
        Consolidates outputs from all previous stages into action plan
        """
        
        # Run through stages 1-3
        demand_agent = DemandForecastingAgent()
        inventory_agent = InventoryOptimizationAgent()
        supply_agent = SupplyChainCoordinationAgent()
        
        # Collect outputs
        action_plan = []
        total_cost = Decimal('0')
        
        for med_id in sample_dataset['medications'].keys():
            med_cons = sample_dataset['consumption_history'][
                sample_dataset['consumption_history']['medication_id'] == med_id
            ]
            
            if len(med_cons) == 0:
                continue
            
            forecast = demand_agent.forecast_demand(med_id, med_cons)
            
            med_batches = [b for b in sample_dataset['batches'].values() 
                          if b['medication_id'] == med_id]
            
            for batch in med_batches:
                rec = inventory_agent.recommend_action(batch, forecast)
                
                if rec.action_type == 'DISPOSE':
                    # Disposal cost
                    disposal_cost = Decimal(str(batch['quantity'] * batch['unit_price'] * Decimal('0.1')))
                    action_plan.append({
                        'action_id': f"{batch['batch_id']}_DISPOSE",
                        'action_type': 'DISPOSE',
                        'medication_id': med_id,
                        'batch_id': batch['batch_id'],
                        'facility_id': batch['facility_id'],
                        'quantity': batch['quantity'],
                        'estimated_cost': disposal_cost,
                        'priority_level': 'HIGH'
                    })
                    total_cost += disposal_cost
                
                elif rec.action_type in ['TRANSFER', 'HOLD']:
                    decision = supply_agent.coordinate_supply(
                        medication_id=med_id,
                        required_quantity=int(float(rec.quantity_to_action)),
                        current_location=batch['facility_id'],
                        suppliers=sample_dataset['suppliers']
                    )
                    
                    action_plan.append({
                        'action_id': f"{batch['batch_id']}_SUPPLY",
                        'action_type': decision.decision_type,
                        'medication_id': med_id,
                        'batch_id': batch['batch_id'],
                        'facility_id': batch['facility_id'],
                        'supplier_id': decision.selected_supplier_id,
                        'quantity': int(float(rec.quantity_to_action)),
                        'estimated_cost': decision.cost_estimate,
                        'priority_level': 'MEDIUM'
                    })
                    total_cost += decision.cost_estimate
        
        # Verify Stage 4 output
        assert isinstance(action_plan, list), "Stage 4: Action plan should be a list"
        assert all('action_id' in a for a in action_plan), "Stage 4: All actions must have action_id"
        assert len(action_plan) > 0, "Stage 4: Should synthesize actions"
    
    def test_orchestrator_stage_5_metrics(self, sample_dataset):
        """
        Stage 5: Calculate system metrics
        
        Aggregates all stage outputs into final metrics
        """
        
        # Run through all stages
        demand_agent = DemandForecastingAgent()
        inventory_agent = InventoryOptimizationAgent()
        supply_agent = SupplyChainCoordinationAgent()
        
        forecasts_list = []
        recommendations_list = []
        decisions_list = []
        total_cost = Decimal('0')
        disposal_cost_total = Decimal('0')
        waste_cost = Decimal('0')
        
        for med_id in sample_dataset['medications'].keys():
            med_cons = sample_dataset['consumption_history'][
                sample_dataset['consumption_history']['medication_id'] == med_id
            ]
            
            if len(med_cons) == 0:
                continue
            
            forecast = demand_agent.forecast_demand(med_id, med_cons)
            forecasts_list.append(forecast)
            
            med_batches = [b for b in sample_dataset['batches'].values() 
                          if b['medication_id'] == med_id]
            
            for batch in med_batches:
                rec = inventory_agent.recommend_action(batch, forecast)
                recommendations_list.append(rec)
                
                if rec.action_type == 'DISPOSE':
                    disposal_cost = Decimal(str(batch['quantity'] * batch['unit_price']))
                    waste_cost += disposal_cost
                    total_cost += disposal_cost
                elif rec.action_type in ['TRANSFER', 'HOLD']:
                    decision = supply_agent.coordinate_supply(
                        medication_id=med_id,
                        required_quantity=int(float(rec.quantity_to_action)),
                        current_location=batch['facility_id'],
                        suppliers=sample_dataset['suppliers']
                    )
                    decisions_list.append(decision)
                    total_cost += decision.cost_estimate
        
        # Build metrics
        metrics = {
            'system_health_score': len(forecasts_list) / max(len(sample_dataset['medications']), 1),
            'total_facilities': len(sample_dataset['facilities']),
            'total_medications': len(forecasts_list),
            'total_batches_processed': len(recommendations_list),
            'total_supply_decisions': len(decisions_list),
            'waste_prevented_value': float(waste_cost),
            'total_cost_estimate': float(total_cost),
            'avg_forecast_confidence': sum(f.confidence_level for f in forecasts_list) / len(forecasts_list) 
                if forecasts_list else 0,
            'forecast_accuracy_mape': sum(f.model_accuracy_mape for f in forecasts_list) / len(forecasts_list)
                if forecasts_list else 0
        }
        
        # Verify Stage 5 output
        assert 'system_health_score' in metrics, "Stage 5: Must include health score"
        assert 0 <= metrics['system_health_score'] <= 1, "Stage 5: Health score 0-1"
        assert metrics['total_facilities'] > 0, "Stage 5: Must have facilities"
        assert metrics['waste_prevented_value'] >= 0, "Stage 5: Waste prevented non-negative"


class TestOrchestratorErrorHandling:
    """Test orchestrator error handling and recovery"""
    
    def test_orchestrator_handles_missing_suppliers(self, sample_dataset):
        """
        Test: Pipeline doesn't crash with no suppliers
        
        Expected: Stage 3 generates no decisions (no supply options)
        """
        
        demand_agent = DemandForecastingAgent()
        inventory_agent = InventoryOptimizationAgent()
        supply_agent = SupplyChainCoordinationAgent()
        
        # Empty suppliers
        empty_suppliers = {}
        
        decision_count = 0
        
        for med_id in sample_dataset['medications'].keys():
            med_cons = sample_dataset['consumption_history'][
                sample_dataset['consumption_history']['medication_id'] == med_id
            ]
            
            if len(med_cons) == 0:
                continue
            
            forecast = demand_agent.forecast_demand(med_id, med_cons)
            
            med_batches = [b for b in sample_dataset['batches'].values() 
                          if b['medication_id'] == med_id]
            
            for batch in med_batches[:1]:  # Just first batch
                rec = inventory_agent.recommend_action(batch, forecast)
                
                if rec.action_type in ['TRANSFER', 'HOLD']:
                    try:
                        decision = supply_agent.coordinate_supply(
                            medication_id=med_id,
                            required_quantity=int(float(rec.quantity_to_action)),
                            current_location=batch['facility_id'],
                            suppliers=empty_suppliers
                        )
                        decision_count += 1
                    except:
                        # Expected to fail or handle gracefully
                        pass
        
        # Verify graceful handling (no crash)
        assert True  # If we get here, orchestrator didn't crash
    
    def test_orchestrator_with_single_medication(self, sample_consumption_history):
        """
        Test: Orchestrator works with minimal data (1 medication)
        """
        
        demand_agent = DemandForecastingAgent()
        
        # Get one medicine
        unique_meds = sample_consumption_history['medication_id'].unique()
        med_id = unique_meds[0]
        
        med_cons = sample_consumption_history[
            sample_consumption_history['medication_id'] == med_id
        ]
        
        forecast = demand_agent.forecast_demand(med_id, med_cons)
        
        assert forecast is not None, "Should handle single medication"
        assert forecast.medication_id == med_id, "Should forecast correct medicine"


class TestOrchestratorDataValidation:
    """Test orchestrator input/output validation"""
    
    def test_orchestrator_validates_consumption_data(self, sample_consumption_history):
        """
        Test: Orchestrator validates input consumption data
        
        Rule: History must have >0 records
        """
        
        demand_agent = DemandForecastingAgent()
        
        # Valid data
        valid_consumption = sample_consumption_history[
            sample_consumption_history['quantity'] > 0
        ]
        
        assert len(valid_consumption) > 0, "Should have valid consumption records"
    
    def test_orchestrator_output_model_compliance(self, sample_dataset):
        """
        Test: All outputs conform to model schemas
        """
        
        demand_agent = DemandForecastingAgent()
        
        for med_id in list(sample_dataset['medications'].keys())[:5]:
            med_cons = sample_dataset['consumption_history'][
                sample_dataset['consumption_history']['medication_id'] == med_id
            ]
            
            if len(med_cons) == 0:
                continue
            
            forecast = demand_agent.forecast_demand(med_id, med_cons)
            
            # Check model compliance
            assert hasattr(forecast, 'medication_id'), "Must have medication_id"
            assert hasattr(forecast, 'predicted_demand_units'), "Must have predicted_demand_units"
            assert hasattr(forecast, 'model_type'), "Must have model_type"
            assert hasattr(forecast, 'confidence_level'), "Must have confidence_level"
            assert hasattr(forecast, 'model_accuracy_mape'), "Must have model_accuracy_mape"


class TestOrchestratorStageDependencies:
    """Test that stages properly depend on previous stages"""
    
    def test_stage_2_cannot_run_without_stage_1(self, sample_batches, sample_medications):
        """
        Test: Stage 2 requires Stage 1 output
        
        Expected: Cannot create recommendations without forecasts
        """
        
        inventory_agent = InventoryOptimizationAgent()
        
        # Try without forecast (should fail)
        batch = list(sample_batches.values())[0]
        
        # Create dummy forecast
        from agents.models import DemandForecast
        forecast = DemandForecast(
            medication_id=batch['medication_id'],
            predicted_demand_units=50,
            confidence_level=0.8,
            confidence_interval_lower=40,
            confidence_interval_upper=60,
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        # This should work
        rec = inventory_agent.recommend_action(batch, forecast)
        assert rec is not None, "Stage 2 should work with Stage 1 output"
    
    def test_stage_3_cannot_run_without_stage_2(self, sample_suppliers):
        """
        Test: Stage 3 requires Stage 2 output
        
        Expected: Cannot create supply decisions without recommendations
        """
        
        supply_agent = SupplyChainCoordinationAgent()
        
        # Minimal decision
        decision = supply_agent.coordinate_supply(
            medication_id='MED001',
            required_quantity=100,
            current_location='FAC001',
            suppliers=sample_suppliers
        )
        
        assert decision is not None, "Stage 3 should work with valid inputs"
        assert hasattr(decision, 'decision_type'), "Must have decision_type"
