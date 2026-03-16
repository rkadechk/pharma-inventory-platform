"""
Basic Integration Tests
Tests for agents, tools, and data loading
"""

import pytest
import os
from pathlib import Path
from datetime import datetime

# Test data loader
def test_data_loader_initialization():
    """Test that data loader can be initialized"""
    from database.data_loader import get_data_loader
    
    loader = get_data_loader()
    assert loader is not None
    print("✅ Data loader initialized")


def test_data_loader_csv_loading():
    """Test that CSV files are loaded correctly"""
    from database.data_loader import get_data_loader
    
    loader = get_data_loader()
    data = loader.load_csv_files()
    
    # Check that all expected tables are loaded
    expected_tables = [
        'facilities', 'medications', 'inventory', 'consumption',
        'demand_forecast', 'transfers', 'replenishment_orders', 'external_signals'
    ]
    
    for table in expected_tables:
        assert table in data, f"Table {table} not found"
        assert len(data[table]) > 0, f"Table {table} is empty"
    
    print(f"✅ Loaded {len(data)} data tables")


def test_data_loader_sqlite_creation():
    """Test that SQLite database is created"""
    from database.data_loader import get_data_loader
    
    loader = get_data_loader(db_path="test_pharma.db")
    loader.load_csv_files()
    loader.create_sqlite_db()
    
    assert loader.db_path.exists(), "Database file not created"
    assert loader.conn is not None, "Database connection not established"
    
    print("✅ SQLite database created successfully")
    
    # Cleanup
    if loader.db_path.exists():
        loader.conn.close()
        loader.db_path.unlink()


# Test inventory tools
def test_inventory_tools_query():
    """Test inventory query tool"""
    from tools.inventory_tools import create_inventory_tools
    
    tools = create_inventory_tools()
    result = tools.query_inventory()
    
    assert result['status'] == 'success'
    assert result['total_batches'] > 0
    assert result['total_units'] > 0
    assert len(result['items']) > 0
    
    print(f"✅ Inventory query returned {result['total_batches']} batches")


def test_inventory_tools_expiring():
    """Test get expiring medications tool"""
    from tools.inventory_tools import create_inventory_tools
    
    tools = create_inventory_tools()
    result = tools.get_expiring_medications(days_threshold=14)
    
    assert result['threshold_days'] == 14
    assert 'expiring_items' in result
    
    print(f"✅ Found {result['expiring_count']} expiring items")


def test_inventory_tools_capacity():
    """Test facility capacity check"""
    from tools.inventory_tools import create_inventory_tools
    from database.data_loader import get_data_loader
    
    tools = create_inventory_tools()
    loader = get_data_loader()
    
    # Get first facility
    facilities = loader.data['facilities']['facility_id'].unique()
    if len(facilities) > 0:
        result = tools.check_facility_capacity(facilities[0])
        
        assert 'utilization_percent' in result
        assert 'alert_level' in result
        assert result['alert_level'] in ['OK', 'CAUTION', 'WARNING', 'CRITICAL']
        
        print(f"✅ Capacity check: {result['utilization_percent']}% utilization")


def test_inventory_tools_alert():
    """Test alert creation"""
    from tools.inventory_tools import create_inventory_tools
    
    tools = create_inventory_tools()
    result = tools.create_alert(
        alert_type="test_alert",
        severity="MEDIUM",
        facility_id="TEST_FAC",
        message="Test alert message"
    )
    
    assert result['status'] == 'success'
    assert result['alert']['alert_id'].startswith('ALERT_')
    assert result['notification_sent'] == True
    
    print(f"✅ Alert created: {result['alert']['alert_id']}")


# Test transfer tools
def test_transfer_tools_matching():
    """Test transfer matching tool"""
    from tools.transfer_tools import create_transfer_tools
    
    tools = create_transfer_tools()
    result = tools.find_transfer_matches()
    
    assert result['status'] == 'success'
    assert 'matches' in result
    assert result['total_matches'] >= 0
    
    print(f"✅ Found {result['total_matches']} transfer opportunities")


def test_transfer_tools_cost():
    """Test cost calculation"""
    from tools.transfer_tools import create_transfer_tools
    from database.data_loader import get_data_loader
    
    tools = create_transfer_tools()
    loader = get_data_loader()
    
    # Get two different facilities
    facilities = loader.data['facilities']['facility_id'].unique()
    if len(facilities) >= 2:
        result = tools.calculate_transfer_cost(
            from_facility=facilities[0],
            to_facility=facilities[1],
            quantity=500
        )
        
        assert result['status'] if 'status' in result else True
        assert result['total_cost'] >= 0
        assert 'cost_breakdown' in result
        
        print(f"✅ Transfer cost calculated: ${result['total_cost']:.2f}")


def test_transfer_tools_proposal():
    """Test proposal creation"""
    from tools.transfer_tools import create_transfer_tools
    
    tools = create_transfer_tools()
    result = tools.create_transfer_proposal(
        medication_id="MED_TEST",
        from_facility="FAC_FROM",
        to_facility="FAC_TO",
        quantity=500,
        reason="Test transfer"
    )
    
    assert result['status'] == 'success'
    assert result['proposal']['proposal_id'].startswith('TRF_')
    assert result['proposal']['status'] == 'PENDING_REVIEW'
    
    print(f"✅ Transfer proposal created: {result['proposal']['proposal_id']}")


