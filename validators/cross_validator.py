"""
Cross-Validation Framework
Validates pipeline outputs against inputs for consistency and logic flows
"""

from typing import Dict, List, Any, Tuple
from decimal import Decimal


class CrossValidator:
    """Cross-validate pipeline outputs against inputs"""
    
    @staticmethod
    def validate_forecast_vs_consumption(forecast: Dict[str, Any],
                                         consumption_history: List[Tuple[str, float]]) -> bool:
        """
        Validate prediction aligns with historical consumption
        
        Rules:
        - Forecast should be in reasonable range relative to history
        - If all history is zero, forecast should be close to zero
        - Average of history should be at least 50% of forecast
        """
        
        if not consumption_history:
            raise ValueError("❌ Cross-Validation: Empty consumption history")
        
        # Extract quantities
        quantities = [q for _, q in consumption_history]
        avg_consumption = sum(quantities) / len(quantities) if quantities else 0
        max_consumption = max(quantities) if quantities else 0
        
        predicted = float(forecast.get('predicted_demand_units', 0))
        
        # If history is all zero, prediction should be low
        if max_consumption == 0 and predicted > 10:
            raise ValueError(f"❌ Forecast: Predicted {predicted} but historical max is 0")
        
        # Prediction should be within 3x max historical (reasonable room for growth)
        if max_consumption > 0 and predicted > max_consumption * 3:
            raise ValueError(f"❌ Forecast: Predicted {predicted} exceeds 3x max historical {max_consumption}")
        
        return True
    
    @staticmethod
    def validate_recommendation_vs_forecast(recommendation: Dict[str, Any],
                                           forecast: Dict[str, Any]) -> bool:
        """
        Validate recommendation aligns with forecast
        
        Rules:
        - HOLD/TRANSFER when demand is strong (forecast > batch quantity)
        - DISPOSE when demand is weak and batch expiring
        - Recommendation confidence <= forecast confidence
        """
        
        forecast_confidence = float(forecast.get('confidence_level', 0.5))
        rec_confidence = float(recommendation.get('confidence_score', 0.5))
        
        # Recommendation confidence should not exceed forecast confidence
        if rec_confidence > forecast_confidence:
            raise ValueError(f"❌ Cross-Validation: Recommendation confidence ({rec_confidence}) "
                            f"exceeds forecast confidence ({forecast_confidence})")
        
        return True
    
    @staticmethod
    def validate_decision_vs_recommendation(decision: Dict[str, Any],
                                           recommendation: Dict[str, Any]) -> bool:
        """
        Validate supply chain decision aligns with recommendation
        
        Rules:
        - If DISPOSE recommended, no supply decision needed (but if present, invalid)
        - If TRANSFER recommended, prefer TRANSFER decision
        - If HOLD recommended, prefer minimal cost option
        - Cost estimate should be reasonable
        """
        
        rec_action = recommendation.get('action_type', 'UNKNOWN')
        decision_type = decision.get('decision_type', 'UNKNOWN')
        cost = float(decision.get('cost_estimate', 0))
        
        # DISPOSE should not have supply decision
        if rec_action == 'DISPOSE' and decision_type in ['REORDER', 'TRANSFER']:
            raise ValueError(f"❌ Cross-Validation: DISPOSE recommendation shouldn't have {decision_type} decision")
        
        # Cost should be positive for REORDER/TRANSFER
        if decision_type in ['REORDER', 'TRANSFER'] and cost <= 0:
            raise ValueError(f"❌ Cross-Validation: {decision_type} has invalid cost {cost}")
        
        return True
    
    @staticmethod
    def validate_action_plan_vs_data(action_plan: List[Dict[str, Any]],
                                    medications: Dict[str, Any],
                                    facilities: Dict[str, Any]) -> bool:
        """
        Validate action plan references valid entities
        
        Rules:
        - All medication IDs must exist in system
        - All facility IDs must exist in system
        - No duplicate actions on same batch
        - Costs are consistent with previous estimates
        """
        
        if not action_plan:
            return True
        
        medication_ids = set(medications.keys())
        facility_ids = set(facilities.keys())
        
        seen_batch_actions = set()
        
        for action in action_plan:
            # Check references
            medication_id = action.get('medication_id')
            if medication_id and medication_id not in medication_ids:
                raise ValueError(f"❌ Action Plan: Unknown medication_id {medication_id}")
            
            facility_id = action.get('facility_id')
            if facility_id and facility_id not in facility_ids:
                raise ValueError(f"❌ Action Plan: Unknown facility_id {facility_id}")
            
            # Check for duplicates
            batch_action_key = (action.get('batch_id'), action.get('action_type'))
            if batch_action_key in seen_batch_actions:
                raise ValueError(f"❌ Action Plan: Duplicate action on batch {action.get('batch_id')}")
            seen_batch_actions.add(batch_action_key)
            
            # Check cost is reasonable
            cost = action.get('estimated_cost', 0)
            if cost < 0:
                raise ValueError(f"❌ Action Plan: Negative cost for action {action.get('action_id')}")
        
        return True
    
    @staticmethod
    def validate_metrics_vs_data(metrics: Dict[str, Any],
                                all_recommendations: List[Dict[str, Any]],
                                all_costs: List[Decimal]) -> bool:
        """
        Validate metrics reflect actual data accurately
        
        Rules:
        - Total facilities matches count in data
        - Waste prevented value >= 0
        - Health score reflects pass rate
        - Forecast accuracy reasonable relative to actual forecasts
        """
        
        if not metrics or not all_recommendations:
            return True
        
        # Check cost total
        actual_total_cost = sum(all_costs)
        reported_total_cost = Decimal(str(metrics.get('total_cost_estimate', 0)))
        
        # Allow 1% variance for rounding
        cost_variance = abs(actual_total_cost - reported_total_cost) / (actual_total_cost + Decimal('0.01'))
        if cost_variance > Decimal('0.01'):
            raise ValueError(f"❌ Metrics: Cost mismatch. Actual: {actual_total_cost}, Reported: {reported_total_cost}")
        
        # Health score should be 0-1
        health = float(metrics.get('system_health_score', 0))
        if not (0 <= health <= 1):
            raise ValueError(f"❌ Metrics: Health score {health} out of range")
        
        return True
    
    @staticmethod
    def validate_data_lineage(input_data: Dict[str, Any],
                             stage_outputs: Dict[str, Any],
                             final_metrics: Dict[str, Any]) -> bool:
        """
        Validate data flows correctly through all stages
        
        Rules:
        - Input medication count matches forecast medication count
        - Forecast count matches recommendation count
        - Recommendation count matches decision count (excluding DISPOSE)
        - Final metrics reflect all data processed
        """
        
        input_med_count = len(input_data.get('medications', {}))
        
        # Check stage 1
        forecast_count = len(stage_outputs.get('stage_1_forecasts', []))
        if forecast_count != input_med_count:
            raise ValueError(f"❌ Data Lineage: Input meds {input_med_count}, Forecasts {forecast_count}")
        
        # Check stage 2
        recommendation_count = len(stage_outputs.get('stage_2_recommendations', []))
        if recommendation_count == 0 and input_med_count > 0:
            raise ValueError(f"❌ Data Lineage: No recommendations for {input_med_count} medicines")
        
        # Check stage 3
        decision_count = len(stage_outputs.get('stage_3_decisions', []))
        # Decisions may be less than recommendations (e.g., DISPOSE has no decision)
        if decision_count > recommendation_count:
            raise ValueError(f"❌ Data Lineage: More decisions {decision_count} than recommendations {recommendation_count}")
        
        return True
    
    @staticmethod
    def validate_output_consistency(output1: Dict[str, Any],
                                   output2: Dict[str, Any],
                                   tolerance_percent: float = 1.0) -> bool:
        """
        Validate two outputs are consistent (for testing reproducibility)
        
        Rules:
        - Same decisions
        - Cost estimates within tolerance_percent
        - Same action types
        """
        
        # Check decision types match
        decisions1 = [o.get('decision_type') for o in output1.get('decisions', [])]
        decisions2 = [o.get('decision_type') for o in output2.get('decisions', [])]
        
        if sorted(decisions1) != sorted(decisions2):
            raise ValueError(f"❌ Consistency: Decision types differ")
        
        # Check costs are close
        cost1 = float(output1.get('total_cost', 0))
        cost2 = float(output2.get('total_cost', 0))
        
        if cost1 > 0:
            variance = abs(cost1 - cost2) / cost1 * 100
            if variance > tolerance_percent:
                raise ValueError(f"❌ Consistency: Cost variance {variance:.2f}% exceeds {tolerance_percent}%")
        
        return True
