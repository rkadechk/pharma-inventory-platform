"""
Input Data Validation Framework
Validates all input data before processing
"""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from decimal import Decimal


class InputDataValidator:
    """Validate input data before processing"""
    
    @staticmethod
    def validate_facility_data(facilities: List[Dict]) -> bool:
        """
        Validate facility data
        
        Rules:
        - facility_id must be unique and positive
        - location must not be empty
        - capacity_units must be positive
        """
        
        if not facilities:
            raise ValueError("❌ No facilities provided")
        
        facility_ids = set()
        for idx, f in enumerate(facilities):
            required = ['facility_id', 'facility_name', 'location', 'capacity_units']
            
            # Check required fields
            missing = [field for field in required if field not in f]
            if missing:
                raise ValueError(f"❌ Facility {idx}: Missing fields {missing}")
            
            # Check ID uniqueness
            if f['facility_id'] in facility_ids:
                raise ValueError(f"❌ Duplicate facility_id: {f['facility_id']}")
            facility_ids.add(f['facility_id'])
            
            # Check constraints
            if not isinstance(f['facility_id'], int) or f['facility_id'] <= 0:
                raise ValueError(f"❌ Facility {idx}: ID must be positive integer")
            
            if not f.get('location'):
                raise ValueError(f"❌ Facility {idx}: location cannot be empty")
            
            if not isinstance(f['capacity_units'], (int, float)) or f['capacity_units'] <= 0:
                raise ValueError(f"❌ Facility {idx}: capacity_units must be positive")
        
        return True
    
    @staticmethod
    def validate_medication_data(medications: List[Dict]) -> bool:
        """
        Validate medication data
        
        Rules:
        - medication_id unique & positive
        - medication_name unique & not empty
        - min_stock <= max_stock
        - avg_daily_consumption >= 0
        """
        
        if not medications:
            raise ValueError("❌ No medications provided")
        
        med_ids = set()
        med_names = set()
        
        for idx, m in enumerate(medications):
            required = ['medication_id', 'medication_name', 'min_stock_level', 
                       'max_stock_level', 'avg_daily_consumption']
            
            missing = [field for field in required if field not in m]
            if missing:
                raise ValueError(f"❌ Medication {idx}: Missing fields {missing}")
            
            # ID & Name uniqueness
            if m['medication_id'] in med_ids:
                raise ValueError(f"❌ Duplicate medication_id: {m['medication_id']}")
            if m['medication_name'] in med_names:
                raise ValueError(f"❌ Duplicate medication_name: {m['medication_name']}")
            
            med_ids.add(m['medication_id'])
            med_names.add(m['medication_name'])
            
            # Constraints
            if m['min_stock_level'] > m['max_stock_level']:
                raise ValueError(f"❌ Medication {idx}: min_stock > max_stock")
            
            if m['avg_daily_consumption'] < 0:
                raise ValueError(f"❌ Medication {idx}: avg_daily_consumption cannot be negative")
        
        return True
    
    @staticmethod
    def validate_consumption_history(consumption_list: List[Dict], 
                                    medications: List[Dict], 
                                    facilities: List[Dict],
                                    min_days: int = 30) -> bool:
        """
        Validate consumption history
        
        Rules:
        - medication_id exists
        - facility_id exists
        - quantity_consumed non-negative
        - sufficient historical data (min_days)
        """
        
        if not consumption_list:
            raise ValueError("❌ No consumption history provided")
        
        med_ids = {m['medication_id'] for m in medications}
        fac_ids = {f['facility_id'] for f in facilities}
        
        # Check each record
        for idx, c in enumerate(consumption_list):
            required = ['medication_id', 'facility_id', 'quantity_consumed', 'date']
            missing = [field for field in required if field not in c]
            if missing:
                raise ValueError(f"❌ Record {idx}: Missing fields {missing}")
            
            if c['medication_id'] not in med_ids:
                raise ValueError(f"❌ Record {idx}: Invalid medication_id {c['medication_id']}")
            
            if c['facility_id'] not in fac_ids:
                raise ValueError(f"❌ Record {idx}: Invalid facility_id {c['facility_id']}")
            
            if c['quantity_consumed'] < 0:
                raise ValueError(f"❌ Record {idx}: Negative quantity_consumed")
        
        # Check sufficient history
        if isinstance(consumption_list[0]['date'], str):
            dates = pd.to_datetime([c['date'] for c in consumption_list])
        else:
            dates = pd.to_datetime([c['date'].isoformat() if hasattr(c['date'], 'isoformat') 
                                   else c['date'] for c in consumption_list])
        
        days_covered = (dates.max() - dates.min()).days
        if days_covered < min_days:
            raise ValueError(f"❌ Insufficient history: {days_covered} days < {min_days}")
        
        return True
    
    @staticmethod
    def validate_batch_data(batches: List[Dict], 
                           medications: List[Dict],
                           facilities: List[Dict]) -> bool:
        """
        Validate inventory batch data
        
        Rules:
        - batch_id unique & positive
        - expiry_date > manufacture_date
        - quantity_units positive
        - unit_price positive
        - IDs valid references
        """
        
        if not batches:
            raise ValueError("❌ No inventory batches provided")
        
        batch_ids = set()
        med_ids = {m['medication_id'] for m in medications}
        fac_ids = {f['facility_id'] for f in facilities}
        
        for idx, b in enumerate(batches):
            required = ['batch_id', 'medication_id', 'facility_id', 'quantity_units', 
                       'unit_price', 'manufacture_date', 'expiry_date']
            missing = [field for field in required if field not in b]
            if missing:
                raise ValueError(f"❌ Batch {idx}: Missing fields {missing}")
            
            if b['batch_id'] in batch_ids:
                raise ValueError(f"❌ Duplicate batch_id: {b['batch_id']}")
            batch_ids.add(b['batch_id'])
            
            if b['medication_id'] not in med_ids:
                raise ValueError(f"❌ Batch {idx}: Invalid medication_id")
            
            if b['facility_id'] not in fac_ids:
                raise ValueError(f"❌ Batch {idx}: Invalid facility_id")
            
            # Parse dates
            if isinstance(b['expiry_date'], str):
                expiry = datetime.fromisoformat(b['expiry_date'])
                manufacture = datetime.fromisoformat(b['manufacture_date'])
            else:
                expiry = b['expiry_date']
                manufacture = b['manufacture_date']
            
            if expiry <= manufacture:
                raise ValueError(f"❌ Batch {idx}: Expiry <= Manufacture date")
            
            if b['quantity_units'] <= 0:
                raise ValueError(f"❌ Batch {idx}: quantity_units must be positive")
            
            unit_price = b.get('unit_price')
            if isinstance(unit_price, (int, float, Decimal)):
                if unit_price <= 0:
                    raise ValueError(f"❌ Batch {idx}: unit_price must be positive")
        
        return True
    
    @staticmethod
    def validate_supplier_data(suppliers: List[Dict]) -> bool:
        """
        Validate supplier data
        
        Rules:
        - supplier_id unique & positive
        - lead_time_days positive
        - reliability rating 0-1
        """
        
        if not suppliers:
            raise ValueError("❌ No suppliers provided")
        
        supplier_ids = set()
        
        for idx, s in enumerate(suppliers):
            required = ['supplier_id', 'supplier_name', 'lead_time_days', 'reliability_rating']
            missing = [field for field in required if field not in s]
            if missing:
                raise ValueError(f"❌ Supplier {idx}: Missing fields {missing}")
            
            if s['supplier_id'] in supplier_ids:
                raise ValueError(f"❌ Duplicate supplier_id: {s['supplier_id']}")
            supplier_ids.add(s['supplier_id'])
            
            if s['lead_time_days'] <= 0:
                raise ValueError(f"❌ Supplier {idx}: lead_time_days must be positive")
            
            reliability = float(s['reliability_rating'])
            if not (0 <= reliability <= 1):
                raise ValueError(f"❌ Supplier {idx}: reliability_rating must be 0-1")
        
        return True