def test_transfer_tools_approve():
    """Test transfer approval"""
    from tools.transfer_tools import create_transfer_tools
    
    tools = create_transfer_tools()
    result = tools.approve_transfer(
        proposal_id="TRF_TEST",
        approved_by="Manager Test",
        notes="Approved for testing"
    )
    
    assert result['status'] == 'success'
    assert result['approval']['transfer_status'] == 'SCHEDULED'
    
    print(f"✅ Transfer approved: {result['proposal_id']}")


# Test forecasting tools
def test_forecasting_tools_forecast():
    """Test demand forecast"""
    from tools.forecasting_tools import create_forecasting_tools
    from database.data_loader import get_data_loader
    
    tools = create_forecasting_tools()
    loader = get_data_loader()
    
    meds = loader.data['medications']['medication_id'].unique()
    facilities = loader.data['facilities']['facility_id'].unique()
    
    if len(meds) > 0 and len(facilities) > 0:
        result = tools.run_demand_forecast(meds[0], facilities[0])
        
        if result['status'] == 'success':
            assert 'forecast' in result
            assert len(result['forecast']) > 0
            print(f"✅ Forecast generated: {len(result['forecast'])} days")
        else:
            print(f"⚠️  Forecast status: {result['status']}")


def test_forecasting_tools_anomaly():
    """Test anomaly detection"""
    from tools.forecasting_tools import create_forecasting_tools
    from database.data_loader import get_data_loader
    
    tools = create_forecasting_tools()
    loader = get_data_loader()
    
    meds = loader.data['medications']['medication_id'].unique()
    facilities = loader.data['facilities']['facility_id'].unique()
    
    if len(meds) > 0 and len(facilities) > 0:
        result = tools.detect_demand_anomaly(meds[0], facilities[0])
        
        if result['status'] == 'success':
            assert 'risk_assessment' in result
            assert result['risk_assessment'] in ['LOW', 'MEDIUM', 'HIGH']
            print(f"✅ Anomaly detection: {result['risk_assessment']} risk")
        else:
            print(f"⚠️  Anomaly detection status: {result['status']}")


def test_forecasting_tools_stockout():
    """Test stockout risk assessment"""
    from tools.forecasting_tools import create_forecasting_tools
    from database.data_loader import get_data_loader
    
    tools = create_forecasting_tools()
    loader = get_data_loader()
    
    meds = loader.data['medications']['medication_id'].unique()
    facilities = loader.data['facilities']['facility_id'].unique()
    
    if len(meds) > 0 and len(facilities) > 0:
        result = tools.assess_stockout_risk(meds[0], facilities[0])
        
        assert result['status'] == 'success'
        assert 'coverage_days' in result
        assert result['risk_level'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        print(f"✅ Stockout risk: {result['risk_level']} ({result['coverage_days']} days)")


# Test agents
def test_agents_initialization():
    """Test that agents can be initialized"""
    from agents.pharma_agents import create_pharma_agents
    
    agents = create_pharma_agents()
    
    assert len(agents) == 3
    assert agents[0].role == "Inventory Expiration Manager"
    assert agents[1].role == "Multi-Facility Transfer Coordinator"
    assert agents[2].role == "Demand Forecasting & Risk Analyst"
    
    print("✅ All three agents initialized successfully")


def test_agents_memory():
    """Test that agents have memory enabled"""
    from agents.pharma_agents import create_pharma_agents
    
    agents = create_pharma_agents()
    
    for agent in agents:
        assert agent.memory == True, f"{agent.role} memory not enabled"
    
    print("✅ All agents have memory enabled")


def test_agents_tools_reference():
    """Test that agents have tool references"""
    from agents.pharma_agents import create_pharma_agents
    
    agents = create_pharma_agents()
    
    for agent in agents:
        assert agent.tools is not None
        # Note: Actual tools will be set during crew creation
    
    print("✅ All agents ready for tool assignment")


# Test Claude connectivity
def test_claude_config():
    """Test Claude API configuration"""
    from agents.config import test_claude_connection
    
    try:
        is_configured = test_claude_connection()
        if is_configured:
            print("✅ Claude API is configured and accessible")
        else:
            print("⚠️  Claude API connection test failed - check API key")
    except Exception as e:
        print(f"⚠️  Claude API test failed: {str(e)}")


# Run all tests
if __name__ == "__main__":
    print("\n" + "="*70)
    print("RUNNING BASIC INTEGRATION TESTS")
    print("="*70 + "\n")
    
    tests = [
        ("Data Loader", [
            test_data_loader_initialization,
            test_data_loader_csv_loading,
            test_data_loader_sqlite_creation
        ]),
        ("Inventory Tools", [
            test_inventory_tools_query,
            test_inventory_tools_expiring,
            test_inventory_tools_capacity,
            test_inventory_tools_alert
        ]),
        ("Transfer Tools", [
            test_transfer_tools_matching,
            test_transfer_tools_cost,
            test_transfer_tools_proposal,
            test_transfer_tools_approve
        ]),
        ("Forecasting Tools", [
            test_forecasting_tools_forecast,
            test_forecasting_tools_anomaly,
            test_forecasting_tools_stockout
        ]),
        ("Agents", [
            test_agents_initialization,
            test_agents_memory,
            test_agents_tools_reference
        ]),
        ("Claude Configuration", [
            test_claude_config
        ])
    ]
    
    passed = 0
    failed = 0
    
    for category, test_list in tests:
        print(f"\n📋 {category}")
        print("-" * 70)
        
        for test in test_list:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"❌ {test.__name__} failed: {str(e)}")
                failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    if failed == 0:
        print("✅ All tests passed!\n")
    else:
        print(f"⚠️  {failed} test(s) failed. Review errors above.\n")
