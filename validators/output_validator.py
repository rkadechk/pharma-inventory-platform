"""
Output Data Validation Framework
Validates all agent outputs and system results
"""

from decimal import Decimal
from typing import List, Dict, Any
from agents.models import DemandForecast, TransferRecommendation, SupplyChainDecision


class OutputValidator:
    """Validate agent outputs"""
    
    @staticmethod
    def validate_forecast_output(forecast: DemandForecast) -> bool:
        """
        Validate demand forecast output
        
        Rules:
        - predicted_demand_units > 0
        - confidence_level between 0-1
        - MAPE between 0-1
        - confidence_interval_upper >= confidence_interval_lower
        """
        
        if forecast.predicted_demand_units <= 0:
            raise ValueError(f"❌ Forecast: predicted_demand_units must be > 0, got {forecast.predicted_demand_units}")
        
        confidence = float(forecast.confidence_level)
        if not (0 <= confidence <= 1):
            raise ValueError(f"❌ Forecast: confidence_level out of range [0-1], got {confidence}")
        
        mape = float(forecast.model_accuracy_mape)
        if not (0 <= mape <= 1):
            raise ValueError(f"❌ Forecast: MAPE out of range [0-1], got {mape}")
        
        if forecast.confidence_interval_upper < forecast.confidence_interval_lower:
            raise ValueError(f"❌ Forecast: upper interval < lower interval")
        
        if forecast.model_type not in ['PROPHET', 'ARIMA']:
            raise ValueError(f"❌ Forecast: invalid model_type {forecast.model_type}")
        
        return True
    
    @staticmethod
    def validate_recommendation_output(rec: TransferRecommendation) -> bool:
        """
        Validate inventory recommendation
        
        Rules:
        - action is TRANSFER, DISPOSE, HOLD
        - costs are non-negative
        - confidence_score 0-1
        """
        
        valid_actions = ['TRANSFER', 'DISPOSE', 'HOLD', 'REORDER']
        if hasattr(rec, 'action'):
            # Get the string value if it's an enum
            action_val = rec.action.value if hasattr(rec.action, 'value') else str(rec.action)
            if action_val not in valid_actions:
                raise ValueError(f"❌ Recommendation: Invalid action {action_val}")
        
        if rec.cost_benefit_analysis is None:
            # cost_benefit_analysis is optional - don't fail if missing
            pass
        else:
            disposal_cost = rec.cost_benefit_analysis.get('disposal_cost', 0)
            transfer_cost = rec.cost_benefit_analysis.get('transfer_cost', 0)
            
            if disposal_cost < 0:
                raise ValueError(f"❌ Recommendation: Negative disposal cost {disposal_cost}")
            
            if transfer_cost < 0:
                raise ValueError(f"❌ Recommendation: Negative transfer cost {transfer_cost}")
        
        confidence = float(rec.confidence_score)
        if not (0 <= confidence <= 1):
            raise ValueError(f"❌ Recommendation: Invalid confidence_score {confidence}")
        
        return True
    
    @staticmethod
    def validate_supply_decision_output(decision: SupplyChainDecision) -> bool:
        """
        Validate supply chain decision
        
        Rules:
        - decision_type is REORDER or TRANSFER
        - cost_estimate positive
        - confidence_score 0-1
        - lead_time_estimate_days positive
        """
        
        if decision.decision_type not in ['REORDER', 'TRANSFER']:
            raise ValueError(f"❌ Supply Decision: Invalid decision_type {decision.decision_type}")
        
        if decision.cost_estimate <= 0:
            raise ValueError(f"❌ Supply Decision: Invalid cost_estimate {decision.cost_estimate}")
        
        if decision.lead_time_estimate_days < 0:
            raise ValueError(f"❌ Supply Decision: Negative lead_time")
        
        confidence = float(decision.confidence_score)
        if not (0 <= confidence <= 1):
            raise ValueError(f"❌ Supply Decision: Invalid confidence_score")
        
        return True
    
    @staticmethod
    def validate_action_plan(actions: List[Dict]) -> bool:
        """
        Validate action plan
        
        Rules:
        - Actions properly structured
        - No duplicate action IDs
        - Costs are numeric and reasonable
        """
        
        if not actions:
            raise ValueError("❌ Action Plan: Empty action plan")
        
        action_ids = set()
        
        for idx, action in enumerate(actions):
            if action.get('action_id') in action_ids:
                raise ValueError(f"❌ Action Plan: Duplicate action_id {action.get('action_id')}")
            action_ids.add(action.get('action_id'))
            
            if action.get('priority_level') not in ['HIGH', 'MEDIUM', 'LOW']:
                raise ValueError(f"❌ Action {idx}: Invalid priority_level")
            
            cost = action.get('estimated_cost', 0)
            if not isinstance(cost, (int, float, Decimal)):
                raise ValueError(f"❌ Action {idx}: Cost must be numeric")
            
            if cost < 0:
                raise ValueError(f"❌ Action {idx}: Negative estimated_cost")
        
        return True
    
    @staticmethod
    def validate_system_metrics(metrics: Dict[str, Any]) -> bool:
        """
        Validate system metrics
        
        Rules:
        - Health score 0-1
        - Counts non-negative
        - Values reasonable
        """
        
        if not metrics:
            raise ValueError("❌ Metrics: Empty metrics object")
        
        health = float(metrics.get('system_health_score', 0))
        if not (0 <= health <= 1):
            raise ValueError(f"❌ Metrics: Health score out of range [0-1]")
        
        if metrics.get('total_facilities', 0) <= 0:
            raise ValueError(f"❌ Metrics: Must have at least 1 facility")
        
        if metrics.get('waste_prevented_value', 0) < 0:
            raise ValueError(f"❌ Metrics: Waste prevented cannot be negative")
        
        mape = float(metrics.get('forecast_accuracy_mape', 0))
        if not (0 <= mape <= 1):
            raise ValueError(f"❌ Metrics: MAPE out of range")
        
        return True
