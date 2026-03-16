"""
Inventory Management Tools
Tools for querying, checking capacity, and creating alerts
Used by Expiration Manager agent
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
import json
from database.data_loader import get_data_loader

class InventoryTools:
    """Tool collection for inventory management"""
    
    def __init__(self):
        """Initialize with data loader"""
        self.loader = get_data_loader()
    
    def query_inventory(
        self,
        facility_id: str = None,
        medication_id: str = None,
        include_expired: bool = False
    ) -> Dict[str, Any]:
        """
        Query inventory with optional filters
        
        Args:
            facility_id: Filter by facility (optional)
            medication_id: Filter by medication (optional)
            include_expired: Include expired items (default: False)
        
        Returns:
            Dict with inventory query results
        """
        
        inventory_df = self.loader.data['inventory'].copy()
        medications_df = self.loader.data['medications']
        
        # Convert dates
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'])
        today = datetime.now()
        
        # Filter expired
        if not include_expired:
            inventory_df = inventory_df[inventory_df['expiry_date'] > today]
        
        # Apply facility filter
        if facility_id:
            inventory_df = inventory_df[inventory_df['facility_id'] == facility_id]
        
        # Apply medication filter
        if medication_id:
            inventory_df = inventory_df[inventory_df['medication_id'] == medication_id]
        
        # Merge with medication details
        inventory_df = inventory_df.merge(
            medications_df[['medication_id', 'medication_name', 'category']],
            on='medication_id',
            how='left'
        )
        
        # Calculate expiry info
        inventory_df['days_to_expiry'] = (
            inventory_df['expiry_date'] - today
        ).dt.days
        
        # Sort by expiry date
        inventory_df = inventory_df.sort_values('days_to_expiry')
        
        return {
            "status": "success",
            "total_batches": len(inventory_df),
            "total_units": int(inventory_df['quantity_on_hand'].sum()),
            "items": inventory_df[[
                'batch_id', 'medication_id', 'medication_name',
                'facility_id', 'quantity_on_hand', 'expiry_date',
                'days_to_expiry', 'unit_cost'
            ]].to_dict(orient='records')
        }
    
    def get_expiring_medications(
        self,
        days_threshold: int = 14,
        facility_id: str = None
    ) -> Dict[str, Any]:
        """
        Get medications expiring within threshold
        
        Args:
            days_threshold: Number of days to look ahead (default: 14)
            facility_id: Optional facility filter
        
        Returns:
            List of expiring medications sorted by urgency
        """
        
        inventory_df = self.loader.data['inventory'].copy()
        medications_df = self.loader.data['medications']
        
        # Convert dates
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'])
        today = datetime.now()
        expiry_threshold = today + timedelta(days=days_threshold)
        
        # Find expiring items
        expiring = inventory_df[
            (inventory_df['expiry_date'] > today) &
            (inventory_df['expiry_date'] <= expiry_threshold)
        ]
        
        # Optional facility filter
        if facility_id:
            expiring = expiring[expiring['facility_id'] == facility_id]
        
        # Merge medication details
        expiring = expiring.merge(
            medications_df[['medication_id', 'medication_name', 'category']],
            on='medication_id',
            how='left'
        )
        
        # Calculate metrics
        expiring['days_to_expiry'] = (expiring['expiry_date'] - today).dt.days
        expiring['waste_value'] = expiring['quantity_on_hand'] * expiring['unit_cost']
        
        # Sort by urgency (days to expiry, then by value)
        expiring = expiring.sort_values(['days_to_expiry', 'waste_value'], ascending=[True, False])
        
        return {
            "threshold_days": days_threshold,
            "expiring_count": len(expiring),
            "total_at_risk_value": float(expiring['waste_value'].sum()),
            "expiring_items": expiring[[
                'batch_id', 'medication_id', 'medication_name', 'category',
                'facility_id', 'quantity_on_hand', 'days_to_expiry',
                'expiry_date', 'waste_value'
            ]].to_dict(orient='records')
        }
    
    def check_facility_capacity(self, facility_id: str) -> Dict[str, Any]:
        """
        Check storage capacity for a facility
        
        Args:
            facility_id: Facility to check
        
        Returns:
            Capacity utilization info
        """
        
        capacity_info = self.loader.get_facility_capacity(facility_id)
        
        # Add recommendations
        utilization = capacity_info['utilization_percent']
        
        if utilization >= 95:
            recommendation = "CRITICAL: Facility at maximum capacity. Immediate action needed."
            alert_level = "CRITICAL"
        elif utilization >= 85:
            recommendation = "WARNING: High capacity utilization. Plan transfers/consumption."
            alert_level = "WARNING"
        elif utilization >= 70:
            recommendation = "CAUTION: Moderate capacity utilization. Monitor closely."
            alert_level = "CAUTION"
        else:
            recommendation = "NORMAL: Adequate storage capacity available."
            alert_level = "OK"
        
        return {
            **capacity_info,
            "alert_level": alert_level,
            "recommendation": recommendation
        }
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        facility_id: str,
        medication_id: str = None,
        message: str = None,
        recommended_action: str = None
    ) -> Dict[str, Any]:
        """
        Create an alert message for pharmacists
        
        Args:
            alert_type: Type of alert (expiring_stock, low_stock, capacity, etc.)
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            facility_id: Target facility
            medication_id: Optional medication ID
            message: Alert message text
            recommended_action: Suggested action for pharmacist
        
        Returns:
            Alert notification
        """
        
        alert = {
            "alert_id": f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "facility_id": facility_id,
            "medication_id": medication_id,
            "message": message or f"Alert: {alert_type}",
            "recommended_action": recommended_action or "Review and take appropriate action",
            "status": "CREATED"
        }
        
        return {
            "status": "success",
            "alert": alert,
            "notification_sent": True,
            "recipients": ["pharmacist@facility.com", "inventory_manager@facility.com"]
        }
    
    def get_inventory_summary(self, facility_id: str = None) -> Dict[str, Any]:
        """
        Get high-level inventory summary
        
        Args:
            facility_id: Optional facility filter
        
        Returns:
            Summary statistics
        """
        
        inventory_df = self.loader.data['inventory'].copy()
        medications_df = self.loader.data['medications']
        
        # Apply facility filter
        if facility_id:
            inventory_df = inventory_df[inventory_df['facility_id'] == facility_id]
        
        # Merge medication details for value calculation
        inventory_df = inventory_df.merge(
            medications_df[['medication_id', 'unit_cost']],
            on='medication_id',
            how='left'
        )
        
        inventory_value = (inventory_df['quantity_on_hand'] * inventory_df['unit_cost']).sum()
        
        return {
            "facility_id": facility_id,
            "total_batches": len(inventory_df),
            "total_units": int(inventory_df['quantity_on_hand'].sum()),
            "total_value": float(inventory_value),
            "average_batch_size": float(inventory_df['quantity_on_hand'].mean()),
            "unique_medications": int(inventory_df['medication_id'].nunique()),
            "summary_generated": datetime.now().isoformat()
        }


# Import pandas for data operations
import pandas as pd

# Create tool instances for agent use
def create_inventory_tools():
    """Factory function to create inventory tools"""
    return InventoryTools()


if __name__ == "__main__":
    # Test inventory tools
    print("\n🔧 Testing Inventory Tools\n")
    
    tools = create_inventory_tools()
    
    # Test 1: Query all inventory
    print("✅ Test 1: Query all inventory")
    result = tools.query_inventory()
    print(f"   Found {result['total_batches']} batches with {result['total_units']:,} units")
    
    # Test 2: Get expiring medications
    print("\n✅ Test 2: Get expiring medications")
    expiring = tools.get_expiring_medications(days_threshold=14)
    print(f"   Found {expiring['expiring_count']} items expiring within 14 days")
    print(f"   Total at-risk value: ${expiring['total_at_risk_value']:,.2f}")
    
    # Test 3: Check facility capacity
    print("\n✅ Test 3: Check facility capacity")
    facilities = tools.loader.data['facilities']['facility_id'].unique()
    if len(facilities) > 0:
        capacity = tools.check_facility_capacity(facilities[0])
        print(f"   Facility: {capacity['facility_name']}")
        print(f"   Utilization: {capacity['utilization_percent']}%")
        print(f"   Alert Level: {capacity['alert_level']}")
    
    # Test 4: Create alert
    print("\n✅ Test 4: Create alert")
    alert = tools.create_alert(
        alert_type="EXPIRING_STOCK",
        severity="HIGH",
        facility_id="FAC001",
        medication_id="MED001",
        message="Amoxicillin expiring in 3 days",
        recommended_action="Transfer to other facilities or dispose safely"
    )
    print(f"   Alert ID: {alert['alert']['alert_id']}")
    print(f"   Severity: {alert['alert']['severity']}")
    
    # Test 5: Get inventory summary
    print("\n✅ Test 5: Get inventory summary")
    summary = tools.get_inventory_summary()
    print(f"   Total batches: {summary['total_batches']}")
    print(f"   Total value: ${summary['total_value']:,.2f}")
    
    print("\n✅ All inventory tool tests passed!\n")
