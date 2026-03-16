"""
Inventory Optimization Agent

Monitors medication stock levels, detects expiration risk, 
and recommends transfers to prevent waste.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from abc import ABC, abstractmethod

from .models import (
    InventoryBatch,
    TransferRecommendation,
    RecommendationAction,
    ConfidenceLevel,
    FacilityInfo,
    DemandForecast
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.decision_count = 0
        self.error_count = 0
        self.last_decision_time = None
    
    @abstractmethod
    async def process(self, *args, **kwargs):
        """Process data and make decisions"""
        pass
    
    def log_decision(self, message: str):
        """Log a decision"""
        self.decision_count += 1
        self.last_decision_time = datetime.now()
        logger.info(f"{self.name} - Decision #{self.decision_count}: {message}")
    
    def log_error(self, message: str):
        """Log an error"""
        self.error_count += 1
        logger.error(f"{self.name} - Error: {message}")


class InventoryOptimizationAgent(BaseAgent):
    """
    Monitors medication inventory and recommends:
    - TRANSFER: Move batch to facility with demand
    - DISPOSE: Safely discard expired medication
    - HOLD: Keep in current facility
    """
    
    def __init__(
        self,
        risk_window_days: int = 14,
        disposal_cost: float = 18000.0
    ):
        super().__init__("Inventory Optimization Agent")
        self.risk_window_days = risk_window_days
        self.disposal_cost = disposal_cost
        self.recommendations: List[TransferRecommendation] = []
    
    async def process(self, *args, **kwargs):
        """
        Process inventory data and generate optimization recommendations.
        
        Can be called in multiple ways:
        - process(inventory_df, demand_forecasts, facility_network, transfer_history)
        - process(inventory_df=df, demand_forecasts=dict, facility_network=dict, transfer_history=df)
        
        Returns:
            List of TransferRecommendation objects
        """
        # Support both positional and keyword arguments
        if args:
            inventory_df = args[0]
            demand_forecasts = args[1] if len(args) > 1 else kwargs.get('demand_forecasts', {})
            facility_network = args[2] if len(args) > 2 else kwargs.get('facility_network', {})
            transfer_history = args[3] if len(args) > 3 else kwargs.get('transfer_history', None)
        else:
            inventory_df = kwargs.get('inventory_df')
            demand_forecasts = kwargs.get('demand_forecasts', {})
            facility_network = kwargs.get('facility_network', {})
            transfer_history = kwargs.get('transfer_history', None)
        
        if inventory_df is None:
            self.log_error("inventory_df is required for process()")
            return []
        
        # Default to empty dataframe if not provided
        if transfer_history is None:
            transfer_history = pd.DataFrame()
        
        # Delegate to main method
        return await self.evaluate_all_batches(
            inventory_df,
            demand_forecasts,
            facility_network,
            transfer_history
        )
    
    async def evaluate_all_batches(
        self,
        inventory_df: pd.DataFrame,
        demand_forecasts: Dict[str, DemandForecast],
        facility_network: Dict[str, FacilityInfo],
        transfer_history: pd.DataFrame
    ) -> List[TransferRecommendation]:
        """
        Main entry point: Evaluate all batches for risk
        
        Args:
            inventory_df: DataFrame with current inventory
            demand_forecasts: Dict mapping medication_id -> DemandForecast
            facility_network: Dict mapping facility_id -> FacilityInfo
            transfer_history: Historical transfer data for cost calculation
        
        Returns:
            List of recommendations
        """
        
        logger.info(f"Starting inventory evaluation. Batches to evaluate: {len(inventory_df)}")
        
        self.recommendations = []
        
        # Find at-risk batches
        at_risk_batches = self._find_at_risk_batches(inventory_df)
        
        logger.info(f"Found {len(at_risk_batches)} at-risk batches (expiring within {self.risk_window_days} days)")
        
        # Evaluate each batch
        for idx, batch_row in at_risk_batches.iterrows():
            try:
                batch = InventoryBatch(
                    batch_id=batch_row['batch_id'],
                    medication_id=batch_row['medication_id'],
                    medication_name=batch_row['medication_name'],
                    facility_id=batch_row['facility_id'],
                    facility_name=batch_row['facility_name'],
                    quantity=int(batch_row['quantity']),
                    unit_of_measure=batch_row.get('unit_of_measure', 'tablets'),
                    expiry_date=pd.to_datetime(batch_row['expiry_date']),
                    storage_location=batch_row.get('storage_location', 'Unknown'),
                    storage_temperature=float(batch_row.get('storage_temperature', 22.0)),
                    last_updated=pd.to_datetime(batch_row['last_updated']),
                    supplier_batch_code=batch_row.get('supplier_batch_code', '')
                )
                
                # Evaluate this batch
                rec = await self._evaluate_batch(
                    batch,
                    demand_forecasts,
                    facility_network,
                    transfer_history
                )
                
                if rec:
                    self.recommendations.append(rec)
                    
            except Exception as e:
                self.log_error(f"Error evaluating batch {batch_row.get('batch_id', 'Unknown')}: {str(e)}")
        
        logger.info(f"Evaluation complete. Generated {len(self.recommendations)} recommendations")
        return self.recommendations
    
    async def _evaluate_batch(
        self,
        batch: InventoryBatch,
        demand_forecasts: Dict[str, DemandForecast],
        facility_network: Dict[str, FacilityInfo],
        transfer_history: pd.DataFrame
    ) -> Optional[TransferRecommendation]:
        """
        Evaluate a single batch:
        1. Check demand forecast for medication
        2. If demand exists, find best transfer option
        3. Compare transfer cost vs disposal cost
        4. Generate recommendation
        """
        
        logger.debug(f"Evaluating batch {batch.batch_id} (expiring in {batch.days_until_expiry} days)")
        
        # Step 1: Check if medication has demand
        demand_forecast = demand_forecasts.get(batch.medication_id)
        
        if not demand_forecast or demand_forecast.total_predicted_demand_30d == 0:
            # No demand forecasted → Recommend DISPOSE
            rec = TransferRecommendation(
                batch_id=batch.batch_id,
                medication_id=batch.medication_id,
                action=RecommendationAction.DISPOSE,
                reason=f"No demand forecasted for {batch.medication_name}. "
                       f"Medication expires in {batch.days_until_expiry} days.",
                disposal_cost=self.disposal_cost,
                disposal_method="FDA-approved incineration",
                confidence_score=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                cost_benefit_analysis={
                    "disposal_cost": self.disposal_cost,
                    "transfer_options": 0,
                    "recommendation": "DISPOSE",
                    "rationale": "No demand forecasted"
                }
            )
            
            self.log_decision(
                f"Batch {batch.batch_id}: DISPOSE (no demand, saving ${self.disposal_cost})"
            )
            return rec
        
        # Step 2: Find transfer options
        transfer_options = await self._find_transfer_options(
            batch,
            demand_forecast,
            facility_network,
            transfer_history
        )
        
        if not transfer_options:
            # No transfer options available → Recommend DISPOSE
            rec = TransferRecommendation(
                batch_id=batch.batch_id,
                medication_id=batch.medication_id,
                action=RecommendationAction.DISPOSE,
                reason=f"No facilities with sufficient capacity or demand available for transfer. "
                       f"Safe disposal recommended.",
                disposal_cost=self.disposal_cost,
                confidence_score=0.80,
                confidence_level=ConfidenceLevel.HIGH,
                cost_benefit_analysis={
                    "disposal_cost": self.disposal_cost,
                    "transfer_options": 0,
                    "recommendation": "DISPOSE",
                    "rationale": "No transfer options available"
                }
            )
            
            self.log_decision(
                f"Batch {batch.batch_id}: DISPOSE (no transfer options)"
            )
            return rec
        
        # Step 3: Select best transfer option (minimum cost)
        best_option = min(transfer_options, key=lambda x: x["total_cost"])
        
        transfer_cost = best_option["transfer_cost"]
        savings = self.disposal_cost - transfer_cost
        
        # Calculate confidence based on demand match and facility capacity
        demand_match_score = best_option.get("demand_match_score", 0.7)
        confidence_score = min(0.95, 0.70 + (demand_match_score * 0.25))
        
        rec = TransferRecommendation(
            batch_id=batch.batch_id,
            medication_id=batch.medication_id,
            action=RecommendationAction.TRANSFER,
            reason=f"Transfer {batch.quantity} units of {batch.medication_name} to "
                   f"{best_option['target_facility_name']}. Prevents ${self.disposal_cost} waste. "
                   f"Target facility has forecasted demand of {best_option.get('facility_forecasted_demand', 'high')} units.",
            target_facility_id=best_option["target_facility_id"],
            target_facility_name=best_option["target_facility_name"],
            transfer_cost=transfer_cost,
            transfer_lead_time_hours=best_option.get("lead_time_hours", 4),
            confidence_score=confidence_score,
            confidence_level=self._get_confidence_level(confidence_score),
            cost_benefit_analysis={
                "disposal_cost": self.disposal_cost,
                "transfer_cost": transfer_cost,
                "savings": savings,
                "savings_percentage": (savings / self.disposal_cost) * 100,
                "roi": f"{(savings / transfer_cost * 100):.1f}%" if transfer_cost > 0 else "∞",
                "target_facility": best_option["target_facility_name"],
                "demand_driver": demand_forecast.external_signals_used,
                "confidence_basis": "Demand match + facility capacity + historical transfer data"
            }
        )
        
        self.log_decision(
            f"Batch {batch.batch_id}: TRANSFER to {best_option['target_facility_name']} "
            f"(Save ${savings:.0f}, Transfer cost ${transfer_cost:.0f}, "
            f"Confidence: {confidence_score:.2f})"
        )
        
        return rec
    
    async def _find_transfer_options(
        self,
        batch: InventoryBatch,
        demand_forecast: DemandForecast,
        facility_network: Dict[str, FacilityInfo],
        transfer_history: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Find all facilities that:
        1. Have demand for this medication
        2. Have available storage capacity
        3. Can receive transfers
        4. Have acceptable lead times
        
        Returns sorted by cost (lowest first)
        """
        
        options = []
        
        # Filter candidates: facilities that can receive, have capacity, exclude source
        candidates = [
            fac for fac in facility_network.values()
            if (fac.facility_id != batch.facility_id and
                fac.can_receive_transfers and
                fac.utilization_percentage < 90)  # Don't fill beyond 90%
        ]
        
        logger.debug(f"Evaluating {len(candidates)} candidate facilities for transfer")
        
        for candidate in candidates:
            # Check if candidate has demand for this medication
            # (In real implementation, would query demand forecast for each facility)
            
            # Estimate facility-specific demand
            facility_demand = self._estimate_facility_demand(
                batch.medication_id,
                candidate.facility_id,
                demand_forecast
            )
            
            if facility_demand <= 0:
                continue  # No demand at this facility
            
            # Calculate transfer cost
            transfer_cost = self._calculate_transfer_cost(
                from_facility=batch.facility_id,
                to_facility=candidate.facility_id,
                quantity=batch.quantity,
                transfer_history=transfer_history
            )
            
            # Calculate demand match score (higher is better)
            demand_match_score = min(1.0, facility_demand / batch.quantity)
            
            option = {
                "target_facility_id": candidate.facility_id,
                "target_facility_name": candidate.facility_name,
                "transfer_cost": transfer_cost,
                "lead_time_hours": candidate.transfer_lead_time_hours,
                "facility_capacity_remaining": candidate.available_capacity,
                "facility_forecasted_demand": facility_demand,
                "demand_match_score": demand_match_score,
                "confidence_score": min(0.95, 0.70 + (demand_match_score * 0.25)),
                "total_cost": transfer_cost
            }
            
            options.append(option)
            logger.debug(f"  Candidate: {candidate.facility_name} - "
                        f"Cost: ${transfer_cost:.0f}, Demand: {facility_demand} units")
        
        # Sort by total cost
        return sorted(options, key=lambda x: x["total_cost"])
    
    def _find_at_risk_batches(self, inventory_df: pd.DataFrame) -> pd.DataFrame:
        """Find all batches expiring within risk window"""
        
        inventory_df = inventory_df.copy()
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'])
        
        today = datetime.now()
        cutoff_date = today + timedelta(days=self.risk_window_days)
        
        at_risk = inventory_df[
            (inventory_df['expiry_date'] <= cutoff_date) &
            (inventory_df['quantity'] > 0)
        ].copy()
        
        # Sort by urgency (closest expiration first)
        at_risk['days_to_expiry'] = (at_risk['expiry_date'] - today).dt.days
        at_risk = at_risk.sort_values('days_to_expiry')
        
        return at_risk
    
    def _calculate_transfer_cost(
        self,
        from_facility: str,
        to_facility: str,
        quantity: int,
        transfer_history: pd.DataFrame
    ) -> float:
        """
        Calculate transfer cost using historical data.
        Falls back to estimation if no history available.
        """
        
        # Filter transfer history between these facilities
        historical = transfer_history[
            (transfer_history['from_facility_id'] == from_facility) &
            (transfer_history['to_facility_id'] == to_facility)
        ]
        
        if len(historical) > 0:
            # Calculate average cost per unit
            avg_cost_per_unit = (
                historical['transfer_cost'].sum() / 
                historical['quantity'].sum()
            )
            return avg_cost_per_unit * quantity
        
        # Fallback: Estimate based on distance and handling
        return self._estimate_transfer_cost(from_facility, to_facility, quantity)
    
    def _estimate_transfer_cost(
        self,
        from_facility: str,
        to_facility: str,
        quantity: int
    ) -> float:
        """
        Estimate transfer cost = base + distance + handling.
        (In real implementation, would use geocoding + logistics API)
        
        Cost formula:
        - Base: $500 (carrier minimum)
        - Distance: $2/mile
        - Handling: $0.50/unit
        """
        
        base_cost = 500
        distance = self._estimate_distance(from_facility, to_facility)
        handling_cost = quantity * 0.50
        
        total = base_cost + (distance * 2) + handling_cost
        
        logger.debug(f"Estimated transfer cost {from_facility} -> {to_facility}: "
                    f"Base ${base_cost} + Distance ${distance * 2:.0f} + Handling ${handling_cost:.0f} = ${total:.0f}")
        
        return total
    
    def _estimate_facility_demand(
        self,
        medication_id: str,
        facility_id: str,
        demand_forecast: DemandForecast
    ) -> float:
        """
        Estimate demand for a medication at a specific facility.
        (In real implementation, would query facility-specific forecasts)
        """
        
        # For now, use total forecast divided by average facility count (assume ~5 facilities)
        return demand_forecast.total_predicted_demand_30d * 0.3  # Rough estimate
    
    def _estimate_distance(self, facility1: str, facility2: str) -> float:
        """
        Estimate distance between facilities in miles.
        (In real implementation, would use facility coordinates + geocoding)
        """
        
        # Mock distances
        distance_map = {
            ("HOSP-A-001", "CLINIC-C-001"): 15,
            ("CLINIC-C-001", "HOSP-A-001"): 15,
            ("HOSP-A-001", "HOSP-B-002"): 8,
            ("HOSP-B-002", "CLINIC-D-004"): 12,
        }
        
        key = (facility1, facility2)
        return distance_map.get(key, 20)  # Default 20 miles
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric confidence to level"""
        if score >= 0.90:
            return ConfidenceLevel.HIGH
        elif score >= 0.70:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return agent metrics"""
        return {
            "agent_name": self.name,
            "decisions_made": self.decision_count,
            "recommendations_generated": len(self.recommendations),
            "error_count": self.error_count,
            "last_decision_time": self.last_decision_time.isoformat() if self.last_decision_time else None,
            "total_waste_prevented_value": sum(
                r.cost_benefit_analysis.get("savings", 0) 
                for r in self.recommendations 
                if r.action == RecommendationAction.TRANSFER
            ),
            "disposal_items_identified": len([
                r for r in self.recommendations 
                if r.action == RecommendationAction.DISPOSE
            ])
        }
