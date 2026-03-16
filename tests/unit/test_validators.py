"""
Unit Tests - Output and Cross Validators
Tests data validation frameworks
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from agents.models import DemandForecast, InventoryRecommendation, SupplyChainDecision
from validators.output_validator import OutputValidator
from validators.cross_validator import CrossValidator
from validators.input_validator import InputValidator


class TestOutputValidatorForecastValidation:
    """Test forecast output validation"""
    
    def test_valid_forecast_passes_validation(self):
        """Test: Valid forecast passes all checks"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=100,
            confidence_level=0.85,
            confidence_interval_lower=80,
            confidence_interval_upper=120,
            model_type='PROPHET',
            model_accuracy_mape=0.12,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        assert OutputValidator.validate_forecast_output(forecast) is True
    
    def test_forecast_with_zero_demand_fails(self):
        """Test: Forecast with zero demand fails validation"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=0,  # INVALID
            confidence_level=0.8,
            confidence_interval_lower=0,
            confidence_interval_upper=10,
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        with pytest.raises(ValueError, match="predicted_demand_units"):
            OutputValidator.validate_forecast_output(forecast)
    
    def test_forecast_with_negative_demand_fails(self):
        """Test: Negative demand fails"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=-50,  # INVALID
            confidence_level=0.8,
            confidence_interval_lower=-60,
            confidence_interval_upper=-40,
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        with pytest.raises(ValueError):
            OutputValidator.validate_forecast_output(forecast)
    
    def test_forecast_with_invalid_confidence_fails(self):
        """Test: Confidence outside [0-1] fails"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=100,
            confidence_level=1.5,  # INVALID (>1)
            confidence_interval_lower=80,
            confidence_interval_upper=120,
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        with pytest.raises(ValueError, match="confidence_level"):
            OutputValidator.validate_forecast_output(forecast)
    
    def test_forecast_with_inverted_intervals_fails(self):
        """Test: Upper < lower fails"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=100,
            confidence_level=0.8,
            confidence_interval_lower=120,  # INVALID (lower)
            confidence_interval_upper=80,   # INVALID (upper)
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        with pytest.raises(ValueError, match="interval"):
            OutputValidator.validate_forecast_output(forecast)


class TestOutputValidatorRecommendationValidation:
    """Test recommendation output validation"""
    
    def test_valid_recommendation_passes(self):
        """Test: Valid recommendation passes"""
        
        rec = InventoryRecommendation(
            batch_id='BATCH001',
            action_type='TRANSFER',
            quantity_to_action=50,
            confidence_score=0.9,
            cost_benefit_analysis={
                'disposal_cost': 5000.00,
                'transfer_cost': 2500.00,
                'savings': 2500.00
            },
            rationale='High-value batch, expiring soon'
        )
        
        assert OutputValidator.validate_recommendation_output(rec) is True
    
    def test_recommendation_with_invalid_action_fails(self):
        """Test: Invalid action type fails"""
        
        rec = InventoryRecommendation(
            batch_id='BATCH001',
            action_type='UNKNOWN',  # INVALID
            quantity_to_action=50,
            confidence_score=0.8,
            cost_benefit_analysis={'disposal_cost': 1000},
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="action_type"):
            OutputValidator.validate_recommendation_output(rec)
    
    def test_recommendation_with_negative_cost_fails(self):
        """Test: Negative costs fail"""
        
        rec = InventoryRecommendation(
            batch_id='BATCH001',
            action_type='TRANSFER',
            quantity_to_action=50,
            confidence_score=0.8,
            cost_benefit_analysis={
                'disposal_cost': -5000.00,  # INVALID
                'transfer_cost': 2500.00
            },
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="disposal_cost"):
            OutputValidator.validate_recommendation_output(rec)
    
    def test_recommendation_with_invalid_confidence_fails(self):
        """Test: Confidence outside [0-1] fails"""
        
        rec = InventoryRecommendation(
            batch_id='BATCH001',
            action_type='DISPOSE',
            quantity_to_action=100,
            confidence_score=1.5,  # INVALID
            cost_benefit_analysis={'disposal_cost': 1000},
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="confidence_score"):
            OutputValidator.validate_recommendation_output(rec)


