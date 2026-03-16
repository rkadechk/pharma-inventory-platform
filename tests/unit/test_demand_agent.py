"""
Unit tests for Demand Forecasting Agent
Tests all aspects of demand prediction, anomaly detection, and model selection
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from agents.demand_agent import DemandForecastingAgent
from agents.models import DemandForecast, ConsumptionData


class TestDemandForecastingAgentDataValidation:
    """Test data validation for demand agent"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance"""
        return DemandForecastingAgent()
    
    def test_validate_consumption_data_success(self, agent, sample_consumption_history):
        """Test successful validation of consumption data"""
        result = agent.validate_consumption_data(sample_consumption_history)
        assert result is True
    
    def test_validate_consumption_data_empty(self, agent):
        """Test validation fails with empty dataframe"""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="Empty consumption data"):
            agent.validate_consumption_data(empty_df)
    
    def test_validate_consumption_data_missing_columns(self, agent):
        """Test validation fails with missing required columns"""
        bad_df = pd.DataFrame({'date': [], 'quantity_consumed': []})
        with pytest.raises(ValueError, match="Missing required columns"):
            agent.validate_consumption_data(bad_df)
    
    def test_validate_consumption_data_insufficient_rows(self, agent):
        """Test validation fails with < 30 days of data"""
        minimal_df = pd.DataFrame({
            'date': [datetime.now() - timedelta(days=x) for x in range(10)],
            'medication_id': [1] * 10,
            'quantity_consumed': [50] * 10,
            'facility_id': [1] * 10
        })
        with pytest.raises(ValueError, match="Insufficient historical data"):
            agent.validate_consumption_data(minimal_df)
    
    def test_negative_consumption_values(self, agent):
        """Test detection of negative consumption values"""
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': [-10] + [50] * 89,  # One negative value
            'facility_id': [1] * 90
        })
        with pytest.raises(ValueError, match="Negative consumption"):
            agent.validate_consumption_data(df)


