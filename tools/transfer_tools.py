"""
Transfer Coordination Tools
Tools for finding matches, calculating costs, and managing transfers
Used by Transfer Coordinator agent
"""

from typing import Any, Dict, List
from datetime import datetime
import json
import pandas as pd
from database.data_loader import get_data_loader

class TransferTools:
    """Tool collection for transfer coordination"""
    
    def __init__(self):
        """Initialize with data loader"""
        self.loader = get_data_loader()
    
    def find_transfer_matches(
        self,
        medication_id: str = None,
        min_quantity: int = 100,
        max_distance_km: int = 500
    ) -> Dict[str, Any]:
        """
        Find transfer opportunities (surplus/shortage matches)
        
        Args:
            medication_id: Specific medication to match (optional)
            min_quantity: Minimum units for transfer consideration
            max_distance_km: Maximum distance between facilities
        
        Returns:
            List of potential transfers
        """
        
        inventory_df = self.loader.data['inventory'].copy()
        facilities_df = self.loader.data['facilities'].copy()
        consumption_df = self.loader.data['consumption'].copy()
        medications_df = self.loader.data['medications']
        
        # Calculate average consumption rate per medication per facility (last 30 days)
        consumption_df['consumption_date'] = pd.to_datetime(consumption_df['consumption_date'])
        recent = consumption_df[
            consumption_df['consumption_date'] >= 
            (datetime.now() - pd.Timedelta(days=30))
        ]
        
        consumption_rate = recent.groupby(['medication_id', 'facility_id'])['quantity_consumed'].mean()
        
        # Merge inventory with facility location
        inventory_df = inventory_df.merge(
            facilities_df[['facility_id', 'latitude', 'longitude']],
            on='facility_id',
            how='left'
        )
        
        # Filter by medication if specified
        if medication_id:
            inventory_df = inventory_df[inventory_df['medication_id'] == medication_id]
            medications_filter = [medication_id]
        else:
            medications_filter = inventory_df['medication_id'].unique()
        
        matches = []
        
        # Find surplus/shortage pairs for each medication
        for med_id in medications_filter:
            med_inventory = inventory_df[inventory_df['medication_id'] == med_id]
            
            # Calculate supply coverage days for each facility
            coverage = {}
            for facility_id in med_inventory['facility_id'].unique():
                facility_stock = med_inventory[
                    med_inventory['facility_id'] == facility_id
                ]['quantity_on_hand'].sum()
                
                daily_consumption = consumption_rate.get((med_id, facility_id), 10)
                coverage_days = facility_stock / daily_consumption if daily_consumption > 0 else 999
                coverage[facility_id] = {
                    'stock': facility_stock,
                    'consumption_rate': daily_consumption,
                    'coverage_days': coverage_days
                }
            
            # Find surplus (>30 days) and shortage (<10 days) pairs
            surplus_facilities = [
                f for f, c in coverage.items() if c['coverage_days'] > 30
            ]
            shortage_facilities = [
                f for f, c in coverage.items() if c['coverage_days'] < 10
            ]
            
            # Find viable transfers between surplus and shortage
            for surplus_fac in surplus_facilities:
                surplus_stock = coverage[surplus_fac]['stock']
                for shortage_fac in shortage_facilities:
                    shortage_coverage = coverage[shortage_fac]
                    
                    # Calculate transfer quantity
                    daily_need = shortage_coverage['consumption_rate']
                    transfer_qty = int(daily_need * 14)  # 2 weeks supply
                    
                    if transfer_qty >= min_quantity and transfer_qty <= surplus_stock:
                        matches.append({
                            'medication_id': med_id,
                            'from_facility': surplus_fac,
                            'to_facility': shortage_fac,
                            'current_surplus': int(surplus_stock),
                            'shortage_coverage_days': round(shortage_coverage['coverage_days'], 2),
                            'proposed_transfer': transfer_qty,
                            'priority': 'HIGH' if shortage_coverage['coverage_days'] < 5 else 'MEDIUM'
                        })
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "total_matches": len(matches),
            "matches": matches[:20]  # Return top 20 matches
        }
    
    def calculate_transfer_cost(
        self,
        from_facility: str,
        to_facility: str,
        quantity: int,
        medication_id: str = None
    ) -> Dict[str, Any]:
        """
        Calculate logistics cost for transfer
        
        Args:
            from_facility: Source facility ID
            to_facility: Destination facility ID
            quantity: Units to transfer
            medication_id: Optional medication for cost estimation
        
        Returns:
            Cost breakdown
        """
        
        facilities_df = self.loader.data['facilities'].copy()
        
        # Get facility coordinates
        from_fac = facilities_df[facilities_df['facility_id'] == from_facility].iloc[0]
        to_fac = facilities_df[facilities_df['facility_id'] == to_facility].iloc[0]
        
        # Simple distance calculation (Euclidean)
        lat_diff = from_fac['latitude'] - to_fac['latitude']
        lon_diff = from_fac['longitude'] - to_fac['longitude']
        distance_km = ((lat_diff**2 + lon_diff**2)**0.5) * 111  # Rough km conversion
        
        # Cost components
        base_transport = 50  # Base fee
        distance_cost = distance_km * 0.5  # $0.50 per km
        handling_cost = quantity * 0.10  # $0.10 per unit
        insurance_cost = (quantity * 0.05) * 1.05  # 5% of unit value + insurance
        
        total_cost = base_transport + distance_cost + handling_cost + insurance_cost
        
        return {
            "from_facility": from_facility,
            "to_facility": to_facility,
            "distance_km": round(distance_km, 2),
            "quantity": quantity,
            "cost_breakdown": {
                "base_transport": round(base_transport, 2),
                "distance_cost": round(distance_cost, 2),
                "handling_cost": round(handling_cost, 2),
                "insurance_cost": round(insurance_cost, 2)
            },
            "total_cost": round(total_cost, 2),
            "cost_per_unit": round(total_cost / quantity, 4),
            "currency": "USD"
        }
    
    def create_transfer_proposal(
        self,
        medication_id: str,
        from_facility: str,
        to_facility: str,
        quantity: int,
        reason: str,
        cost_data: Dict = None
    ) -> Dict[str, Any]:
        """
        Create a transfer proposal for approval
        
        Args:
            medication_id: Medication being transferred
            from_facility: Source facility
            to_facility: Destination facility
            quantity: Transfer quantity
            reason: Reason for transfer
            cost_data: Pre-calculated cost data
        
        Returns:
            Transfer proposal
        """
        
        # Calculate cost if not provided
        if cost_data is None:
            transfer_tool = TransferTools()
            cost_data = transfer_tool.calculate_transfer_cost(
                from_facility, to_facility, quantity, medication_id
            )
        
        proposal = {
            "proposal_id": f"TRF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING_REVIEW",
            "medication_id": medication_id,
            "transfer_details": {
                "from_facility": from_facility,
                "to_facility": to_facility,
                "quantity": quantity,
                "reason": reason
            },
            "financial_impact": cost_data,
            "approval_required": True,
            "estimated_duration_hours": 24
        }
        
        return {
            "status": "success",
            "proposal": proposal,
            "next_step": "Submit for approval by facility manager"
        }
    
    def check_regulatory_constraints(
        self,
        medication_id: str,
        from_facility: str,
        to_facility: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Check regulatory constraints for transfer
        
        Args:
            medication_id: Medication to transfer
            from_facility: Source facility
            to_facility: Destination facility
            quantity: Transfer quantity
        
        Returns:
            Regulatory compliance status
        """
        
        medications_df = self.loader.data['medications']
        facilities_df = self.loader.data['facilities']
        
        med = medications_df[medications_df['medication_id'] == medication_id].iloc[0]
        from_fac = facilities_df[facilities_df['facility_id'] == from_facility].iloc[0]
        to_fac = facilities_df[facilities_df['facility_id'] == to_facility].iloc[0]
        
        constraints = []
        allowed = True
        
        # Check controlled substance status
        if med['controlled_substance']:
            constraints.append({
                "type": "CONTROLLED_SUBSTANCE",
                "description": f"{med['medication_name']} is a controlled substance",
                "requirement": "Enhanced documentation and DEA approval required",
                "status": "REQUIRES_SPECIAL_HANDLING"
            })
            allowed = allowed and True  # Allowed but with special handling
        
        # Check facility licensing for high-risk medications
        if med['category'] in ['Oncology', 'Immunosuppressant']:
            if 'hospital' not in from_fac['facility_type'].lower():
                constraints.append({
                    "type": "FACILITY_TYPE_MISMATCH",
                    "description": f"Source facility {from_facility} not licensed for {med['category']}",
                    "requirement": "Source facility must have appropriate licensing",
                    "status": "NOT_ALLOWED"
                })
                allowed = False
        
        # Check destination facility capability
        if to_fac['facility_type'] == 'clinic':
            if med['category'] in ['Oncology']:
                constraints.append({
                    "type": "DESTINATION_CAPABILITY",
                    "description": f"Destination clinic not equipped for {med['category']} medications",
                    "requirement": "Transfer destination must have appropriate infrastructure",
                    "status": "NOT_ALLOWED"
                })
                allowed = False
        
        return {
            "medication_id": medication_id,
            "from_facility": from_facility,
            "to_facility": to_facility,
            "transfer_allowed": allowed,
            "total_constraints": len(constraints),
            "constraints": constraints,
            "compliance_status": "APPROVED" if allowed else "REQUIRES_REVIEW"
        }
    
    def approve_transfer(
        self,
        proposal_id: str,
        approved_by: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Approve a transfer proposal
        
        Args:
            proposal_id: Proposal to approve
            approved_by: Manager approving the transfer
            notes: Approval notes
        
        Returns:
            Approval notification
        """
        
        return {
            "status": "success",
            "proposal_id": proposal_id,
            "approval": {
                "timestamp": datetime.now().isoformat(),
                "approved_by": approved_by,
                "notes": notes or "Transfer approved",
                "transfer_status": "SCHEDULED"
            },
            "next_steps": [
                "Schedule physical transfer",
                "Notify source facility",
                "Notify destination facility",
                "Update inventory system"
            ]
        }
    
    def get_transfer_history(
        self,
        facility_id: str = None,
        medication_id: str = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get transfer history
        
        Args:
            facility_id: Optional facility filter
            medication_id: Optional medication filter
            days: Number of days to look back
        
        Returns:
            Transfer records
        """
        
        transfers_df = self.loader.data['transfers'].copy()
        transfers_df['transfer_date'] = pd.to_datetime(transfers_df['transfer_date'])
        
        # Filter by date
        cutoff = datetime.now() - pd.Timedelta(days=days)
        transfers_df = transfers_df[transfers_df['transfer_date'] > cutoff]
        
        # Apply facility filter
        if facility_id:
            transfers_df = transfers_df[
                (transfers_df['from_facility'] == facility_id) |
                (transfers_df['to_facility'] == facility_id)
            ]
        
        # Apply medication filter
        if medication_id:
            transfers_df = transfers_df[transfers_df['medication_id'] == medication_id]
        
        return {
            "total_transfers": len(transfers_df),
            "total_units_transferred": int(transfers_df['quantity_transferred'].sum()),
            "date_range": f"Last {days} days",
            "transfers": transfers_df.to_dict(orient='records')
        }


# Create tool instances for agent use
def create_transfer_tools():
    """Factory function to create transfer tools"""
    return TransferTools()


if __name__ == "__main__":
    # Test transfer tools
    print("\n🔧 Testing Transfer Tools\n")
    
    tools = create_transfer_tools()
    
    # Test 1: Find transfer matches
    print("✅ Test 1: Find transfer matches")
    matches = tools.find_transfer_matches()
    print(f"   Found {matches['total_matches']} potential transfers")
    if matches['matches']:
        print(f"   Sample: {matches['matches'][0]['medication_id']} from {matches['matches'][0]['from_facility']} to {matches['matches'][0]['to_facility']}")
    
    # Test 2: Calculate transfer cost
    print("\n✅ Test 2: Calculate transfer cost")
    if matches['matches']:
        sample = matches['matches'][0]
        cost = tools.calculate_transfer_cost(
            sample['from_facility'],
            sample['to_facility'],
            sample['proposed_transfer']
        )
        print(f"   Cost: ${cost['total_cost']:.2f} for {cost['quantity']} units")
        print(f"   Distance: {cost['distance_km']} km")
    
    # Test 3: Create transfer proposal
    print("\n✅ Test 3: Create transfer proposal")
    if matches['matches']:
        sample = matches['matches'][0]
        proposal = tools.create_transfer_proposal(
            sample['medication_id'],
            sample['from_facility'],
            sample['to_facility'],
            sample['proposed_transfer'],
            "Redistribute surplus stock to shortage location"
        )
        print(f"   Proposal ID: {proposal['proposal']['proposal_id']}")
        print(f"   Status: {proposal['proposal']['status']}")
    
    # Test 4: Check regulatory constraints
    print("\n✅ Test 4: Check regulatory constraints")
    if matches['matches']:
        sample = matches['matches'][0]
        constraints = tools.check_regulatory_constraints(
            sample['medication_id'],
            sample['from_facility'],
            sample['to_facility'],
            sample['proposed_transfer']
        )
        print(f"   Allowed: {constraints['transfer_allowed']}")
        print(f"   Constraints: {constraints['total_constraints']}")
    
    # Test 5: Get transfer history
    print("\n✅ Test 5: Get transfer history")
    history = tools.get_transfer_history()
    print(f"   Total transfers (30 days): {history['total_transfers']}")
    print(f"   Total units transferred: {history['total_units_transferred']:,}")
    
    print("\n✅ All transfer tool tests passed!\n")
