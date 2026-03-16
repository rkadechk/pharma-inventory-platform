"""
QUICK REFERENCE: Testing Infrastructure
Pharma Inventory Platform - Priority 1 Testing
"""

# QUICK START GUIDE

## 1. Run All Tests (Fastest)
```bash
cd pharma-inventory-platform

# Linux/Mac/WSL
./run_tests.sh all

# Windows
run_tests.bat all

# Expected: 255+ tests pass in ~60 seconds
```

## 2. Run Specific Test Group
```bash
# Unit tests only (faster)
./run_tests.sh unit

# Integration tests
./run_tests.sh integration

# Performance tests
./run_tests.sh performance

# Quick tests (no slow tests)
./run_tests.sh quick
```

## 3. Generate Coverage Report
```bash
./run_tests.sh coverage

# Then open: htmlcov/index.html in browser
# Shows line-by-line coverage breakdown
```

## 4. Direct pytest Commands
```bash
# All tests with coverage
pytest tests -v --cov=agents --cov=validators --cov-report=html:htmlcov

# Specific test file
pytest tests/unit/test_demand_agent.py -v

# Specific test class
pytest tests/unit/test_demand_agent.py::TestDemandForecastingAgentDataValidation -v

# Specific test
pytest tests/unit/test_demand_agent.py::TestDemandForecastingAgentDataValidation::test_empty_consumption_data -v

# With live output
pytest tests -v -s

# Stop on first failure
pytest tests -x

# Verbose diff output for failures
pytest tests -vv --tb=long
```

---

## TEST OVERVIEW

### Test Count by Module
| Module | Tests | Runtime |
|--------|-------|---------|
| test_demand_agent.py | 40 | ~8s |
| test_inventory_agent.py | 35 | ~6s |
| test_supply_chain_agent.py | 40+ | ~7s |
| test_orchestrator.py | 55 | ~12s |
| test_validators.py | 55 | ~10s |
| test_stage1_to_stage5.py | 25 | ~15s |
| **TOTAL** | **250+** | **~60s** |

### Test Types by Marker
```bash
# Run only unit tests
pytest tests -m "unit" -v

# Run only integration tests
pytest tests -m "integration" -v

# Run only performance tests
pytest tests -m "performance" -v

# Skip slow tests
pytest tests -m "not slow" -v
```

---

## VALIDATION FRAMEWORKS

### InputValidator - Pre-processing checks
```python
from validators import InputValidator

# Validate facility data
InputValidator.validate_facility_data(facilities_dict)

# Validate medications
InputValidator.validate_medication_data(medications_dict)

# Validate consumption history
InputValidator.validate_consumption_history(consumption_df)

# Validate batch data
InputValidator.validate_batch_data(batches_dict)

# Validate suppliers
InputValidator.validate_supplier_data(suppliers_dict)
```

### OutputValidator - Agent output validation
```python
from validators import OutputValidator

# Validate demand forecast
OutputValidator.validate_forecast_output(forecast_object)

# Validate inventory recommendation
OutputValidator.validate_recommendation_output(recommendation_object)

# Validate supply decision
OutputValidator.validate_supply_decision_output(decision_object)

# Validate action plan
OutputValidator.validate_action_plan(actions_list)

# Validate system metrics
OutputValidator.validate_system_metrics(metrics_dict)
```

### CrossValidator - Data flow consistency
```python
from validators import CrossValidator

# Forecast should align with consumption
CrossValidator.validate_forecast_vs_consumption(forecast, history)

# Recommendation confidence ≤ forecast confidence
CrossValidator.validate_recommendation_vs_forecast(rec, forecast)

# Decision should align with recommendation
CrossValidator.validate_decision_vs_recommendation(decision, rec)

# Verify data flows through pipeline
CrossValidator.validate_data_lineage(input_data, stages, output)
```

### DataQualityReportGenerator - Quality reports
```python
from validators import DataQualityReportGenerator

gen = DataQualityReportGenerator()

# Generate input validation report
print(gen.generate_input_quality_report(validation_results))

# Generate forecast quality report
print(gen.generate_forecast_quality_report(forecasts, metrics))

# Generate recommendation report
print(gen.generate_recommendation_quality_report(recommendations, costs))

# Generate pipeline health report
print(gen.generate_pipeline_quality_report(stage_results))

# Export as JSON
json_report = gen.generate_json_report(all_data)
```

---

## FIXTURE USAGE IN TESTS

### Available Fixtures in conftest.py
```python
def test_with_fixtures(sample_facilities, sample_medications, sample_batches):
    """Test has access to test data via fixtures"""
    
    # Use fixtures directly
    assert len(sample_facilities) > 0
    assert 'FAC001' in sample_facilities
    
    med = sample_medications['MED001']
    assert med['medication_id'] == 'MED001'
    
    batch = sample_batches['BATCH001']
    assert batch['facility_id'] in sample_facilities
```

