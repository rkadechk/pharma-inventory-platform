"""
Synthetic Data Generator for Pharmaceutical Inventory Optimization Platform
Generates realistic pharmacy data for:
1. Expiration Management
2. Multi-Facility Coordination
3. Demand Forecasting
4. Decision Support Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================================================
# DATA CONFIGURATION
# ============================================================================

FACILITIES = [
    {"id": "FAC001", "name": "Downtown Medical Center", "city": "Seattle", "state": "WA", "capacity": 10000},
    {"id": "FAC002", "name": "Northgate Community Hospital", "city": "Seattle", "state": "WA", "capacity": 5000},
    {"id": "FAC003", "name": "Eastside Regional Medical", "city": "Bellevue", "state": "WA", "capacity": 8000},
    {"id": "FAC004", "name": "Suburban Health Clinic", "city": "Renton", "state": "WA", "capacity": 3000},
    {"id": "FAC005", "name": "Central Valley Hospital", "city": "Yakima", "state": "WA", "capacity": 4000},
]

# Top 50 medications by usage in US hospitals
MEDICATIONS = [
    {"id": "MED001", "name": "Lisinopril 10mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    {"id": "MED002", "name": "Metformin 500mg", "category": "Endocrine", "shelf_life_days": 1825},
    {"id": "MED003", "name": "Atorvastatin 20mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    {"id": "MED004", "name": "Omeprazole 20mg", "category": "GI", "shelf_life_days": 1095},
    {"id": "MED005", "name": "Amoxicillin 500mg", "category": "Antibiotic", "shelf_life_days": 730},
    {"id": "MED006", "name": "Ibuprofen 400mg", "category": "Pain", "shelf_life_days": 1825},
    {"id": "MED007", "name": "Albuterol Inhaler", "category": "Respiratory", "shelf_life_days": 1095},
    {"id": "MED008", "name": "Metoprolol 50mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    {"id": "MED009", "name": "Sertraline 50mg", "category": "Psychiatric", "shelf_life_days": 1825},
    {"id": "MED010", "name": "Levothyroxine 50mcg", "category": "Endocrine", "shelf_life_days": 1825},
    {"id": "MED011", "name": "Amlodipine 5mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    {"id": "MED012", "name": "Clopidogrel 75mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    {"id": "MED013", "name": "Azithromycin 500mg", "category": "Antibiotic", "shelf_life_days": 730},
    {"id": "MED014", "name": "Ciprofloxacin 500mg", "category": "Antibiotic", "shelf_life_days": 730},
    {"id": "MED015", "name": "Ranitidine 150mg", "category": "GI", "shelf_life_days": 1095},
    {"id": "MED016", "name": "Hydrocodone/Acetaminophen", "category": "Pain", "shelf_life_days": 1825},
    {"id": "MED017", "name": "Prednisone 5mg", "category": "Immunosuppressant", "shelf_life_days": 1825},
    {"id": "MED018", "name": "Fluoxetine 20mg", "category": "Psychiatric", "shelf_life_days": 1825},
    {"id": "MED019", "name": "Diphenhydramine 25mg", "category": "Antihistamine", "shelf_life_days": 1825},
    {"id": "MED020", "name": "Metoclopramide 10mg", "category": "GI", "shelf_life_days": 1095},
    {"id": "MED021", "name": "Insulin Glargine (Vial)", "category": "Endocrine", "shelf_life_days": 365},
    {"id": "MED022", "name": "Warfarin 5mg", "category": "Anticoagulant", "shelf_life_days": 1825},
    {"id": "MED023", "name": "Aspirin 81mg", "category": "Antiplatelet", "shelf_life_days": 1825},
    {"id": "MED024", "name": "Cefdinir 300mg", "category": "Antibiotic", "shelf_life_days": 730},
    {"id": "MED025", "name": "Trimethoprim-Sulfamethoxazole", "category": "Antibiotic", "shelf_life_days": 730},
]

# ============================================================================
# GENERATOR FUNCTIONS
# ============================================================================

def generate_facilities_table(facilities):
    """Generate facilities master data."""
    df = pd.DataFrame(facilities)
    df['created_date'] = datetime.now()
    df['last_updated'] = datetime.now()
    return df

def generate_medications_table(medications):
    """Generate medications master data."""
    df = pd.DataFrame(medications)
    df['created_date'] = datetime.now()
    df['last_updated'] = datetime.now()
    return df

def generate_inventory_table(facilities, medications, num_batches=3000):
    """
    Generate inventory records with realistic stock levels, batch numbers, and expiration dates.
    This supports Expiration Management feature.
    """
    records = []
    start_date = datetime.now() - timedelta(days=365)
    now = datetime.now()

    for _ in range(num_batches):
        facility = random.choice(facilities)
        medication = random.choice(medications)

        # Generate realistic quantity (variation by facility size and med category)
        base_qty = facility['capacity'] * np.random.uniform(0.05, 0.30) / len(medications)
        quantity_on_hand = max(int(base_qty * np.random.gamma(2, 1)), 10)

        # 25% of batches are "old stock" — expiry falls within the next 365 days
        # so every medication category has near-expiry items visible on the dashboard.
        near_expiry_batch = random.random() < 0.25
        if near_expiry_batch:
            # Target expiry: 0-365 days from now (spread across CRITICAL/HIGH/MEDIUM/LOW)
            days_to_target_expiry = random.randint(-5, 365)
            expiration_date = now + timedelta(days=days_to_target_expiry)
            purchase_date = expiration_date - timedelta(days=medication['shelf_life_days'])
        else:
            purchase_date = start_date + timedelta(days=random.randint(0, 365))
            expiration_date = purchase_date + timedelta(days=medication['shelf_life_days'])
        
        # Calculate days until expiry
        days_to_expiry = (expiration_date - datetime.now()).days
        
        # Determine risk level
        if days_to_expiry <= 0:
            risk_level = "EXPIRED"
        elif days_to_expiry <= 30:
            risk_level = "CRITICAL"
        elif days_to_expiry <= 90:
            risk_level = "HIGH"
        elif days_to_expiry <= 180:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        records.append({
            "inventory_id": f"INV{_:06d}",
            "facility_id": facility['id'],
            "medication_id": medication['id'],
            "batch_number": f"BATCH{random.randint(100000, 999999)}",
            "quantity_on_hand": quantity_on_hand,
            "reorder_level": int(quantity_on_hand * 0.25),
            "purchase_date": purchase_date,
            "expiration_date": expiration_date,
            "days_to_expiry": days_to_expiry,
            "risk_level": risk_level,
            "storage_location": f"SHELF_{random.randint(1, 20)}",
            "last_counted": purchase_date + timedelta(days=random.randint(0, 90)),
            "created_date": datetime.now(),
        })
    
    return pd.DataFrame(records)

def generate_consumption_table(facilities, medications, num_days=365, records_per_day=500):
    """
    Generate daily consumption records for demand forecasting.
    This supports Demand Forecasting feature.
    """
    records = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Add seasonality: higher consumption in winter months (flu season)
        month = current_date.month
        if month in [11, 12, 1, 2]:
            seasonal_factor = 1.3
        elif month in [3, 4, 9, 10]:
            seasonal_factor = 1.0
        else:
            seasonal_factor = 0.8
        
        # Generate consumption events for the day
        num_records = int(records_per_day * seasonal_factor * np.random.uniform(0.8, 1.2))
        
        for _ in range(num_records):
            facility = random.choice(facilities)
            medication = random.choice(medications)
            
            # Quantity typically 1-20 units per transaction
            quantity = np.random.poisson(3) + 1
            
            records.append({
                "transaction_id": f"TXN{len(records):08d}",
                "facility_id": facility['id'],
                "medication_id": medication['id'],
                "transaction_date": current_date,
                "transaction_type": "CONSUMPTION",
                "quantity": quantity,
                "unit_price": round(np.random.uniform(2, 50), 2),
                "total_cost": round(quantity * np.random.uniform(2, 50), 2),
                "department": random.choice(["ICU", "ER", "Pharmacy", "General Ward", "Surgery"]),
                "prescriber_id": f"DOC{random.randint(100, 999)}",
                "created_date": datetime.now(),
            })
    
    return pd.DataFrame(records)

def generate_transfers_table(facilities, medications, num_transfers=500):
    """
    Generate historical inter-facility transfer records with realistic variety.
    Supports Multi-Facility Coordination feature.
    """
    records = []
    start_date = datetime.now() - timedelta(days=180)

    # Realistic unit costs per category
    UNIT_COSTS = {
        "Cardiovascular":    18.50,
        "Endocrine":         12.75,
        "GI":                 8.20,
        "Antibiotic":        22.40,
        "Pain":               6.80,
        "Respiratory":       35.00,
        "Psychiatric":       14.60,
        "Immunosuppressant": 28.90,
        "Antihistamine":      5.40,
        "Anticoagulant":     42.00,
        "Antiplatelet":       4.90,
    }

    # Status weights: heavier towards actionable states for demo richness
    STATUS_POOL = (
        ["COMPLETED"]    * 18 +
        ["PENDING"]      * 12 +
        ["APPROVED"]     * 8  +
        ["IN_TRANSIT"]   * 6  +
        ["REJECTED"]     * 4  +
        ["BLOCKED"]      * 2
    )

    REASONS = [
        "Expiration Management",
        "Shortage Prevention",
        "Demand Spike",
        "Regulatory",
        "Demand Spike",          # repeated for higher weight
        "Shortage Prevention",
        "Expiration Management",
    ]

    for i in range(num_transfers):
        source = random.choice(facilities)
        target = random.choice([f for f in facilities if f['id'] != source['id']])
        medication = random.choice(medications)

        transfer_date  = start_date + timedelta(days=random.randint(0, 180))
        received_date  = transfer_date + timedelta(days=random.randint(1, 5))
        status         = random.choice(STATUS_POOL)
        reason         = random.choice(REASONS)

        qty_requested   = int(np.random.uniform(50, 600))
        qty_transferred = (int(qty_requested * np.random.uniform(0.75, 1.0))
                           if status not in ("REJECTED", "BLOCKED") else 0)
        distance        = round(np.random.uniform(5, 120), 1)
        unit_cost       = UNIT_COSTS.get(medication.get('category', 'Pain'), 10.0)
        # Transfer cost: base rate + per-mile logistics
        transfer_cost   = round(max(45.0, 25.0 + distance * 1.80 + qty_transferred * 0.12), 2)
        med_value       = round(qty_transferred * unit_cost, 2)
        # Savings: value rescued from expiry or shortage (fraction varies by reason)
        savings_rate    = {"Expiration Management": 0.55, "Shortage Prevention": 0.40,
                           "Demand Spike": 0.35, "Regulatory": 0.20}.get(reason, 0.30)
        estimated_savings = round(med_value * savings_rate, 2)
        # Efficiency: ratio of savings to total cost, capped at 1.0
        efficiency_score  = round(min(1.0, estimated_savings / max(transfer_cost + med_value * 0.05, 1)), 3)
        cost_benefit      = round(min(1.5, estimated_savings / max(transfer_cost, 1)), 3)

        records.append({
            "transfer_id":         f"TRF{i:06d}",
            "source_facility_id":  source['id'],
            "target_facility_id":  target['id'],
            "medication_id":       medication['id'],
            "quantity_requested":  qty_requested,
            "quantity_transferred":qty_transferred,
            "transfer_date":       transfer_date,
            "received_date":       received_date if status == "COMPLETED" else None,
            "transfer_status":     status,
            "reason":              reason,
            "distance_miles":      distance,
            "cost_usd":            transfer_cost,
            "estimated_savings":   estimated_savings,
            "efficiency_score":    efficiency_score,
            "cost_benefit_score":  cost_benefit,
            "created_date":        datetime.now(),
        })

    return pd.DataFrame(records)

def generate_external_signals_table(num_days=365):
    """
    Generate external signals (weather, disease outbreaks, events).
    This supports Demand Forecasting feature with external factors.
    """
    records = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    # Disease outbreaks
    outbreak_dates = [
        start_date + timedelta(days=random.randint(0, num_days))
        for _ in range(random.randint(2, 5))
    ]
    
    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        
        # Weather severity
        weather_severity = "NORMAL"
        if current_date.month in [12, 1]:
            if random.random() < 0.3:
                weather_severity = random.choice(["COLD_WAVE", "SNOW"])
        
        # Disease outbreak signals
        disease_signal = "NONE"
        if any(abs((d - current_date).days) <= 30 for d in outbreak_dates):
            disease_signal = random.choice(["FLU_SPIKE", "COVID_SURGE", "RSV_OUTBREAK"])
        
        # Hospital events
        hospital_event = "NONE"
        if random.random() < 0.05:
            hospital_event = random.choice(["EMERGENCY_DRILL", "CONFERENCE", "HOLIDAY"])
        
        records.append({
            "signal_date": current_date,
            "weather_condition": "SUNNY" if weather_severity == "NORMAL" else weather_severity,
            "weather_severity": weather_severity,
            "disease_signal": disease_signal,
            "hospital_event": hospital_event,
            "external_demand_factor": 1.0 if weather_severity == "NORMAL" else 1.2 if disease_signal != "NONE" else 0.9,
            "created_date": datetime.now(),
        })
    
    return pd.DataFrame(records)

def generate_forecast_baseline_table(medications, facilities):
    """
    Generate demand forecast data: one row per medication with realistic, varied values.
    Columns match exactly what the /export/demand-forecast API endpoint expects.
    """
    # Per-medication hand-crafted realistic values.
    # urgency_level drives suggested_action and risk_level automatically.
    MED_FORECAST = {
        # id: (7d, 14d, 30d, current_inv, confidence, model, mape, min_safety, max_cap, urgency, anomalies, ext_signal)
        "MED001": (850,  1650, 3400,  4200, 0.92, "ARIMA",    0.082, 1500, 8000,  "LOW",      0, "None"),
        "MED002": (1100, 2180, 4400,  5200, 0.93, "ARIMA",    0.065, 2000, 9000,  "LOW",      0, "None"),
        "MED003": (780,  1520, 3100,  2100, 0.89, "PROPHET",  0.095, 1200, 7000,  "LOW",      0, "None"),
        "MED004": (720,  1400, 2900,  2800, 0.90, "ARIMA",    0.088, 1000, 6000,  "LOW",      0, "None"),
        "MED005": (940,  1850, 3750,  1100, 0.82, "PROPHET",  0.163, 1500, 7000,  "HIGH",     1, "Flu season +38% demand"),
        "MED006": (1050, 2060, 4200,  3500, 0.88, "PROPHET",  0.104, 1500, 8000,  "LOW",      0, "None"),
        "MED007": (760,  1490, 3020,   900, 0.86, "PROPHET",  0.117, 1200, 5500,  "HIGH",     1, "Cold front — asthma surge"),
        "MED008": (920,  1840, 3750,  1200, 0.87, "PROPHET",  0.113, 1500, 7000,  "HIGH",     1, "None"),
        "MED009": (540,  1060, 2150,  2600, 0.91, "ARIMA",    0.077, 900,  5000,  "LOW",      0, "None"),
        "MED010": (650,  1280, 2600,  3100, 0.94, "ARIMA",    0.058, 1000, 5500,  "LOW",      0, "None"),
        "MED011": (680,  1320, 2700,  3800, 0.91, "ARIMA",    0.078, 1100, 6000,  "LOW",      0, "None"),
        "MED012": (510,  990,  2050,   450, 0.84, "PROPHET",  0.142, 900,  4500,  "CRITICAL", 2, "Cardiovascular event surge +41%"),
        "MED013": (620,  1220, 2480,   800, 0.79, "PROPHET",  0.194, 1000, 5000,  "HIGH",     1, "Respiratory outbreak signal"),
        "MED014": (290,  570,  1160,   950, 0.85, "ARIMA",    0.118, 500,  3000,  "MEDIUM",   0, "None"),
        "MED015": (430,  850,  1720,  1800, 0.86, "BASELINE", 0.134, 700,  4000,  "MEDIUM",   0, "None"),
        "MED016": (480,  940,  1900,   280, 0.85, "ARIMA",    0.128, 600,  3500,  "CRITICAL", 1, "Post-holiday elective surgery spike"),
        "MED017": (320,  630,  1280,  1600, 0.86, "ARIMA",    0.111, 600,  3500,  "LOW",      0, "None"),
        "MED018": (390,  770,  1560,  1900, 0.90, "ARIMA",    0.083, 700,  4000,  "LOW",      0, "None"),
        "MED019": (410,  810,  1640,  2200, 0.88, "BASELINE", 0.095, 800,  4500,  "LOW",      0, "None"),
        "MED020": (180,  355,   720,   900, 0.81, "BASELINE", 0.178, 400,  2500,  "MEDIUM",   0, "None"),
        "MED021": (380,  750,  1520,   600, 0.88, "PROPHET",  0.121, 500,  3000,  "HIGH",     1, "Seasonal diabetes management spike"),
        "MED022": (290,  570,  1160,   200, 0.87, "ARIMA",    0.103, 400,  2500,  "CRITICAL", 1, "None"),
        "MED023": (870,  1710, 3470,  4800, 0.92, "BASELINE", 0.072, 1500, 7000,  "LOW",      0, "None"),
        "MED024": (250,  490,  1000,   320, 0.80, "PROPHET",  0.170, 400,  2500,  "CRITICAL", 2, "Pediatric respiratory infections +52%"),
        "MED025": (310,  610,  1240,  1400, 0.83, "ARIMA",    0.139, 500,  3000,  "LOW",      0, "None"),
    }

    URGENCY_TO_ACTION = {
        "CRITICAL": "URGENT_REORDER",
        "HIGH":     "REORDER",
        "MEDIUM":   "MONITOR",
        "LOW":      "MONITOR",
    }

    records = []
    for medication in medications:
        mid = medication['id']
        vals = MED_FORECAST.get(mid)
        if vals is None:
            # Fallback for any medication not hand-crafted
            vals = (300, 580, 1200, 1500, 0.85, "PROPHET", 0.15, 600, 3000, "MEDIUM", 0, "None")

        d7, d14, d30, inv, conf, model, mape, min_s, max_c, urgency, anomalies, ext = vals

        # Derived urgency check: if stock < 7d demand → CRITICAL regardless
        if inv < d7:
            urgency = "CRITICAL"
        elif inv < d14:
            urgency = max(urgency, "HIGH") if urgency in ("MEDIUM", "LOW") else urgency

        records.append({
            "medication_id":         mid,
            "demand_7day_forecast":  d7,
            "demand_14day_forecast": d14,
            "demand_30day_forecast": d30,
            "current_inventory":     inv,
            "forecast_confidence":   conf,
            "forecast_model":        model,
            "model_mape":            mape,
            "min_safety_stock":      min_s,
            "max_capacity":          max_c,
            "urgency_level":         urgency,
            "suggested_action":      URGENCY_TO_ACTION[urgency],
            "risk_level":            urgency,
            "anomalies_detected":    anomalies,
            "external_signals":      ext,
        })

    return pd.DataFrame(records)

def generate_replenishment_orders_table(facilities, medications, num_orders=200):
    """
    Generate replenishment order records.
    This supports Decision Support Analytics.
    """
    records = []
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(num_orders):
        facility = random.choice(facilities)
        medication = random.choice(medications)
        
        order_date = start_date + timedelta(days=random.randint(0, 90))
        delivery_date = order_date + timedelta(days=random.randint(2, 10))
        
        order_status = random.choice(["DELIVERED", "DELIVERED", "DELIVERED", "PENDING", "CANCELLED"])
        
        records.append({
            "order_id": f"ORD{i:06d}",
            "facility_id": facility['id'],
            "medication_id": medication['id'],
            "order_date": order_date,
            "delivery_date": delivery_date if order_status == "DELIVERED" else None,
            "order_quantity": int(np.random.uniform(100, 1000)),
            "unit_cost": round(np.random.uniform(2, 50), 2),
            "order_status": order_status,
            "supplier_id": f"SUP{random.randint(1, 10):02d}",
            "created_date": datetime.now(),
        })
    
    return pd.DataFrame(records)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all synthetic data and export to CSV."""
    
    output_dir = "synthetic_data"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 80)
    print("PHARMACEUTICAL INVENTORY SYNTHETIC DATA GENERATOR")
    print("=" * 80)
    print()
    
    # 1. Generate Facilities
    print("[1/8] Generating Facilities data...")
    facilities_df = generate_facilities_table(FACILITIES)
    facilities_df.to_csv(f"{output_dir}/facilities.csv", index=False)
    print(f"    ✓ Generated {len(facilities_df)} facility records")
    
    # 2. Generate Medications
    print("[2/8] Generating Medications data...")
    medications_df = generate_medications_table(MEDICATIONS)
    medications_df.to_csv(f"{output_dir}/medications.csv", index=False)
    print(f"    ✓ Generated {len(medications_df)} medication records")
    
    # 3. Generate Inventory
    print("[3/8] Generating Inventory data (Expiration Management)...")
    inventory_df = generate_inventory_table(FACILITIES, MEDICATIONS, num_batches=3000)
    inventory_df.to_csv(f"{output_dir}/inventory.csv", index=False)
    print(f"    ✓ Generated {len(inventory_df)} inventory batch records")
    print(f"       Risk distribution: {inventory_df['risk_level'].value_counts().to_dict()}")
    
    # 4. Generate Consumption
    print("[4/8] Generating Consumption data (Demand Forecasting)...")
    consumption_df = generate_consumption_table(FACILITIES, MEDICATIONS, num_days=365, records_per_day=500)
    consumption_df.to_csv(f"{output_dir}/consumption.csv", index=False)
    print(f"    ✓ Generated {len(consumption_df)} consumption transaction records")
    
    # 5. Generate Transfers
    print("[5/8] Generating Transfer data (Multi-Facility Coordination)...")
    transfers_df = generate_transfers_table(FACILITIES, MEDICATIONS, num_transfers=500)
    transfers_df.to_csv(f"{output_dir}/transfers.csv", index=False)
    print(f"    ✓ Generated {len(transfers_df)} inter-facility transfer records")
    print(f"       Status distribution: {transfers_df['transfer_status'].value_counts().to_dict()}")
    
    # 6. Generate External Signals
    print("[6/8] Generating External Signals data (Demand Forecasting)...")
    signals_df = generate_external_signals_table(num_days=365)
    signals_df.to_csv(f"{output_dir}/external_signals.csv", index=False)
    print(f"    ✓ Generated {len(signals_df)} daily external signal records")
    
    # 7. Generate Forecast Baseline
    print("[7/8] Generating Demand Forecast baseline...")
    forecast_df = generate_forecast_baseline_table(MEDICATIONS, FACILITIES)
    forecast_df.to_csv(f"{output_dir}/demand_forecast.csv", index=False)
    print(f"    ✓ Generated {len(forecast_df)} forecast records (90-day forward)")
    
    # 8. Generate Replenishment Orders
    print("[8/8] Generating Replenishment Orders data...")
    orders_df = generate_replenishment_orders_table(FACILITIES, MEDICATIONS, num_orders=200)
    orders_df.to_csv(f"{output_dir}/replenishment_orders.csv", index=False)
    print(f"    ✓ Generated {len(orders_df)} replenishment order records")
    
    # Generate summary statistics
    print()
    print("=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    print(f"Output directory: {os.path.abspath(output_dir)}")
    print()
    print("Files generated:")
    print(f"  • facilities.csv ({len(facilities_df)} rows)")
    print(f"  • medications.csv ({len(medications_df)} rows)")
    print(f"  • inventory.csv ({len(inventory_df)} rows)")
    print(f"  • consumption.csv ({len(consumption_df)} rows)")
    print(f"  • transfers.csv ({len(transfers_df)} rows)")
    print(f"  • external_signals.csv ({len(signals_df)} rows)")
    print(f"  • demand_forecast.csv ({len(forecast_df)} rows)")
    print(f"  • replenishment_orders.csv ({len(orders_df)} rows)")
    print()
    
    # Key statistics for feature validation
    print("Key Statistics (Feature Validation):")
    print()
    print("1. EXPIRATION MANAGEMENT:")
    risk_counts = inventory_df['risk_level'].value_counts()
    print(f"   • Items at risk of expiry (CRITICAL+HIGH): {risk_counts.get('CRITICAL', 0) + risk_counts.get('HIGH', 0)}")
    print(f"   • Expired items: {risk_counts.get('EXPIRED', 0)}")
    print()
    
    print("2. MULTI-FACILITY COORDINATION:")
    completed_transfers = len(transfers_df[transfers_df['transfer_status'] == 'COMPLETED'])
    print(f"   • Completed transfers: {completed_transfers}")
    print(f"   • Facilities in network: {len(facilities_df)}")
    print()
    
    print("3. DEMAND FORECASTING:")
    print(f"   • Historical consumption days: 365")
    print(f"   • Forecast horizon: 90 days")
    print(f"   • Medications tracked: {len(medications_df)}")
    print()
    
    print("4. DECISION SUPPORT ANALYTICS:")
    print(f"   • Inventory visibility: {len(inventory_df)} batches across {len(facilities_df)} facilities")
    print(f"   • Pending transfers: {len(transfers_df[transfers_df['transfer_status'] == 'PENDING'])}")
    print(f"   • Pending orders: {len(orders_df[orders_df['order_status'] == 'PENDING'])}")
    print()
    print("=" * 80)
    print("✓ Synthetic data generation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