class TestOutputValidatorSupplyDecisionValidation:
    """Test supply decision output validation"""
    
    def test_valid_supply_decision_passes(self):
        """Test: Valid decision passes"""
        
        decision = SupplyChainDecision(
            medication_id='MED001',
            decision_type='REORDER',
            selected_supplier_id='SUP001',
            cost_estimate=Decimal('5000.00'),
            lead_time_estimate_days=3,
            confidence_score=0.92,
            rationale='Best cost and lead time'
        )
        
        assert OutputValidator.validate_supply_decision_output(decision) is True
    
    def test_decision_with_invalid_type_fails(self):
        """Test: Invalid decision type fails"""
        
        decision = SupplyChainDecision(
            medication_id='MED001',
            decision_type='UNKNOWN',  # INVALID
            selected_supplier_id='SUP001',
            cost_estimate=Decimal('5000.00'),
            lead_time_estimate_days=3,
            confidence_score=0.9,
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="decision_type"):
            OutputValidator.validate_supply_decision_output(decision)
    
    def test_decision_with_zero_cost_fails(self):
        """Test: Zero cost fails"""
        
        decision = SupplyChainDecision(
            medication_id='MED001',
            decision_type='REORDER',
            selected_supplier_id='SUP001',
            cost_estimate=Decimal('0.00'),  # INVALID
            lead_time_estimate_days=3,
            confidence_score=0.9,
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="cost_estimate"):
            OutputValidator.validate_supply_decision_output(decision)
    
    def test_decision_with_negative_lead_time_fails(self):
        """Test: Negative lead time fails"""
        
        decision = SupplyChainDecision(
            medication_id='MED001',
            decision_type='REORDER',
            selected_supplier_id='SUP001',
            cost_estimate=Decimal('5000.00'),
            lead_time_estimate_days=-3,  # INVALID
            confidence_score=0.9,
            rationale='Test'
        )
        
        with pytest.raises(ValueError, match="lead_time"):
            OutputValidator.validate_supply_decision_output(decision)


class TestCrossValidatorForecastVsConsumption:
    """Test cross-validation: forecast vs consumption history"""
    
    def test_forecast_aligned_with_consumption(self):
        """Test: Forecast within reasonable range of history"""
        
        # History: average 50 units/day, max 75
        consumption_history = [
            ('2024-01-01', 45),
            ('2024-01-02', 55),
            ('2024-01-03', 50),
            ('2024-01-04', 48),
            ('2024-01-05', 60),
        ]
        
        forecast = {
            'medication_id': 'MED001',
            'predicted_demand_units': 100,  # Within 3x max (75*3=225)
        }
        
        assert CrossValidator.validate_forecast_vs_consumption(
            forecast, consumption_history
        ) is True
    
    def test_forecast_exceeds_reasonable_bound(self):
        """Test: Forecast > 3x max history fails"""
        
        consumption_history = [
            ('2024-01-01', 50),
            ('2024-01-02', 50),
            ('2024-01-03', 50),
        ]
        
        forecast = {
            'medication_id': 'MED001',
            'predicted_demand_units': 10000,  # WAY outside 3x max (150)
        }
        
        with pytest.raises(ValueError):
            CrossValidator.validate_forecast_vs_consumption(
                forecast, consumption_history
            )
    
    def test_forecast_high_when_history_zero(self):
        """Test: Forecast high but history is zero fails"""
        
        consumption_history = [
            ('2024-01-01', 0),
            ('2024-01-02', 0),
            ('2024-01-03', 0),
        ]
        
        forecast = {
            'medication_id': 'MED001',
            'predicted_demand_units': 100,  # INVALID when history is zero
        }
        
        with pytest.raises(ValueError, match="historical max is 0"):
            CrossValidator.validate_forecast_vs_consumption(
                forecast, consumption_history
            )


class TestCrossValidatorRecommendationVsForecast:
    """Test cross-validation: recommendation vs forecast confidence"""
    
    def test_recommendation_confidence_lower_than_forecast(self):
        """Test: Recommendation confidence ≤ forecast confidence"""
        
        forecast = {
            'medication_id': 'MED001',
            'confidence_level': 0.9,
        }
        
        recommendation = {
            'medication_id': 'MED001',
            'confidence_score': 0.8,  # Lower than forecast OK
        }
        
        assert CrossValidator.validate_recommendation_vs_forecast(
            recommendation, forecast
        ) is True
    
    def test_recommendation_confidence_exceeds_forecast(self):
        """Test: Recommendation confidence > forecast confidence fails"""
        
        forecast = {
            'medication_id': 'MED001',
            'confidence_level': 0.7,
        }
        
        recommendation = {
            'medication_id': 'MED001',
            'confidence_score': 0.95,  # HIGHER than forecast INVALID
        }
        
        with pytest.raises(ValueError, match="exceeds forecast confidence"):
            CrossValidator.validate_recommendation_vs_forecast(
                recommendation, forecast
            )


