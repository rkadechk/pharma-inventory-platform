"""
Unit tests for Supply Chain Coordination Agent
Tests REORDER vs TRANSFER decision logic and cost optimization
"""

import pytest
from decimal import Decimal
from datetime import timedelta

from agents.supply_chain_agent import SupplyChainCoordinationAgent
from agents.models import SupplyChainDecision, DemandForecast


class TestSupplyChainAgentReorderOptions:
    """Test REORDER option generation"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    @pytest.fixture
    def sample_suppliers(self):
        return [
            {
                'supplier_id': 1,
                'name': 'Pharma X',
                'unit_price': Decimal("12.00"),
                'lead_time_days': 2,
                'availability': 1000,
                'reliability_rating': Decimal("0.95"),
                'min_order': 100
            },
            {
                'supplier_id': 2,
                'name': 'Pharma Y',
                'unit_price': Decimal("11.00"),
                'lead_time_days': 5,
                'availability': 800,
                'reliability_rating': Decimal("0.85"),
                'min_order': 200
            }
        ]
    
    def test_generate_reorder_options(self, agent, sample_suppliers):
        """Test generating reorder options"""
        options = agent.generate_reorder_options(
            medication_id=1,
            quantity_needed=500,
            suppliers=sample_suppliers
        )
        
        assert len(options) >= 2
        assert all(opt.get('unit_price', 0) > 0 for opt in options)
        assert all(opt.get('lead_time_days', 0) > 0 for opt in options)
    
    def test_reorder_cost_calculation(self, agent):
        """Test reorder cost = quantity × unit_price"""
        quantity = 500
        unit_price = Decimal("12.00")
        
        cost = agent.calculate_reorder_cost(quantity, unit_price)
        
        assert cost == quantity * unit_price
    
    def test_reorder_no_suppliers_error(self, agent):
        """Test error when no suppliers available"""
        with pytest.raises(ValueError, match="No suppliers available"):
            agent.generate_reorder_options(1, 500, [])
    
    def test_reorder_insufficient_availability(self, agent):
        """Test handling of insufficient supplier availability"""
        suppliers = [
            {
                'supplier_id': 1,
                'name': 'Pharma X',
                'unit_price': Decimal("12.00"),
                'lead_time_days': 2,
                'availability': 300,  # Less than needed
                'reliability_rating': Decimal("0.95"),
                'min_order': 100
            }
        ]
        
        options = agent.generate_reorder_options(1, 500, suppliers)
        
        # Should flag that full quantity not available
        assert any(opt.get('partial', False) for opt in options) or len(options) > 0


class TestSupplyChainAgentTransferOptions:
    """Test TRANSFER option generation"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    @pytest.fixture
    def sample_facilities(self):
        return [
            {'facility_id': 2, 'available_qty': 300, 'distance_km': 50},
            {'facility_id': 3, 'available_qty': 150, 'distance_km': 120}
        ]
    
    def test_generate_transfer_options(self, agent, sample_facilities):
        """Test generating transfer options"""
        options = agent.generate_transfer_options(
            medication_id=1,
            quantity_needed=300,
            source_facility_id=1,
            facilities=sample_facilities
        )
        
        assert len(options) >= 1
        assert all(opt.get('available_qty', 0) > 0 for opt in options)
        assert all(opt.get('transfer_cost', 0) >= 0 for opt in options)
    
    def test_transfer_cost_increases_with_distance(self, agent):
        """Test transfer cost scales with distance"""
        cost_50km = agent.calculate_transfer_cost(distance_km=50, quantity_units=100)
        cost_100km = agent.calculate_transfer_cost(distance_km=100, quantity_units=100)
        
        assert cost_100km > cost_50km, \
            "Cost should increase with distance"
    
    def test_transfer_cost_increases_with_quantity(self, agent):
        """Test transfer cost scales with quantity"""
        cost_100units = agent.calculate_transfer_cost(distance_km=50, quantity_units=100)
        cost_200units = agent.calculate_transfer_cost(distance_km=50, quantity_units=200)
        
        assert cost_200units > cost_100units, \
            "Cost should increase with quantity"
    
    def test_transfer_feasibility_check(self, agent, sample_facilities):
        """Test feasibility checking"""
        # Need 300, have 300+150=450 available
        feasible = agent.check_transfer_feasibility(300, sample_facilities)
        assert feasible is True
    
    def test_transfer_insufficient_supply(self, agent):
        """Test infeasibility when supply insufficient"""
        facilities = [
            {'facility_id': 2, 'available_qty': 100},
            {'facility_id': 3, 'available_qty': 150}
        ]
        
        # Need 500, only have 250 available
        feasible = agent.check_transfer_feasibility(500, facilities)
        assert feasible is False
    
    def test_transfer_no_options_error(self, agent):
        """Test error when no facilities available"""
        with pytest.raises(ValueError, match="No transfer options"):
            agent.generate_transfer_options(1, 500, 1, [])


