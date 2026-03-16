"""
Pytest configuration and shared fixtures for all tests
Provides test data generators and common setup for all test suites
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.models import (
    DemandForecast, InventoryBatch, ConsumptionData,
    TransferRecommendation, SupplyChainDecision, 
    Supplier, ExternalSignal, FacilityInfo
)


class TestDataGenerator:
    """Generate realistic test data for all tests"""
    
    @staticmethod
    def create_sample_facilities(count: int = 4):
        """Generate sample facilities"""
        return [
            FacilityInfo(
                facility_id=i,
                facility_name=f'Hospital {chr(64+i)}',
                location=['New York', 'Boston', 'LA', 'Chicago'][i-1],
                capacity_units=10000,
                utilization_percent=Decimal("63.5"),
                address=f'{100*i} Main St',
                phone=f'555-000{i}',
                manager_name=f'Manager {i}'
            )
            for i in range(1, count+1)
        ]
    
    @staticmethod
    def create_sample_medications(count: int = 50):
        """Generate sample medications"""
        categories = ['Antibiotic', 'Painkiller', 'Vitamin', 'Antiviral']
        return [
            {
                'medication_id': i,
                'medication_name': f'Drug-{i:03d}',
                'generic_name': f'generic-drug-{i}',
                'therapeutic_category': categories[i % 4],
                'unit_type': 'tablet',
                'min_stock_level': 100,
                'max_stock_level': 1000,
                'avg_daily_consumption': Decimal(str(50 + i % 100)),
                'is_controlled_substance': i % 10 == 0,
                'storage_requirements': 'Room temperature',
                'manufacturer': f'Pharma-{i % 5}',
                'active_ingredient': f'Ingredient-{i}',
                'strength': '100mg',
                'regulatory_code': f'REG-{i:05d}'
            }
            for i in range(1, count+1)
        ]
    
    @staticmethod
    def create_sample_consumption_history(days: int = 90, medications: int = 50):
        """Generate consumption history data"""
        records = []
        for med_id in range(1, medications + 1):
            for day in range(days):
                records.append({
                    'consumption_id': len(records) + 1,
                    'medication_id': med_id,
                    'facility_id': (day % 4) + 1,
                    'date': (datetime.now() - timedelta(days=day)).date(),
                    'quantity_consumed': max(10, 50 + np.random.randint(-30, 30)),
                    'reason': 'PATIENT_USE',
                    'department': f'Dept-{med_id % 3}',
                    'patient_count': np.random.randint(10, 50),
                    'cost': Decimal(str(100 + np.random.randint(0, 500)))
                })
        
        return pd.DataFrame(records).sort_values('date').reset_index(drop=True)
    
    @staticmethod
    def create_sample_batches(count: int = 20, medications: int = 50):
        """Generate inventory batches"""
        batches = []
        for i in range(1, count + 1):
            batches.append(
                InventoryBatch(
                    batch_id=i,
                    medication_id=(i % medications) + 1,
                    batch_number=f'BATCH-{i:05d}',
                    quantity_units=np.random.randint(100, 1000),
                    unit_price=Decimal(str(round(np.random.uniform(5, 100), 2))),
                    manufacture_date=(datetime.now() - timedelta(days=30)).date(),
                    expiry_date=(datetime.now() + timedelta(days=np.random.randint(5, 365))).date(),
                    facility_id=(i % 4) + 1,
                    storage_location=f'A-{i%10}-{i%3}'
                )
            )
        return batches
    
    @staticmethod
    def create_sample_suppliers(count: int = 5):
        """Generate supplier data"""
        return [
            {
                'supplier_id': i,
                'supplier_name': f'Pharma Supplier {chr(88+i)}',
                'contact_person': f'Contact {i}',
                'email': f'supplier{i}@pharma.com',
                'phone': f'555-100{i}',
                'address': f'{i}00 Supplier Ave',
                'city': ['NYC', 'LA', 'Chicago', 'Boston', 'Seattle'][i-1],
                'country': 'USA',
                'lead_time_days': 2 + i,
                'reliability_rating': Decimal(str(0.80 + 0.03*i)),
                'payment_terms': 'Net 30',
                'min_order_quantity': 100 * i,
                'is_active': True,
                'contract_start_date': (datetime.now() - timedelta(days=365)).date(),
                'contract_end_date': (datetime.now() + timedelta(days=365)).date()
            }
            for i in range(1, count+1)
        ]
    
    @staticmethod
    def create_sample_forecasts(medications: int = 50):
        """Generate demand forecasts"""
        forecasts = []
        for med_id in range(1, medications + 1):
            forecasts.append(
                DemandForecast(
                    forecast_id=med_id,
                    medication_id=med_id,
                    predicted_demand_units=np.random.randint(100, 500),
                    confidence_interval_lower=np.random.randint(80, 200),
                    confidence_interval_upper=np.random.randint(200, 600),
                    confidence_level=Decimal(str(round(np.random.uniform(0.75, 0.95), 2))),
                    model_type='PROPHET',
                    model_accuracy_mape=Decimal(str(round(np.random.uniform(0.08, 0.20), 2))),
                    anomalies_detected=[]
                )
            )
        return forecasts
    
    @staticmethod
    def create_realistic_consumption(months: int = 12, medications: int = 150):
        """Generate realistic consumption with seasonality"""
        records = []
        days = months * 30
        
        for med_id in range(1, medications + 1):
            baseline = 50 + (med_id % 100)
            
            for day in range(days):
                # Add seasonality (weekly pattern)
                day_of_week = day % 7
                seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * day_of_week / 7)
                
                # Add random variation
                quantity = int(baseline * seasonal_factor * (0.8 + 0.4 * np.random.random()))
                
                records.append({
                    'consumption_id': len(records) + 1,
                    'medication_id': med_id,
                    'facility_id': (day % 4) + 1,
                    'date': (datetime.now() - timedelta(days=days-day)).date(),
                    'quantity_consumed': max(10, quantity),
                    'reason': 'PATIENT_USE',
                    'department': f'Dept-{med_id % 3}',
                    'patient_count': np.random.randint(10, 50),
                    'cost': Decimal(str(int(baseline * 2)))
                })
        
        return pd.DataFrame(records).sort_values('date').reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def test_data_generator():
    """Provide test data generator"""
    return TestDataGenerator()


@pytest.fixture
def sample_facilities(test_data_generator):
    """Sample facilities fixture"""
    return test_data_generator.create_sample_facilities(4)


@pytest.fixture
def sample_medications(test_data_generator):
    """Sample medications fixture"""
    return test_data_generator.create_sample_medications(50)


@pytest.fixture
def sample_consumption_history(test_data_generator):
    """90 days of consumption history"""
    return test_data_generator.create_sample_consumption_history(90, 50)


@pytest.fixture
def sample_batches(test_data_generator):
    """Sample inventory batches"""
    return test_data_generator.create_sample_batches(20, 50)


@pytest.fixture
def sample_suppliers(test_data_generator):
    """Sample suppliers"""
    return test_data_generator.create_sample_suppliers(5)


@pytest.fixture
def sample_forecasts(test_data_generator):
    """Sample demand forecasts"""
    return test_data_generator.create_sample_forecasts(50)


@pytest.fixture
def sample_dataset(test_data_generator):
    """Complete sample dataset"""
    return {
        'facilities': test_data_generator.create_sample_facilities(4),
        'medications': test_data_generator.create_sample_medications(50),
        'consumption_history': test_data_generator.create_sample_consumption_history(90, 50),
        'inventory_batches': test_data_generator.create_sample_batches(20, 50),
        'suppliers': test_data_generator.create_sample_suppliers(5)
    }


@pytest.fixture
def mock_prophet():
    """Mock Prophet model"""
    mock = Mock()
    mock.fit = Mock(return_value=None)
    mock.make_future_dataframe = Mock(return_value=pd.DataFrame({'ds': pd.date_range('2024-01-01', periods=30)}))
    mock.predict = Mock(return_value=pd.DataFrame({
        'yhat': [50+i for i in range(30)],
        'yhat_lower': [40+i for i in range(30)],
        'yhat_upper': [60+i for i in range(30)]
    }))
    return mock


@pytest.fixture
def mock_db():
    """Mock database"""
    db = Mock()
    db.query = Mock(return_value=[])
    db.insert = Mock(return_value=True)
    db.update = Mock(return_value=True)
    db.delete = Mock(return_value=True)
    return db


@pytest.fixture
def temp_db(tmp_path):
    """Temporary SQLite database for testing"""
    db_path = tmp_path / "test.db"
    return str(db_path)


# ─────────────────────────────────────────────────────────────────────────────
# PYTEST CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Add custom test reporting"""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        if hasattr(item, 'funcargs') and 'benchmark' in item.funcargs:
            # Include benchmark in report
            pass


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS FOR TESTS
# ─────────────────────────────────────────────────────────────────────────────

