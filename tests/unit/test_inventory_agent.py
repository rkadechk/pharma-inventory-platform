"""
Unit tests for Inventory Optimization Agent
Tests batch evaluation, cost analysis, and recommendation generation
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from agents.inventory_agent import InventoryOptimizationAgent
from agents.models import InventoryBatch, DemandForecast, InventoryRecommendation


class TestInventoryAgentBatchDetection:
    """Test at-risk batch detection"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    @pytest.fixture
    def batch_expiring_soon(self):
        """Batch expiring in 10 days"""
        return InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
    
    @pytest.fixture
    def batch_not_expiring_soon(self):
        """Batch expiring in 90 days"""
        return InventoryBatch(
            batch_id=2,
            medication_id=2,
            batch_number="BATCH-002",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=90),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-2"
        )
    
    @pytest.fixture
    def batch_expired(self):
        """Already expired batch"""
        return InventoryBatch(
            batch_id=3,
            medication_id=3,
            batch_number="BATCH-003",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() - timedelta(days=5),
            manufacture_date=datetime.now() - timedelta(days=365),
            facility_id=1,
            storage_location="A-1-3"
        )
    
    def test_detect_expiring_batch(self, agent, batch_expiring_soon):
        """Test detection of batch expiring soon"""
        at_risk = agent.is_batch_at_risk(batch_expiring_soon, days_threshold=14)
        assert at_risk is True
    
    def test_non_expiring_batch(self, agent, batch_not_expiring_soon):
        """Test non-expiring batch not flagged"""
        at_risk = agent.is_batch_at_risk(batch_not_expiring_soon, days_threshold=14)
        assert at_risk is False
    
    def test_expired_batch_detection(self, agent, batch_expired):
        """Test expired batch detected"""
        at_risk = agent.is_batch_at_risk(batch_expired, days_threshold=0)
        assert at_risk is True
    
    def test_days_until_expiry_calculation(self, agent, batch_expiring_soon):
        """Test days until expiry calculated correctly"""
        days = agent._calculate_days_until_expiry(batch_expiring_soon)
        assert 9 <= days <= 11  # Allow 1 day rounding


class TestInventoryAgentDemandAnalysis:
    """Test demand vs inventory analysis"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    @pytest.fixture
    def batch(self):
        return InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
    
    @pytest.fixture
    def forecast_high_demand(self):
        return DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=600,
            confidence_interval_lower=500,
            confidence_interval_upper=700,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
    
    @pytest.fixture
    def forecast_low_demand(self):
        return DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=100,
            confidence_interval_lower=80,
            confidence_interval_upper=120,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
    
    @pytest.fixture
    def forecast_zero_demand(self):
        return DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=0,
            confidence_interval_lower=0,
            confidence_interval_upper=10,
            confidence_level=Decimal("0.90"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.05"),
            anomalies_detected=[]
        )
    
    def test_demand_exceeds_batch_quantity(self, agent, batch, forecast_high_demand):
        """Test when demand > batch quantity"""
        action = agent.recommend_action(batch, forecast_high_demand)
        
        assert action.action_type in ["TRANSFER", "HOLD"]
        assert action.batch_id == batch.batch_id
    
    def test_batch_exceeds_demand(self, agent, batch, forecast_low_demand):
        """Test when batch quantity > demand"""
        action = agent.recommend_action(batch, forecast_low_demand)
        
        assert action.action_type in ["TRANSFER", "DISPOSE"]
    
    def test_zero_demand_disposal(self, agent, batch, forecast_zero_demand):
        """Test DISPOSE action when demand is zero"""
        action = agent.recommend_action(batch, forecast_zero_demand)
        
        assert action.action_type == "DISPOSE", \
            "Should recommend disposal when no demand and expiring soon"


class TestInventoryAgentCostAnalysis:
    """Test cost-benefit calculations"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    def test_expensive_drug_prefer_transfer(self):
        """Test transfer preferred for expensive drugs"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("100.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=400,
            confidence_interval_lower=300,
            confidence_interval_upper=500,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
        
        agent = InventoryOptimizationAgent()
        action = agent.recommend_action(batch, forecast)
        
        # Disposal cost (~$50K) > Transfer cost (~$2500)
        assert action.action_type == "TRANSFER", \
            "Should prefer transfer for expensive medications"
    
    def test_cost_benefit_analysis_present(self):
        """Test cost-benefit analysis included in recommendation"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=300,
            confidence_interval_lower=250,
            confidence_interval_upper=350,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
        
        agent = InventoryOptimizationAgent()
        action = agent.recommend_action(batch, forecast)
        
        assert action.cost_benefit_analysis is not None
        assert 'disposal_cost' in action.cost_benefit_analysis
        assert 'transfer_cost' in action.cost_benefit_analysis
        assert all(isinstance(v, (int, float, Decimal)) 
                  for v in action.cost_benefit_analysis.values())


