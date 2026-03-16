"""
Supply Chain Coordination Agent

Optimizes medication reorders and transfers.
Decides: REORDER from supplier vs TRANSFER from other facility.
Minimizes total cost while meeting demand.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .models import (
    DemandForecast,
    Supplier,
    SupplyOption,
    SupplyChainDecision,
    RecommendationAction,
    ConfidenceLevel
)
from .inventory_agent import BaseAgent

logger = logging.getLogger(__name__)


class SupplyChainCoordinationAgent(BaseAgent):
    """
    Makes supply chain decisions: Should we REORDER from supplier or TRANSFER from another facility?
    Optimizes for cost while ensuring stock availability.
    """
    
    def __init__(self, default_lead_time_days: int = 5):
        super().__init__("Supply Chain Coordination Agent")
        self.default_lead_time_days = default_lead_time_days
        self.decisions: List[SupplyChainDecision] = []
    
    async def process(self, *args, **kwargs):
        """
        Process supply chain optimization requests.
        
        Can be called in multiple ways:
        - process(facility_id, medication_id, current_stock, demand_forecast, suppliers, facility_inventory, transfer_cost_matrix)
        - process(facility_id=str, medication_id=str, current_stock=int, ...)
        
        Returns:
            SupplyChainDecision object or None
        """
        # Support both positional and keyword arguments
        if args and len(args) >= 7:
            facility_id = args[0]
            medication_id = args[1]
            current_stock = args[2]
            demand_forecast = args[3]
            suppliers = args[4]
            facility_inventory = args[5]
            transfer_cost_matrix = args[6]
        else:
            facility_id = kwargs.get('facility_id')
            medication_id = kwargs.get('medication_id')
            current_stock = kwargs.get('current_stock')
            demand_forecast = kwargs.get('demand_forecast')
            suppliers = kwargs.get('suppliers', [])
            facility_inventory = kwargs.get('facility_inventory')
            transfer_cost_matrix = kwargs.get('transfer_cost_matrix', {})
        
        # Validate required parameters
        if facility_id is None or medication_id is None:
            self.log_error("facility_id and medication_id are required for process()")
            return None
        
        if current_stock is None or demand_forecast is None or facility_inventory is None:
            self.log_error("current_stock, demand_forecast, and facility_inventory are required for process()")
            return None
        
        # Delegate to main method
        return await self.optimize_supply(
            facility_id,
            medication_id,
            current_stock,
            demand_forecast,
            suppliers,
            facility_inventory,
            transfer_cost_matrix
        )
    
    async def optimize_supply(
        self,
        facility_id: str,
        medication_id: str,
        current_stock: int,
        demand_forecast: DemandForecast,
        suppliers: List[Supplier],
        facility_inventory: pd.DataFrame,
        transfer_cost_matrix: Dict[tuple, float]
    ) -> Optional[SupplyChainDecision]:
        """
        Decide how to fulfill supply need for a specific medication at a specific facility.
        
        Args:
            facility_id: Target facility needing stock
            medication_id: Medication ID
            current_stock: Current inventory level
            demand_forecast: Forecast for next 30 days
            suppliers: Available suppliers
            facility_inventory: DataFrame with all facility inventory
            transfer_cost_matrix: Dict mapping (from_fac, to_fac) -> cost
        
        Returns:
            SupplyChainDecision with recommendation
        """
        
        logger.debug(f"Optimizing supply for {medication_id} at {facility_id}. "
                    f"Current stock: {current_stock}, Forecast 30d: {demand_forecast.total_predicted_demand_30d}")
        
        # Step 1: Check if stock is sufficient
        forecast_demand = demand_forecast.total_predicted_demand_30d
        min_stock_threshold = forecast_demand * 0.5  # At least 2 weeks supply
        
        if current_stock >= forecast_demand:
            # Stock is sufficient, no action needed
            decision = SupplyChainDecision(
                medication_id=medication_id,
                facility_id=facility_id,
                decision_type=RecommendationAction.HOLD,
                current_stock=current_stock,
                forecasted_demand_30d=forecast_demand,
                deficit=0,
                recommended_action={
                    "action": "HOLD",
                    "reason": "Current stock sufficient for forecasted demand"
                },
                alternative_options=[],
                reason="Stock levels adequate for 30-day forecast",
                confidence_score=0.95,
                cost_estimate=0.0,
                lead_time_estimate=0.0
            )
            
            self.log_decision(
                f"Medication {medication_id} at {facility_id}: HOLD "
                f"(stocks sufficient: {current_stock} >= {forecast_demand})"
            )
            
            self.decisions.append(decision)
            return decision
        
        # Step 2: Calculate deficit
        deficit = forecast_demand - current_stock
        
        logger.info(f"Deficit identified: {deficit} units needed for {medication_id} at {facility_id}")
        
        # Step 3: Generate supply options
        supply_options = []
        
        # Option Group 1: REORDER from suppliers
        supplier_options = await self._generate_reorder_options(
            medication_id,
            deficit,
            suppliers,
            forecast_demand
        )
        supply_options.extend(supplier_options)
        
        # Option Group 2: TRANSFER from other facilities
        transfer_options = await self._generate_transfer_options(
            facility_id,
            medication_id,
            deficit,
            facility_inventory,
            transfer_cost_matrix
        )
        supply_options.extend(transfer_options)
        
        if not supply_options:
            logger.warning(f"No supply options available for {medication_id} at {facility_id}")
            return None
        
        # Step 4: Score and rank options
        scored_options = self._score_options(supply_options)
        
        # Step 5: Select best option
        best_option = scored_options[0]
        
        # Step 6: Create decision
        decision_type = RecommendationAction.REORDER if best_option['option_type'] == 'REORDER' \
            else RecommendationAction.TRANSFER
        
        decision = SupplyChainDecision(
            medication_id=medication_id,
            facility_id=facility_id,
            decision_type=decision_type,
            current_stock=current_stock,
            forecasted_demand_30d=forecast_demand,
            deficit=deficit,
            recommended_action=best_option,
            alternative_options=scored_options[1:3],  # Top alternatives
            reason=self._generate_reason(best_option, deficit),
            confidence_score=best_option['confidence_score'],
            cost_estimate=best_option['total_cost'],
            lead_time_estimate=best_option['lead_time_days'] if best_option['option_type'] == 'REORDER' 
                               else best_option['lead_time_hours'],
            risk_assessment=self._assess_risk(best_option, deficit, forecast_demand)
        )
        
        self.log_decision(
            f"Supply chain optimization for {medication_id} at {facility_id}: "
            f"{decision_type} (Option: {best_option.get('supplier_name', best_option.get('from_facility_name'))}, "
            f"Cost: ${best_option['total_cost']:.0f}, Confidence: {best_option['confidence_score']:.2f})"
        )
        
        self.decisions.append(decision)
        return decision
    
    async def _generate_reorder_options(
        self,
        medication_id: str,
        deficit: int,
        suppliers: List[Supplier],
        forecast_demand: int
    ) -> List[SupplyOption]:
        """
        Generate REORDER options from suppliers.
        """
        
        options = []
        
        # Filter suppliers that carry this medication
        relevant_suppliers = [s for s in suppliers if medication_id in s.medications_supplied]
        
        logger.debug(f"Found {len(relevant_suppliers)} suppliers for {medication_id}")
        
        for supplier in relevant_suppliers:
            # Check minimum order quantity
            reorder_quantity = max(supplier.minimum_order_quantity, int(deficit * 1.2))  # Order 20% extra
            
            # Calculate cost
            total_cost = reorder_quantity * supplier.unit_price
            
            # Reliability score (delivery on-time rate)
            reliability = supplier.reliability_score * supplier.on_time_delivery_rate
            
            # Confidence based on lead time and reliability
            # Shorter lead time = higher confidence (can get stock before demand peaks)
            lead_time_confidence = max(0.6, 1.0 - (supplier.lead_time_days / 30.0))
            confidence_score = (reliability + lead_time_confidence) / 2.0
            
            # Overall score (lower is better: cost + lead time penalty)
            # Penalize long lead times
            overall_score = total_cost + (supplier.lead_time_days * 100)
            
            option = SupplyOption(
                option_type="REORDER",
                supplier_id=supplier.supplier_id,
                supplier_name=supplier.supplier_name,
                unit_price=supplier.unit_price,
                quantity_needed=reorder_quantity,
                total_cost=total_cost,
                lead_time_days=supplier.lead_time_days,
                confidence_score=confidence_score,
                reliability_score=reliability,
                overall_score=overall_score
            )
            
            options.append(option)
            
            logger.debug(f"  REORDER option: {supplier.supplier_name} - "
                        f"{reorder_quantity} units @ ${supplier.unit_price}/unit = ${total_cost:.0f}, "
                        f"Lead time: {supplier.lead_time_days}d, Reliability: {reliability:.2%}")
        
        return options
    
    async def _generate_transfer_options(
        self,
        target_facility_id: str,
        medication_id: str,
        deficit: int,
        facility_inventory: pd.DataFrame,
        transfer_cost_matrix: Dict[tuple, float]
    ) -> List[SupplyOption]:
        """
        Generate TRANSFER options from other facilities with excess stock.
        """
        
        options = []
        
        # Find facilities with excess stock of this medication
        other_facilities = facility_inventory[
            (facility_inventory['medication_id'] == medication_id) &
            (facility_inventory['facility_id'] != target_facility_id) &
            (facility_inventory['quantity'] > 0)
        ].copy()
        
        if len(other_facilities) == 0:
            logger.debug(f"No other facilities have stock of {medication_id} for transfer")
            return options
        
        logger.debug(f"Found {len(other_facilities)} facilities with {medication_id} stock")
        
        for idx, row in other_facilities.iterrows():
            source_facility_id = row['facility_id']
            source_facility_name = row['facility_name']
            available_qty = int(row['quantity'])
            
            # Can only transfer what's available
            transfer_qty = min(int(deficit * 1.1), available_qty)  # 10% buffer
            
            # Check if source facility has enough surplus
            if transfer_qty <= 0:
                continue
            
            # Get transfer cost
            cost_key = (source_facility_id, target_facility_id)
            transfer_cost = transfer_cost_matrix.get(cost_key, 2500.0)  # Default $2500
            
            # Lead time is typically 4-24 hours (same-day or next-day)
            lead_time_hours = 4  # Assume 4-hour standard delivery
            
            # Confidence based on availability and transfer infrastructure
            availability_confidence = min(transfer_qty / deficit, 1.0)  # Can we get enough?
            infrastructure_confidence = 0.95  # Transfers are reliable
            confidence_score = (availability_confidence + infrastructure_confidence) / 2.0
            
            # Reliability of transfer (nearly 100%)
            reliability = 0.95
            
            # Overall score (lower is better)
            # Transfers typically cheaper and faster than reorders
            overall_score = transfer_cost + (lead_time_hours / 24.0 * 50)  # Small penalty for time
            
            option = SupplyOption(
                option_type="TRANSFER",
                from_facility_id=source_facility_id,
                from_facility_name=source_facility_name,
                transfer_cost=transfer_cost,
                transfer_lead_time_hours=lead_time_hours,
                quantity_needed=transfer_qty,
                total_cost=transfer_cost,
                lead_time_days=lead_time_hours / 24.0,
                confidence_score=confidence_score,
                reliability_score=reliability,
                overall_score=overall_score
            )
            
            options.append(option)
            
            logger.debug(f"  TRANSFER option: From {source_facility_name} - "
                        f"{transfer_qty} units available, Cost: ${transfer_cost:.0f}, "
                        f"Lead time: {lead_time_hours}h, Confidence: {confidence_score:.2%}")
        
        return options
    
    def _score_options(self, options: List[SupplyOption]) -> List[Dict[str, Any]]:
        """
        Score and rank options.
        Returns list of dicts sorted by overall score (lower = better).
        """
        
        # Convert to dicts for easier manipulation
        option_dicts = []
        for opt in options:
            opt_dict = {
                'option_type': opt.option_type,
                'supplier_name': opt.supplier_name,
                'from_facility_name': opt.from_facility_name,
                'quantity_needed': opt.quantity_needed,
                'total_cost': opt.total_cost,
                'lead_time_days': opt.lead_time_days,
                'lead_time_hours': opt.transfer_lead_time_hours if opt.option_type == 'TRANSFER' else None,
                'confidence_score': opt.confidence_score,
                'reliability_score': opt.reliability_score,
                'overall_score': opt.overall_score
            }
            option_dicts.append(opt_dict)
        
        # Sort by overall score (lower = better)
        option_dicts.sort(key=lambda x: x['overall_score'])
        
        return option_dicts
    
    def _generate_reason(self, option: Dict[str, Any], deficit: int) -> str:
        """
        Generate human-readable reason for recommendation.
        """
        
        if option['option_type'] == 'REORDER':
            return (f"Reorder {option['quantity_needed']} units from {option['supplier_name']}. "
                   f"Cost: ${option['total_cost']:.0f}, Lead time: {option['lead_time_days']} days. "
                   f"Will address deficit of {deficit} units.")
        
        else:  # TRANSFER
            return (f"Transfer {option['quantity_needed']} units from {option['from_facility_name']}. "
                   f"Cost: ${option['total_cost']:.0f}, Lead time: {option['lead_time_hours']:.0f} hours. "
                   f"Faster and cheaper than reorder.")
    
    def _assess_risk(
        self,
        option: Dict[str, Any],
        deficit: int,
        forecast_demand: int
    ) -> Optional[str]:
        """
        Assess risk of the supply option.
        """
        
        # Lead time risk
        if option['option_type'] == 'REORDER':
            lead_time = option['lead_time_days']
            daily_demand = forecast_demand / 30.0
            
            if lead_time > 7:
                usage_during_lead = lead_time * daily_demand
                if usage_during_lead > deficit * 0.5:
                    return "MEDIUM: Long lead time may not cover usage during wait period"
        
        else:  # TRANSFER
            if option['quantity_needed'] < deficit * 0.8:
                return "LOW-MEDIUM: Transfer quantity may not fully cover deficit, consider backup reorder"
        
        return "LOW: Supply option is reliable"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return agent metrics"""
        
        reorder_count = len([d for d in self.decisions if d.decision_type == RecommendationAction.REORDER])
        transfer_count = len([d for d in self.decisions if d.decision_type == RecommendationAction.TRANSFER])
        hold_count = len([d for d in self.decisions if d.decision_type == RecommendationAction.HOLD])
        
        total_cost = sum(d.cost_estimate for d in self.decisions)
        
        return {
            "agent_name": self.name,
            "decisions_made": self.decision_count,
            "supply_decisions_total": len(self.decisions),
            "reorder_decisions": reorder_count,
            "transfer_decisions": transfer_count,
            "hold_decisions": hold_count,
            "total_supply_cost": total_cost,
            "average_confidence": np.mean([d.confidence_score for d in self.decisions]) \
                if self.decisions else 0.0,
            "error_count": self.error_count,
            "last_decision_time": self.last_decision_time.isoformat() if self.last_decision_time else None
        }