def assert_valid_dataframe(df: pd.DataFrame, expected_length: int = None, 
                          required_columns: list = None):
    """Assert DataFrame is valid"""
    assert isinstance(df, pd.DataFrame), "Expected pandas DataFrame"
    assert len(df) > 0, "DataFrame cannot be empty"
    
    if expected_length:
        assert len(df) == expected_length, f"Expected {expected_length} rows, got {len(df)}"
    
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        assert not missing, f"Missing columns: {missing}"


def assert_valid_forecast(forecast: DemandForecast):
    """Assert forecast output is valid"""
    assert forecast.predicted_demand_units > 0, "Demand must be positive"
    assert 0 <= forecast.confidence_level <= 1, "Confidence must be 0-1"
    assert 0 <= float(forecast.model_accuracy_mape) <= 1, "MAPE must be 0-1"
    assert forecast.model_type in ['PROPHET', 'ARIMA'], "Invalid model type"


def assert_valid_recommendation(rec: TransferRecommendation):
    """Assert recommendation is valid"""
    assert rec.action_type in ['TRANSFER', 'DISPOSE', 'HOLD'], "Invalid action type"
    assert 0 <= rec.confidence_score <= 1, "Invalid confidence score"
    assert rec.cost_benefit_analysis is not None, "Missing cost-benefit analysis"