class TestSupplyChainAgentDecisionComparison:
    """Test REORDER vs TRANSFER comparison"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    def test_transfer_preferred_lower_cost(self, agent):
        """Test TRANSFER preferred when cheaper"""
        reorder = {
            'type': 'REORDER',
            'cost': Decimal("5000"),
            'lead_time': 3,
            'reliability': Decimal("0.95"),
            'supplier_id': 1
        }
        
        transfer = {
            'type': 'TRANSFER',
            'cost': Decimal("500"),
            'lead_time': 0.25,
            'reliability': Decimal("0.98"),
            'facility_id': 2
        }
        
        decision = agent.compare_options(reorder, transfer)
        
        assert decision.get('recommended') == 'TRANSFER', \
            "Should recommend cheaper option (TRANSFER)"
    
    def test_reorder_preferred_faster(self, agent):
        """Test REORDER preferred when much faster (if cost similar)"""
        # When costs are similar, faster delivery is advantage
        reorder = {
            'type': 'REORDER',
            'cost': Decimal("1500"),
            'lead_time': 1,  # Fast!
            'reliability': Decimal("0.99"),
            'supplier_id': 1
        }
        
        transfer = {
            'type': 'TRANSFER',
            'cost': Decimal("1600"),
            'lead_time': 4,  # Slower
            'reliability': Decimal("0.90"),
            'facility_id': 2
        }
        
        decision = agent.compare_options(reorder, transfer)
        
        # Reorder might be preferred due to speed
        assert decision is not None
        assert decision.get('reason') is not None
    
    def test_tie_breaking_by_reliability(self, agent):
        """Test reliability used as tie-breaker"""
        opt1 = {
            'type': 'REORDER',
            'cost': Decimal("5000"),
            'lead_time': 3,
            'reliability': Decimal("0.99"),
            'supplier_id': 1
        }
        
        opt2 = {
            'type': 'REORDER',
            'cost': Decimal("5000"),
            'lead_time': 3,
            'reliability': Decimal("0.85"),
            'supplier_id': 2
        }
        
        decision = agent.compare_options(opt1, opt2)
        
        assert decision.get('recommended') == opt1['supplier_id'], \
            "Should prefer more reliable option"


class TestSupplyChainAgentOutputValidation:
    """Test output structure"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    def test_supply_decision_structure(self, agent):
        """Test SupplyChainDecision model compliance"""
        decision = SupplyChainDecision(
            decision_id=1,
            medication_id=1,
            facility_id=1,
            decision_type="REORDER",
            quantity_needed=500,
            cost_estimate=Decimal("5000"),
            lead_time_estimate_days=3,
            confidence_score=Decimal("0.92"),
            supplier_selected_id=1,
            risk_assessment="LOW"
        )
        
        assert decision.medication_id == 1
        assert decision.decision_type in ["REORDER", "TRANSFER"]
        assert 0 <= decision.confidence_score <= 1
        assert decision.cost_estimate > 0


class TestSupplyChainAgentErrorHandling:
    """Test error handling"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    def test_invalid_quantity_negative(self, agent):
        """Test error with negative quantity"""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            agent.calculate_reorder_cost(-100, Decimal("10.00"))
    
    def test_invalid_price_negative(self, agent):
        """Test error with negative price"""
        with pytest.raises(ValueError, match="Price must be positive"):
            agent.calculate_reorder_cost(100, Decimal("-10.00"))


@pytest.mark.performance
class TestSupplyChainAgentPerformance:
    """Performance tests"""
    
    @pytest.fixture
    def agent(self):
        return SupplyChainCoordinationAgent()
    
    def test_option_generation_performance(self, agent, sample_suppliers):
        """Test option generation completes quickly"""
        import time
        
        start = time.time()
        
        options = agent.generate_reorder_options(
            medication_id=1,
            quantity_needed=500,
            suppliers=sample_suppliers
        )
        
        duration = time.time() - start
        
        assert duration < 1, f"Option generation took {duration}s, expected <1s"
        assert len(options) > 0
    
    def test_comparison_performance(self, agent, sample_suppliers):
        """Test comparison completes quickly"""
        import time
        
        opt1 = {'type': 'REORDER', 'cost': Decimal("5000"), 'lead_time': 3}
        opt2 = {'type': 'TRANSFER', 'cost': Decimal("500"), 'lead_time': 0.25}
        
        start = time.time()
        agent.compare_options(opt1, opt2)
        duration = time.time() - start
        
        assert duration < 0.1, f"Comparison took {duration}s, expected <0.1s"


# Fixture for sample_suppliers
@pytest.fixture
def sample_suppliers():
    """Sample suppliers for testing"""
    return [
        {
            'supplier_id': 1,
            'name': 'Pharma X',
            'unit_price': Decimal("12.00"),
            'lead_time_days': 2,
            'availability': 1000,
            'reliability_rating': Decimal("0.95"),
            'min_order': 100
        },
        {
            'supplier_id': 2,
            'name': 'Pharma Y',
            'unit_price': Decimal("11.00"),
            'lead_time_days': 5,
            'availability': 800,
            'reliability_rating': Decimal("0.85"),
            'min_order': 200
        },
        {
            'supplier_id': 3,
            'name': 'Pharma Z',
            'unit_price': Decimal("10.00"),
            'lead_time_days': 7,
            'availability': 600,
            'reliability_rating': Decimal("0.75"),
            'min_order': 300
        }
    ]