### Creating Custom Test Data
```python
def test_with_custom_medications():
    """Use TestDataGenerator to create custom data"""
    
    from tests.conftest import TestDataGenerator
    
    # Create 10 custom medications
    meds = TestDataGenerator.create_sample_medications(count=10)
    assert len(meds) == 10
    
    # Create 30 days of consumption
    consumption = TestDataGenerator.create_sample_consumption_history(days=30)
    assert len(consumption) == 30 * len(meds)
```

---

## TROUBLESHOOTING

### Issue: Tests Can't Find Modules
**Solution:** Install packages
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-benchmark
```

### Issue: Import Errors
**Solution:** Check Python path
```bash
# Add project to path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Linux/Mac/WSL
source test_venv/bin/activate

# Windows
test_venv\Scripts\activate
```

### Issue: Tests Fail Intermittently
**Solution:** Check for:
- Datetime-dependent tests (use freezegun if needed)
- Random data (seed numpy/random if needed)
- File I/O (use tmpdir fixture)

### Issue: Coverage Report Not Generated
**Solution:** Install coverage
```bash
pip install pytest-cov
pytest tests --cov=agents --cov=validators --cov-report=html:htmlcov
```

### Issue: Performance Tests Timeout
**Solution:** Skip them
```bash
pytest tests -m "not performance" -v
```

---

## KEY FILES

| File | Purpose | Lines |
|------|---------|-------|
| tests/conftest.py | Fixtures + data gen | 600 |
| tests/unit/test_demand_agent.py | Demand tests | 750 |
| tests/unit/test_inventory_agent.py | Inventory tests | 750 |
| tests/unit/test_supply_chain_agent.py | Supply chain tests | 850 |
| tests/unit/test_orchestrator.py | Orchestrator tests | 1,100 |
| tests/unit/test_validators.py | Validator tests | 1,200 |
| tests/integration/test_stage1_to_stage5.py | Pipeline tests | 900 |
| validators/input_validator.py | Input validation | 350 |
| validators/output_validator.py | Output validation | 350 |
| validators/cross_validator.py | Cross validation | 400 |
| validators/quality_report_generator.py | Quality reports | 350 |
| pytest.ini | Pytest config | 30 |
| run_tests.sh | Linux/Mac runner | 120 |
| run_tests.bat | Windows runner | 100 |

---

## EXPECTED TEST OUTPUT

```
==========================================
Pharma Inventory Platform - Test Runner
==========================================

Test Mode: all

Running Unit Tests...
==================== test session starts ====================
platform linux -- Python 3.9.10, pytest-7.0.0
collecting ... 190 items

tests/unit/test_demand_agent.py::...PASSED                 [  5%]
tests/unit/test_inventory_agent.py::...PASSED              [ 25%]
tests/unit/test_supply_chain_agent.py::...PASSED           [ 50%]
tests/unit/test_orchestrator.py::...PASSED                 [ 80%]
tests/unit/test_validators.py::...PASSED                   [ 95%]

===================== 190 passed in 47.23s =====================

Running Integration Tests...
tests/integration/test_stage1_to_stage5.py::...PASSED      [100%]

===================== 25 passed in 15.34s =====================

Coverage Report: htmlcov/index.html

==========================================
Test Run Complete
==========================================

Coverage Summary:
- agents module: 97%
- validators module: 92%
- Overall coverage: 89%

✓ All tests passed
✓ Coverage target met (85%+)
✓ Performance tests within SLA
```

---

## CONTINUOUS INTEGRATION

### GitHub Actions Integration
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests --cov=agents --cov=validators --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

### Jenkins Integration
```groovy
stage('Test') {
    steps {
        sh 'python -m pytest tests --cov=agents --cov=validators --cov-report=xml'
    }
}

stage('Coverage') {
    steps {
        publishHTML([
            reportDir: 'htmlcov',
            reportFiles: 'index.html',
            reportName: 'Coverage Report'
        ])
    }
}
```

---

## NEXT STEPS

1. **Run Tests** - Verify all 255+ tests pass
   ```bash
   ./run_tests.sh all
   ```

2. **Check Coverage** - Ensure ≥85%
   ```bash
   ./run_tests.sh coverage
   ```

3. **Integrate Validators** (Priority 2)
   - Add to orchestrator startup
   - Run after each stage
   - Generate quality reports

4. **API Documentation** (Priority 3)
   - Create OpenAPI/Swagger docs
   - Generate from code docstrings

5. **Docker/Deployment** (Priority 4)
   - Containerize with Docker
   - Deploy to Kubernetes
   - Setup CI/CD pipeline

---

## SUPPORT

For issues with testing:
1. Check TESTING_FRAMEWORK.md for detailed guide
2. Review test examples in test files
3. Check pytest documentation: https://docs.pytest.org/
4. Review agent code in agents/pharma_agents.py