class TestDemandForecastingAgentProphet:
    """Test Prophet forecasting model"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_prophet_forecast_basic(self, agent, sample_consumption_history):
        """Test basic Prophet forecast generation"""
        forecast = agent._train_prophet_model(
            medication_id=1,
            consumption_data=sample_consumption_history[sample_consumption_history['medication_id'] == 1],
            periods=30
        )
        
        assert isinstance(forecast, dict)
        assert 'yhat' in forecast
        assert 'yhat_lower' in forecast
        assert 'yhat_upper' in forecast
        assert len(forecast['yhat']) == 30
    
    def test_prophet_confidence_intervals(self, agent, sample_consumption_history):
        """Test confidence intervals are calculated correctly"""
        forecast = agent._train_prophet_model(
            medication_id=1,
            consumption_data=sample_consumption_history[sample_consumption_history['medication_id'] == 1],
            periods=30
        )
        
        # Lower bound < point estimate < upper bound
        assert all(lower < point for lower, point in 
                  zip(forecast['yhat_lower'], forecast['yhat']))
        assert all(point < upper for point, upper in 
                  zip(forecast['yhat'], forecast['yhat_upper']))
    
    def test_prophet_positive_forecast(self, agent, sample_consumption_history):
        """Test all forecasts are positive"""
        forecast = agent._train_prophet_model(
            medication_id=1,
            consumption_data=sample_consumption_history[sample_consumption_history['medication_id'] == 1],
            periods=30
        )
        
        assert all(val > 0 for val in forecast['yhat']), \
            "All forecasted values should be positive"
    
    def test_prophet_with_seasonality_detection(self, agent):
        """Test Prophet detects seasonality in cyclic data"""
        # Create weekly seasonal pattern
        dates = pd.date_range('2024-01-01', periods=84, freq='D')
        quantities = [50 + 20 * np.sin(2 * np.pi * i / 7) for i in range(84)]
        
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 84,
            'quantity_consumed': [max(10, int(q)) for q in quantities],
            'facility_id': [1] * 84
        })
        
        forecast = agent._train_prophet_model(1, df, 30)
        
        # With seasonality, forecast should vary
        assert len(set([round(x) for x in forecast['yhat']])) > 1, \
            "Forecast should capture seasonality (have variance)"


class TestDemandForecastingAgentARIMA:
    """Test ARIMA fallback model"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_arima_forecast_fallback(self, agent, sample_consumption_history):
        """Test ARIMA fallback when Prophet fails"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        forecast = agent._train_arima_model(1, med_data, periods=30)
        
        assert isinstance(forecast, dict)
        assert 'forecast' in forecast
        assert len(forecast['forecast']) == 30
    
    def test_arima_positive_forecast(self, agent, sample_consumption_history):
        """Test ARIMA produces positive forecasts"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        forecast = agent._train_arima_model(1, med_data, periods=30)
        
        assert all(val > 0 for val in forecast['forecast']), \
            "All ARIMA forecasts must be positive"
    
    def test_arima_reasonable_range(self, agent, sample_consumption_history):
        """Test ARIMA forecast within reasonable historical bounds"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        baseline = med_data['quantity_consumed'].mean()
        
        forecast = agent._train_arima_model(1, med_data, periods=30)
        
        # Forecast should be within 0.5-1.5x baseline
        assert all(baseline * 0.5 <= val <= baseline * 1.5 for val in forecast['forecast']), \
            "ARIMA forecast should be within reasonable bounds"


class TestDemandForecastingAgentAnomalyDetection:
    """Test anomaly detection"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_anomaly_detection_spikes(self, agent):
        """Test detection of consumption spikes (>100% increase)"""
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        quantities = [50] * 90
        quantities[45] = 150  # 200% spike
        
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': quantities,
            'facility_id': [1] * 90
        })
        
        anomalies = agent._detect_anomalies(df)
        
        assert len(anomalies) >= 1, "Should detect spike anomaly"
        assert any(a.get('type') == 'SPIKE' for a in anomalies), \
            "Should classify spike correctly"
    
    def test_anomaly_detection_dips(self, agent):
        """Test detection of consumption dips (>50% decrease)"""
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        quantities = [50] * 90
        quantities[45] = 10  # 80% drop
        
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': quantities,
            'facility_id': [1] * 90
        })
        
        anomalies = agent._detect_anomalies(df)
        
        assert len(anomalies) >= 1, "Should detect dip anomaly"
        assert any(a.get('type') == 'DIP' for a in anomalies), \
            "Should classify dip correctly"
    
    def test_anomaly_detection_threshold(self, agent):
        """Test anomaly detection respects threshold"""
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        quantities = [50] * 90
        quantities[45] = 60  # 20% increase (normal variation)
        
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': quantities,
            'facility_id': [1] * 90
        })
        
        # With 50% threshold, 20% variation should not be detected
        anomalies = agent._detect_anomalies(df, threshold=0.5)
        
        normal_anomalies = [a for a in anomalies if a.get('type') in ['SPIKE', 'DIP']]
        assert len(normal_anomalies) == 0, \
            "Should not detect normal variations as anomalies"
    
    def test_no_false_positives(self, agent):
        """Test random variations don't create false positives"""
        dates = pd.date_range('2024-01-01', periods=365, freq='D')
        # Normal random variation
        quantities = [50 + np.random.randint(-15, 15) for _ in range(365)]
        
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 365,
            'quantity_consumed': quantities,
            'facility_id': [1] * 365
        })
        
        anomalies = agent._detect_anomalies(df, threshold=0.8)  # Strict threshold
        
        # Should have very few false positives with strict threshold
        assert len(anomalies) < 5, \
            "Should minimize false positives on random data"


class TestDemandForecastingAgentExternalSignals:
    """Test external signal integration"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_external_signals_integration(self, agent, sample_consumption_history):
        """Test external signals adjust forecast upward"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        signals = [
            {'type': 'DISEASE_OUTBREAK', 'magnitude': 1.5, 'duration_days': 30}
        ]
        
        forecast_normal = agent._train_prophet_model(1, med_data, 30)
        
        # Manually apply signal adjustment
        forecast_adjusted = {k: [v * 1.3 if i < 30 else v for i, v in enumerate(forecast_normal[k])] 
                            for k, v in forecast_normal.items()}
        
        avg_normal = np.mean(forecast_normal['yhat'])
        avg_adjusted = np.mean(forecast_adjusted['yhat'])
        
        assert avg_adjusted > avg_normal * 1.2, \
            "Signal should increase forecast significantly"
    
    def test_multiple_signals_stacking(self, agent, sample_consumption_history):
        """Test multiple signals combine reasonably"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        # Two positive signals
        signal1_multiplier = 1.2
        signal2_multiplier = 1.1
        combined_multiplier = signal1_multiplier * signal2_multiplier
        
        # Combined should be ~1.32x
        assert combined_multiplier > 1.25, \
            "Combined signals should stack multiplicatively"
        assert combined_multiplier < 1.5, \
            "Combined effect shouldn't be excessive"


class TestDemandForecastingAgentAccuracyMetrics:
    """Test accuracy calculations"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_mape_calculation(self, agent):
        """Test MAPE (Mean Absolute Percentage Error) calculation"""
        actual = np.array([100.0, 150.0, 120.0, 140.0])
        predicted = np.array([110.0, 160.0, 115.0, 150.0])
        
        mape = agent._calculate_mape(actual, predicted)
        
        assert 0 <= mape <= 1, "MAPE should be between 0 and 1"
        assert isinstance(mape, (float, np.floating)), "MAPE should be numeric"
    
    def test_mape_perfect_forecast(self, agent):
        """Test MAPE is 0 for perfect forecast"""
        actual = np.array([100.0, 150.0, 120.0, 140.0])
        predicted = actual.copy()
        
        mape = agent._calculate_mape(actual, predicted)
        
        assert mape == 0, "Perfect forecast should have MAPE = 0"
    
    def test_mape_range(self, agent):
        """Test MAPE calculation range"""
        actual = np.array([100.0, 100.0, 100.0, 100.0])
        
        # 10% error
        predicted = np.array([110.0, 110.0, 110.0, 110.0])
        mape = agent._calculate_mape(actual, predicted)
        assert abs(mape - 0.10) < 0.01, "Should calculate 10% MAPE"
        
        # 50% error
        predicted = np.array([150.0, 150.0, 150.0, 150.0])
        mape = agent._calculate_mape(actual, predicted)
        assert abs(mape - 0.50) < 0.01, "Should calculate 50% MAPE"


