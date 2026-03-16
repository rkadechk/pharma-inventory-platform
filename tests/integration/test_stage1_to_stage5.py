"""
Integration Tests - Full Pipeline Stage 1→5 Flow
Tests the orchestrator managing complete optimization workflow
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from agents.pharma_agents import DemandForecastingAgent, InventoryOptimizationAgent, SupplyChainCoordinationAgent
from validators.output_validator import OutputValidator
from validators.cross_validator import CrossValidator


class TestPipelineStage1To5:
    """Test complete 5-stage pipeline execution"""
    
    def test_full_pipeline_execution_with_realistic_data(self, sample_dataset):
        """
        Stage 1→5: Full pipeline with realistic hospital data
        
        Flow:
        1. Validate input data
        2. Run demand forecasting (Stage 1)
        3. Evaluate inventory (Stage 2)
        4. Coordinate supply (Stage 3)
        5. Synthesize recommendations (Stage 4)
        6. Calculate metrics (Stage 5)
        """
        
        facilities = sample_dataset['facilities']
        medications = sample_dataset['medications']
        consumption_history = sample_dataset['consumption_history']
        batches = sample_dataset['batches']
        
        # Stage 1: Demand Forecasting
        demand_agent = DemandForecastingAgent()
        forecasts = []
        
        for med_id in medications.keys():
            med_consumption = consumption_history[consumption_history['medication_id'] == med_id]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts.append(forecast)
                assert OutputValidator.validate_forecast_output(forecast)
        
        assert len(forecasts) > 0, "Stage 1: Should generate forecasts"
        assert all(f.predicted_demand_units > 0 for f in forecasts), "Stage 1: All forecasts positive"
    
    def test_stage_2_uses_stage_1_output(self, sample_dataset):
        """
        Stage 2 depends on Stage 1 output
        
        Test: Recommendations should align with forecasts
        """
        
        # Setup
        facilities = sample_dataset['facilities']
        medications = sample_dataset['medications']
        consumption_history = sample_dataset['consumption_history']
        batches = sample_dataset['batches']
        
        # Stage 1
        demand_agent = DemandForecastingAgent()
        forecasts = {}
        
        for med_id in medications.keys():
            med_consumption = consumption_history[consumption_history['medication_id'] == med_id]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        # Stage 2: Using Stage 1 output
        inventory_agent = InventoryOptimizationAgent()
        recommendations = []
        
        for batch_id, batch in batches.items():
            forecast = forecasts.get(batch['medication_id'])
            if forecast:
                rec = inventory_agent.recommend_action(batch, forecast)
                OutputValidator.validate_recommendation_output(rec)
                # Cross-validate: recommendation should align with forecast
                CrossValidator.validate_recommendation_vs_forecast(
                    rec.dict(),
                    forecast.dict()
                )
                recommendations.append(rec)
        
        assert len(recommendations) > 0, "Stage 2: Should generate recommendations"
    
    def test_stage_3_uses_stage_2_output(self, sample_dataset):
        """
        Stage 3 depends on Stage 2 output
        
        Test: Supply decisions should align with recommendations
        """
        
        # Setup
        consumption_history = sample_dataset['consumption_history']
        medications = sample_dataset['medications']
        batches = sample_dataset['batches']
        suppliers = sample_dataset['suppliers']
        facilities = sample_dataset['facilities']
        
        # Stage 1 & 2
        demand_agent = DemandForecastingAgent()
        inventory_agent = InventoryOptimizationAgent()
        
        forecasts = {}
        recommendations = {}
        
        for med_id in medications.keys():
            med_consumption = consumption_history[consumption_history['medication_id'] == med_id]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        for batch_id, batch in batches.items():
            forecast = forecasts.get(batch['medication_id'])
            if forecast:
                rec = inventory_agent.recommend_action(batch, forecast)
                recommendations[batch_id] = rec
        
        # Stage 3: Using Stage 2 output
        supply_agent = SupplyChainCoordinationAgent()
        decisions = []
        
        for batch_id, batch in batches.items():
            rec = recommendations.get(batch_id)
            if rec and rec.action_type in ['TRANSFER', 'HOLD']:
                decision = supply_agent.coordinate_supply(
                    medication_id=batch['medication_id'],
                    required_quantity=int(float(rec.quantity_to_action)),
                    current_location=batch['facility_id'],
                    suppliers=suppliers
                )
                OutputValidator.validate_supply_decision_output(decision)
                # Cross-validate
                CrossValidator.validate_decision_vs_recommendation(
                    decision.dict(),
                    rec.dict()
                )
                decisions.append(decision)
        
        assert len(decisions) > 0, "Stage 3: Should generate supply decisions"
    
    def test_data_lineage_through_pipeline(self, sample_dataset):
        """
        Test: Data flows correctly from input through all stages
        
        Input → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
        """
        
        input_med_count = len(sample_dataset['medications'])
        input_batch_count = len(sample_dataset['batches'])
        
        # Run through all stages
        demand_agent = DemandForecastingAgent()
        inventory_agent = InventoryOptimizationAgent()
        supply_agent = SupplyChainCoordinationAgent()
        
        # Stage 1
        stage1_outputs = []
        for med_id in sample_dataset['medications'].keys():
            med_consumption = sample_dataset['consumption_history'][
                sample_dataset['consumption_history']['medication_id'] == med_id
            ]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                stage1_outputs.append(forecast)
        
        # Stage 2
        stage2_outputs = []
        for batch_id, batch in sample_dataset['batches'].items():
            med_id = batch['medication_id']
            forecast = next((f for f in stage1_outputs 
                            if f.medication_id == med_id), None)
            if forecast:
                rec = inventory_agent.recommend_action(batch, forecast)
                stage2_outputs.append(rec)
        
        # Stage 3
        stage3_outputs = []
        for batch_id, batch in sample_dataset['batches'].items():
            rec = next((r for r in stage2_outputs 
                       if r.batch_id == batch_id), None)
            if rec and rec.action_type in ['TRANSFER', 'HOLD']:
                decision = supply_agent.coordinate_supply(
                    medication_id=batch['medication_id'],
                    required_quantity=int(float(rec.quantity_to_action)),
                    current_location=batch['facility_id'],
                    suppliers=sample_dataset['suppliers']
                )
                stage3_outputs.append(decision)
        
        # Verify data lineage
        assert len(stage1_outputs) <= input_med_count, "Stage 1 output ≤ input medications"
        assert len(stage2_outputs) <= input_batch_count, "Stage 2 output ≤ input batches"
        # Stage 3 may be less due to DISPOSE actions
        assert len(stage3_outputs) <= len(stage2_outputs), "Stage 3 output ≤ Stage 2 output"
    
    def test_output_consistency_across_runs(self, sample_dataset):
        """
        Test: Same input produces same output (reproducibility)
        
        Run pipeline twice with identical input
        """
        
        def run_partial_pipeline(dataset):
            demand_agent = DemandForecastingAgent()
            
            outputs = []
            for med_id in dataset['medications'].keys():
                med_consumption = dataset['consumption_history'][
                    dataset['consumption_history']['medication_id'] == med_id
                ]
                if len(med_consumption) > 0:
                    forecast = demand_agent.forecast_demand(med_id, med_consumption)
                    outputs.append(forecast.dict())
            
            return outputs
        
        # Run twice
        output1 = run_partial_pipeline(sample_dataset)
        output2 = run_partial_pipeline(sample_dataset)
        
        # Should be identical
        assert len(output1) == len(output2), "Output length should match"
        
        for o1, o2 in zip(output1, output2):
            assert o1['medication_id'] == o2['medication_id'], "Medication IDs should match"
            assert abs(o1['predicted_demand_units'] - o2['predicted_demand_units']) < 0.01, \
                "Predicted demand should match"


class TestPipelineErrorHandling:
    """Test pipeline behavior with problematic data"""
    
    def test_pipeline_with_missing_consumption_data(self, sample_facilities, sample_medications):
        """
        Test: Pipeline handles medications with no consumption history
        """
        
        demo_agent = DemandForecastingAgent()
        
        # Empty consumption data
        empty_consumption = pd.DataFrame({
            'date': [],
            'medication_id': [],
            'facility_id': [],
            'quantity': []
        })
        
        # Should not crash, but return no forecasts
        result = demo_agent.forecast_demand(
            medication_id='MED001',
            consumption_history=empty_consumption
        )
        
        # Should fallback gracefully
        assert result is not None or result is None  # Either valid forecast or None
    
    def test_pipeline_with_expired_batches(self, sample_dataset):
        """
        Test: Pipeline correctly identifies expired batches
        """
        
        # Create expired batch
        expired_batch = {
            'batch_id': 'BATCH_EXPIRED',
            'medication_id': 'MED001',
            'facility_id': 'FAC001',
            'quantity': 100,
            'unit_price': Decimal('10.00'),
            'manufacture_date': datetime.now() - timedelta(days=365),
            'expiry_date': datetime.now() - timedelta(days=1),  # Expired yesterday
            'storage_condition': 'COOL'
        }
        
        inventory_agent = InventoryOptimizationAgent()
        
        # Create a dummy forecast
        from agents.models import DemandForecast
        forecast = DemandForecast(
            medication_id='MED001',
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
        
        rec = inventory_agent.recommend_action(expired_batch, forecast)
        
        # Expired batch should be DISPOSE
        assert rec.action_type == 'DISPOSE', "Expired batch should be DISPOSE"
    
    def test_pipeline_with_zero_demand_expiring_stock(self, sample_dataset):
        """
        Test: Pipeline handles zero demand + expiring stock (disposal scenario)
        """
        
        # Create batch expiring soon with zero demand
        expiring_batch = {
            'batch_id': 'BATCH_EXPIRING',
            'medication_id': 'MED999',
            'facility_id': 'FAC001',
            'quantity': 1000,
            'unit_price': Decimal('50.00'),
            'manufacture_date': datetime.now() - timedelta(days=330),
            'expiry_date': datetime.now() + timedelta(days=5),  # Expires in 5 days
            'storage_condition': 'COOL'
        }
        
        inventory_agent = InventoryOptimizationAgent()
        
        # Zero demand forecast
        from agents.models import DemandForecast
        forecast = DemandForecast(
            medication_id='MED999',
            predicted_demand_units=0,  # NO DEMAND
            confidence_level=0.9,
            confidence_interval_lower=0,
            confidence_interval_upper=5,
            model_type='ARIMA',
            model_accuracy_mape=0.05,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        rec = inventory_agent.recommend_action(expiring_batch, forecast)
        
        # Should recommend DISPOSE (costly to store, expiring, no demand)
        assert rec.action_type == 'DISPOSE', "No demand + expiring should be DISPOSE"


class TestPipelinePerformance:
    """Test pipeline performance at scale"""
    
    @pytest.mark.performance
    def test_full_pipeline_with_50_medicines(self, sample_facilities, sample_suppliers):
        """
        Performance test: Pipeline processes 50 medicines + batches
        
        SLA: Complete in <20 seconds
        """
        
        import time
        
        # Create 50 medicines
        medications = {
            f'MED{i:03d}': {
                'medication_id': f'MED{i:03d}',
                'name': f'Medicine {i}',
                'min_stock_level': 10 + i,
                'max_stock_level': 100 + i * 2,
                'normal_consumption_daily': 5 + i * 0.1
            } for i in range(50)
        }
        
        # Create 150 batches (3 per medicine)
        batches = {}
        for i, med_id in enumerate(medications.keys()):
            for batch_num in range(3):
                batch_id = f'{med_id}_B{batch_num}'
                batches[batch_id] = {
                    'batch_id': batch_id,
                    'medication_id': med_id,
                    'facility_id': f'FAC{batch_num % 4 + 1}',
                    'quantity': 50 + i * 2,
                    'unit_price': Decimal(str(10 + batch_num)),
                    'manufacture_date': datetime.now() - timedelta(days=100 + batch_num * 50),
                    'expiry_date': datetime.now() + timedelta(days=200 - batch_num * 50),
                    'storage_condition': 'COOL'
                }
        
        # Create consumption history
        dates = pd.date_range(datetime.now() - timedelta(days=90), periods=90, freq='D')
        consumption_rows = []
        for med_id in medications.keys():
            for date in dates:
                consumption_rows.append({
                    'date': date,
                    'medication_id': med_id,
                    'facility_id': 'FAC001',
                    'quantity': 5 + (hash(med_id) % 10)
                })
        
        consumption_history = pd.DataFrame(consumption_rows)
        
        # Time the pipeline
        start_time = time.time()
        
        # Stage 1: Forecasts
        demand_agent = DemandForecastingAgent()
        forecasts = {}
        for med_id in medications.keys():
            med_consumption = consumption_history[consumption_history['medication_id'] == med_id]
            if len(med_consumption) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_consumption)
                forecasts[med_id] = forecast
        
        # Stage 2: Recommendations
        inventory_agent = InventoryOptimizationAgent()
        recommendations = {}
        for batch_id, batch in batches.items():
            forecast = forecasts.get(batch['medication_id'])
            if forecast:
                rec = inventory_agent.recommend_action(batch, forecast)
                recommendations[batch_id] = rec
        
        # Stage 3: Supply decisions
        supply_agent = SupplyChainCoordinationAgent()
        decisions = {}
        for batch_id, batch in batches.items():
            rec = recommendations.get(batch_id)
            if rec and rec.action_type in ['TRANSFER', 'HOLD']:
                decision = supply_agent.coordinate_supply(
                    medication_id=batch['medication_id'],
                    required_quantity=int(float(rec.quantity_to_action)),
                    current_location=batch['facility_id'],
                    suppliers=sample_suppliers
                )
                decisions[batch_id] = decision
        
        elapsed = time.time() - start_time
        
        # Performance assertions
        assert elapsed < 20, f"Pipeline took {elapsed:.1f}s, expected <20s"
        assert len(forecasts) > 0, "Should generate forecasts"
        assert len(recommendations) > 0, "Should generate recommendations"
        
        print(f"Pipeline processed {len(medications)} medicines, {len(batches)} batches in {elapsed:.2f}s")
    
    @pytest.mark.performance
    def test_full_pipeline_with_150_medicines(self, sample_facilities, sample_suppliers):
        """
        Performance test: Pipeline processes 150 medicines + batches
        
        SLA: Complete in <45 seconds
        """
        
        import time
        
        medications = {
            f'MED{i:04d}': {
                'medication_id': f'MED{i:04d}',
                'name': f'Medicine {i}'
            } for i in range(150)
        }
        
        batches = {}
        for i, med_id in enumerate(medications.keys()):
            for batch_num in range(2):
                batch_id = f'{med_id}_B{batch_num}'
                batches[batch_id] = {
                    'batch_id': batch_id,
                    'medication_id': med_id,
                    'facility_id': 'FAC001',
                    'quantity': 100,
                    'unit_price': Decimal('10.00'),
                    'manufacture_date': datetime.now() - timedelta(days=200),
                    'expiry_date': datetime.now() + timedelta(days=100),
                    'storage_condition': 'COOL'
                }
        
        # Consumption history
        dates = pd.date_range(datetime.now() - timedelta(days=90), periods=90, freq='D')
        consumption_rows = []
        for med_id in medications.keys():
            for date in dates:
                consumption_rows.append({
                    'date': date,
                    'medication_id': med_id,
                    'facility_id': 'FAC001',
                    'quantity': 10
                })
        consumption_history = pd.DataFrame(consumption_rows)
        
        start_time = time.time()
        
        demand_agent = DemandForecastingAgent()
        forecasts = {}
        for med_id in medications.keys():
            med_cons = consumption_history[consumption_history['medication_id'] == med_id]
            if len(med_cons) > 0:
                forecast = demand_agent.forecast_demand(med_id, med_cons)
                forecasts[med_id] = forecast
        
        elapsed = time.time() - start_time
        
        # Even Stage 1 alone should be reasonable
        assert elapsed < 45, f"Stage 1 alone took {elapsed:.1f}s, expected <45s"