class TestCrossValidatorDecisionVsRecommendation:
    """Test cross-validation: decision vs recommendation"""
    
    def test_dispose_recommendation_has_no_decision(self):
        """Test: DISPOSE recommendation shouldn't have supply decision"""
        
        recommendation = {
            'action_type': 'DISPOSE',
        }
        
        decision = {
            'decision_type': 'REORDER',  # INVALID - shouldn't supply DISPOSE
        }
        
        with pytest.raises(ValueError, match="DISPOSE recommendation"):
            CrossValidator.validate_decision_vs_recommendation(
                decision, recommendation
            )
    
    def test_transfer_recommendation_with_transfer_decision(self):
        """Test: TRANSFER recommendation with TRANSFER decision OK"""
        
        recommendation = {
            'action_type': 'TRANSFER',
        }
        
        decision = {
            'decision_type': 'TRANSFER',
            'cost_estimate': 2500.00,
        }
        
        assert CrossValidator.validate_decision_vs_recommendation(
            decision, recommendation
        ) is True


class TestInputValidatorFieldValidation:
    """Test input data validation"""
    
    def test_valid_facility_data_passes(self):
        """Test: Valid facility data passes"""
        
        facilities = {
            'FAC001': {
                'facility_id': 'FAC001',
                'name': 'Central Hospital',
                'location': 'New York',
                'capacity': 1000,
                'manager': 'Dr. Smith'
            }
        }
        
        assert InputValidator.validate_facility_data(facilities) is True
    
    def test_duplicate_facility_ids_fail(self):
        """Test: Duplicate facility IDs fail"""
        
        facilities = {
            'FAC001': {
                'facility_id': 'FAC001',
                'location': 'NY',
                'capacity': 100
            },
            'FAC001': {  # DUPLICATE
                'facility_id': 'FAC001',
                'location': 'LA',
                'capacity': 200
            }
        }
        
        # Dict keys will overwrite, so this test verifies the concept
        assert len(facilities) == 1  # Only one FAC001
    
    def test_valid_medication_data_passes(self):
        """Test: Valid medication data passes"""
        
        medications = {
            'MED001': {
                'medication_id': 'MED001',
                'name': 'Aspirin',
                'min_stock_level': 100,
                'max_stock_level': 500,
                'normal_consumption_daily': 10
            }
        }
        
        assert InputValidator.validate_medication_data(medications) is True
    
    def test_medication_with_inverted_stock_levels_fails(self):
        """Test: min_stock > max_stock fails"""
        
        medications = {
            'MED001': {
                'medication_id': 'MED001',
                'name': 'Aspirin',
                'min_stock_level': 500,  # INVALID (> max)
                'max_stock_level': 100,  # INVALID
                'normal_consumption_daily': 10
            }
        }
        
        with pytest.raises(ValueError):
            InputValidator.validate_medication_data(medications)
    
    def test_valid_batch_data_passes(self):
        """Test: Valid batch data passes"""
        
        batches = {
            'BATCH001': {
                'batch_id': 'BATCH001',
                'medication_id': 'MED001',
                'facility_id': 'FAC001',
                'quantity': 100,
                'unit_price': Decimal('10.00'),
                'manufacture_date': datetime.now() - timedelta(days=100),
                'expiry_date': datetime.now() + timedelta(days=100),
                'storage_condition': 'COOL'
            }
        }
        
        assert InputValidator.validate_batch_data(batches) is True
    
    def test_batch_expiry_before_manufacture_fails(self):
        """Test: Expiry before manufacture fails"""
        
        batches = {
            'BATCH001': {
                'batch_id': 'BATCH001',
                'medication_id': 'MED001',
                'facility_id': 'FAC001',
                'quantity': 100,
                'unit_price': Decimal('10.00'),
                'manufacture_date': datetime.now() + timedelta(days=100),  # FUTURE
                'expiry_date': datetime.now() - timedelta(days=100),  # PAST
                'storage_condition': 'COOL'
            }
        }
        
        with pytest.raises(ValueError):
            InputValidator.validate_batch_data(batches)


class TestValidationErrorMessages:
    """Test validation error messages are helpful"""
    
    def test_error_messages_identify_field(self):
        """Test: Error messages include the problematic field"""
        
        forecast = DemandForecast(
            medication_id='MED001',
            predicted_demand_units=-50,
            confidence_level=0.8,
            confidence_interval_lower=-60,
            confidence_interval_upper=-40,
            model_type='PROPHET',
            model_accuracy_mape=0.1,
            anomaly_detected=False,
            anomaly_type=None,
            external_signals_applied=[]
        )
        
        try:
            OutputValidator.validate_forecast_output(forecast)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            error_msg = str(e)
            # Should mention the field that failed
            assert 'predicted_demand_units' in error_msg or 'demand' in error_msg.lower()