class TestInventoryAgentConfidenceScoring:
    """Test confidence scoring"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    def test_high_confidence_forecast(self):
        """Test high confidence with certain forecast"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=300,
            confidence_interval_lower=280,
            confidence_interval_upper=320,
            confidence_level=Decimal("0.95"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.08"),
            anomalies_detected=[]
        )
        
        agent = InventoryOptimizationAgent()
        action = agent.recommend_action(batch, forecast)
        
        assert action.confidence_score >= 0.80
    
    def test_low_confidence_forecast(self):
        """Test low confidence with uncertain forecast"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=300,
            confidence_interval_lower=100,
            confidence_interval_upper=500,
            confidence_level=Decimal("0.50"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.40"),
            anomalies_detected=[]
        )
        
        agent = InventoryOptimizationAgent()
        action = agent.recommend_action(batch, forecast)
        
        assert action.confidence_score <= 0.70


class TestInventoryAgentOutputValidation:
    """Test recommendation output structure"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    def test_recommendation_model_compliance(self):
        """Test recommendation follows InventoryRecommendation model"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=1,
            medication_id=1,
            predicted_demand_units=300,
            confidence_interval_lower=250,
            confidence_interval_upper=350,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
        
        agent = InventoryOptimizationAgent()
        action = agent.recommend_action(batch, forecast)
        
        assert isinstance(action, InventoryRecommendation)
        assert action.batch_id == batch.batch_id
        assert action.action_type in ["TRANSFER", "DISPOSE", "HOLD"]
        assert 0 <= action.confidence_score <= 1
        assert action.cost_benefit_analysis is not None


class TestInventoryAgentErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    def test_batch_forecast_medication_mismatch(self, agent):
        """Test error when batch and forecast mismatch"""
        batch = InventoryBatch(
            batch_id=1,
            medication_id=1,
            batch_number="BATCH-001",
            quantity_units=500,
            unit_price=Decimal("10.00"),
            expiry_date=datetime.now() + timedelta(days=10),
            manufacture_date=datetime.now() - timedelta(days=20),
            facility_id=1,
            storage_location="A-1-1"
        )
        
        forecast = DemandForecast(
            forecast_id=999,
            medication_id=999,  # Different medication
            predicted_demand_units=300,
            confidence_interval_lower=250,
            confidence_interval_upper=350,
            confidence_level=Decimal("0.85"),
            model_type="PROPHET",
            model_accuracy_mape=Decimal("0.12"),
            anomalies_detected=[]
        )
        
        with pytest.raises(ValueError, match="Medication mismatch"):
            agent.recommend_action(batch, forecast)
    
    def test_invalid_batch_data(self, agent):
        """Test error with invalid batch"""
        with pytest.raises((ValueError, TypeError)):
            agent.recommend_action(None, None)


@pytest.mark.performance
class TestInventoryAgentPerformance:
    """Performance tests"""
    
    @pytest.fixture
    def agent(self):
        return InventoryOptimizationAgent()
    
    def test_batch_processing_time(self, agent, sample_batches, sample_forecasts):
        """Test batch processing completes in reasonable time"""
        import time
        
        start = time.time()
        
        for batch in sample_batches[:5]:  # Test 5 batches
            forecast = next((f for f in sample_forecasts 
                           if f.medication_id == batch.medication_id), None)
            if forecast:
                agent.recommend_action(batch, forecast)
        
        duration = time.time() - start
        
        assert duration < 2, f"Processing 5 batches took {duration}s, expected <2s"