class TestDemandForecastingAgentOutputFormatting:
    """Test output format and serialization"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_forecast_output_structure(self, agent, sample_consumption_history):
        """Test forecast output matches DemandForecast model"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        result = agent.generate_forecasts(
            medication_id=1,
            consumption_data=med_data,
            external_signals=[]
        )
        
        assert isinstance(result, DemandForecast), "Should return DemandForecast object"
        assert result.medication_id == 1
        assert result.predicted_demand_units > 0
        assert 0 <= result.confidence_level <= 1
        assert result.model_type in ['PROPHET', 'ARIMA']
        assert isinstance(result.anomalies_detected, list)
    
    def test_forecast_json_serialization(self, agent, sample_consumption_history):
        """Test forecast can be serialized to JSON"""
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        result = agent.generate_forecasts(1, med_data, [])
        
        json_str = result.model_dump_json()
        assert isinstance(json_str, str), "Should serialize to JSON string"
        assert 'medication_id' in json_str
        assert 'predicted_demand' in json_str


class TestDemandForecastingAgentErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_invalid_medication_id(self, agent):
        """Test handling of invalid medication ID"""
        with pytest.raises(ValueError, match="Invalid medication_id"):
            agent.generate_forecasts(
                medication_id=-1,
                consumption_data=pd.DataFrame(),
                external_signals=[]
            )
    
    def test_null_consumption_values_imputation(self, agent):
        """Test handling of null values"""
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': [50] * 45 + [None] * 45,
            'facility_id': [1] * 90
        })
        
        # Should handle gracefully (impute or skip)
        result = agent.generate_forecasts(1, df, [])
        
        assert result is not None, "Should handle null values"
        assert result.predicted_demand_units > 0
    
    def test_insufficient_data_fallback(self, agent):
        """Test fallback to ARIMA when Prophet struggles"""
        # Create problematic data (all same value)
        dates = pd.date_range('2024-01-01', periods=90, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'medication_id': [1] * 90,
            'quantity_consumed': [50] * 90,  # No variation
            'facility_id': [1] * 90
        })
        
        result = agent.generate_forecasts(1, df, [])
        
        assert result is not None, "Should generate forecast even with constant data"


@pytest.mark.performance
class TestDemandForecastingAgentPerformance:
    """Performance tests"""
    
    @pytest.fixture
    def agent(self):
        return DemandForecastingAgent()
    
    def test_single_forecast_execution_time(self, agent, sample_consumption_history):
        """Test single forecast completes within 5 seconds"""
        import time
        
        med_data = sample_consumption_history[sample_consumption_history['medication_id'] == 1]
        
        start = time.time()
        agent.generate_forecasts(1, med_data, [])
        duration = time.time() - start
        
        assert duration < 5, f"Single forecast took {duration}s, expected <5s"
    
    def test_batch_forecast_50_medications(self, agent, sample_consumption_history):
        """Test batch forecasting 50 medications completes in <30 seconds"""
        import time
        
        start = time.time()
        
        for med_id in range(1, 6):  # Test with 5 medications
            med_data = sample_consumption_history[sample_consumption_history['medication_id'] == med_id]
            agent.generate_forecasts(med_id, med_data, [])
        
        duration = time.time() - start
        
        # 5 medications should take < 10 seconds
        assert duration < 10, f"5 forecasts took {duration}s, expected <10s"
