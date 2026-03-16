"""
Lightweight Synthetic Data Generator (pure Python, no external deps)
Generates realistic pharmacy data for the 4 key features
"""

from datetime import datetime, timedelta
import random
import os
import csv

# Set random seed for reproducibility
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
    
    # 1. Facilities
    print("[1/8] Generating Facilities data...")
    with open(f"{output_dir}/facilities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "city", "state", "capacity", "created_date", "last_updated"])
        writer.writeheader()
        for fac in FACILITIES:
            writer.writerow({
                "id": fac["id"],
                "name": fac["name"],
                "city": fac["city"],
                "state": fac["state"],
                "capacity": fac["capacity"],
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            })
    print(f"    ✓ Generated {len(FACILITIES)} facility records")
    
    # 2. Medications
    print("[2/8] Generating Medications data...")
    with open(f"{output_dir}/medications.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "shelf_life_days", "created_date", "last_updated"])
        writer.writeheader()
        for med in MEDICATIONS:
            writer.writerow({
                "id": med["id"],
                "name": med["name"],
                "category": med["category"],
                "shelf_life_days": med["shelf_life_days"],
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            })
    print(f"    ✓ Generated {len(MEDICATIONS)} medication records")
    
    # 3. Inventory (Expiration Management)
    print("[3/8] Generating Inventory data (Expiration Management)...")
    risk_counts = {"EXPIRED": 0, "CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    start_date = datetime.now() - timedelta(days=365)
    
    with open(f"{output_dir}/inventory.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "inventory_id", "facility_id", "medication_id", "batch_number", "quantity_on_hand",
            "reorder_level", "purchase_date", "expiration_date", "days_to_expiry", "risk_level",
            "storage_location", "last_counted", "created_date"
        ])
        writer.writeheader()
        
        for i in range(3000):
            facility = random.choice(FACILITIES)
            medication = random.choice(MEDICATIONS)
            base_qty = facility["capacity"] * random.uniform(0.05, 0.30) / len(MEDICATIONS)
            quantity_on_hand = max(int(base_qty * (1 + random.gauss(0, 0.3))), 10)
            
            purchase_date = start_date + timedelta(days=random.randint(0, 365))
            expiration_date = purchase_date + timedelta(days=medication["shelf_life_days"])
            days_to_expiry = (expiration_date - datetime.now()).days
            
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
            
            risk_counts[risk_level] += 1
            
            writer.writerow({
                "inventory_id": f"INV{i:06d}",
                "facility_id": facility["id"],
                "medication_id": medication["id"],
                "batch_number": f"BATCH{random.randint(100000, 999999)}",
                "quantity_on_hand": quantity_on_hand,
                "reorder_level": int(quantity_on_hand * 0.25),
                "purchase_date": purchase_date.date(),
                "expiration_date": expiration_date.date(),
                "days_to_expiry": days_to_expiry,
                "risk_level": risk_level,
                "storage_location": f"SHELF_{random.randint(1, 20)}",
                "last_counted": (purchase_date + timedelta(days=random.randint(0, 90))).date(),
                "created_date": datetime.now().isoformat(),
            })
    print(f"    ✓ Generated 3000 inventory batch records")
    print(f"       Risk distribution: {risk_counts}")
    
    # 4. Consumption (Demand Forecasting)
    print("[4/8] Generating Consumption data (Demand Forecasting)...")
    with open(f"{output_dir}/consumption.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transaction_id", "facility_id", "medication_id", "transaction_date", "transaction_type",
            "quantity", "unit_price", "total_cost", "department", "prescriber_id", "created_date"
        ])
        writer.writeheader()
        
        tx_count = 0
        for day_offset in range(365):
            current_date = start_date + timedelta(days=day_offset)
            month = current_date.month
            seasonal_factor = 1.3 if month in [11, 12, 1, 2] else (1.0 if month in [3, 4, 9, 10] else 0.8)
            
            num_records = int(500 * seasonal_factor * random.uniform(0.8, 1.2))
            
            for _ in range(num_records):
                facility = random.choice(FACILITIES)
                medication = random.choice(MEDICATIONS)
                quantity = random.randint(1, 20)
                unit_price = round(random.uniform(2, 50), 2)
                
                writer.writerow({
                    "transaction_id": f"TXN{tx_count:08d}",
                    "facility_id": facility["id"],
                    "medication_id": medication["id"],
                    "transaction_date": current_date.date(),
                    "transaction_type": "CONSUMPTION",
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_cost": round(quantity * unit_price, 2),
                    "department": random.choice(["ICU", "ER", "Pharmacy", "General Ward", "Surgery"]),
                    "prescriber_id": f"DOC{random.randint(100, 999)}",
                    "created_date": datetime.now().isoformat(),
                })
                tx_count += 1
    
    print(f"    ✓ Generated {tx_count} consumption transaction records")
    
    # 5. Transfers (Multi-Facility Coordination)
    print("[5/8] Generating Transfer data (Multi-Facility Coordination)...")
    transfer_statuses = {"COMPLETED": 0, "PENDING": 0, "REJECTED": 0}
    
    with open(f"{output_dir}/transfers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "transfer_id", "source_facility_id", "target_facility_id", "medication_id",
            "quantity_requested", "quantity_transferred", "transfer_date", "received_date",
            "transfer_status", "reason", "distance_miles", "cost_usd", "created_date"
        ])
        writer.writeheader()
        
        for i in range(500):
            source_facility = random.choice(FACILITIES)
            target_facility = random.choice([f for f in FACILITIES if f["id"] != source_facility["id"]])
            medication = random.choice(MEDICATIONS)
            
            transfer_date = start_date + timedelta(days=random.randint(0, 180))
            received_date = transfer_date + timedelta(days=random.randint(1, 5))
            transfer_status = random.choice(["COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "REJECTED"])
            transfer_statuses[transfer_status] += 1
            
            writer.writerow({
                "transfer_id": f"TRF{i:06d}",
                "source_facility_id": source_facility["id"],
                "target_facility_id": target_facility["id"],
                "medication_id": medication["id"],
                "quantity_requested": int(random.uniform(50, 500)),
                "quantity_transferred": int(random.uniform(30, 500)) if transfer_status != "REJECTED" else 0,
                "transfer_date": transfer_date.date(),
                "received_date": received_date.date() if transfer_status == "COMPLETED" else "",
                "transfer_status": transfer_status,
                "reason": random.choice(["Shortage Prevention", "Expiration Management", "Demand Spike", "Regulatory"]),
                "distance_miles": round(random.uniform(5, 100), 1),
                "cost_usd": round(random.uniform(50, 500), 2),
                "created_date": datetime.now().isoformat(),
            })
    print(f"    ✓ Generated 500 inter-facility transfer records")
    print(f"       Status distribution: {transfer_statuses}")
    
    # 6. External Signals (Demand Forecasting)
    print("[6/8] Generating External Signals data (Demand Forecasting)...")
    with open(f"{output_dir}/external_signals.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "signal_date", "weather_condition", "weather_severity", "disease_signal",
            "hospital_event", "external_demand_factor", "created_date"
        ])
        writer.writeheader()
        
        for day_offset in range(365):
            current_date = start_date + timedelta(days=day_offset)
            month = current_date.month
            
            weather_severity = "NORMAL"
            if month in [12, 1] and random.random() < 0.3:
                weather_severity = random.choice(["COLD_WAVE", "SNOW"])
            
            disease_signal = "NONE"
            if random.random() < 0.1:
                disease_signal = random.choice(["FLU_SPIKE", "COVID_SURGE", "RSV_OUTBREAK", "NONE", "NONE"])
            
            hospital_event = "NONE"
            if random.random() < 0.05:
                hospital_event = random.choice(["EMERGENCY_DRILL", "CONFERENCE", "HOLIDAY"])
            
            demand_factor = 1.0
            if weather_severity != "NORMAL":
                demand_factor = 1.2
            elif disease_signal != "NONE":
                demand_factor = 1.3
            elif hospital_event != "NONE":
                demand_factor = 0.9
            
            writer.writerow({
                "signal_date": current_date.date(),
                "weather_condition": "SUNNY" if weather_severity == "NORMAL" else weather_severity,
                "weather_severity": weather_severity,
                "disease_signal": disease_signal,
                "hospital_event": hospital_event,
                "external_demand_factor": demand_factor,
                "created_date": datetime.now().isoformat(),
            })
    
    print(f"    ✓ Generated 365 daily external signal records")
    
    # 7. Demand Forecast (Decision Support)
    print("[7/8] Generating Demand Forecast baseline...")
    with open(f"{output_dir}/demand_forecast.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "forecast_id", "facility_id", "medication_id", "forecast_date", "forecast_quantity",
            "confidence_interval_lower", "confidence_interval_upper", "forecast_method", "created_date"
        ])
        writer.writeheader()
        
        forecast_count = 0
        current_date = datetime.now()
        for day_offset in range(90):
            forecast_date = current_date + timedelta(days=day_offset)
            month = forecast_date.month
            seasonal_factor = 1.3 if month in [11, 12, 1, 2] else 1.0
            
            for facility in FACILITIES:
                for medication in MEDICATIONS[:10]:
                    base_demand = random.randint(50, 200)
                    forecast_qty = int(base_demand * seasonal_factor)
                    
                    writer.writerow({
                        "forecast_id": f"FCT{forecast_count:08d}",
                        "facility_id": facility["id"],
                        "medication_id": medication["id"],
                        "forecast_date": forecast_date.date(),
                        "forecast_quantity": forecast_qty,
                        "confidence_interval_lower": int(forecast_qty * 0.8),
                        "confidence_interval_upper": int(forecast_qty * 1.2),
                        "forecast_method": "Prophet",
                        "created_date": datetime.now().isoformat(),
                    })
                    forecast_count += 1
    
    print(f"    ✓ Generated {forecast_count} forecast records (90-day forward)")
    
    # 8. Replenishment Orders (Decision Support)
    print("[8/8] Generating Replenishment Orders data...")
    order_statuses = {"DELIVERED": 0, "PENDING": 0, "CANCELLED": 0}
    
    with open(f"{output_dir}/replenishment_orders.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "order_id", "facility_id", "medication_id", "order_date", "delivery_date",
            "order_quantity", "unit_cost", "order_status", "supplier_id", "created_date"
        ])
        writer.writeheader()
        
        for i in range(200):
            facility = random.choice(FACILITIES)
            medication = random.choice(MEDICATIONS)
            
            order_date = start_date + timedelta(days=random.randint(0, 90))
            delivery_date = order_date + timedelta(days=random.randint(2, 10))
            order_status = random.choice(["DELIVERED", "DELIVERED", "DELIVERED", "PENDING", "CANCELLED"])
            order_statuses[order_status] += 1
            
            writer.writerow({
                "order_id": f"ORD{i:06d}",
                "facility_id": facility["id"],
                "medication_id": medication["id"],
                "order_date": order_date.date(),
                "delivery_date": delivery_date.date() if order_status == "DELIVERED" else "",
                "order_quantity": int(random.uniform(100, 1000)),
                "unit_cost": round(random.uniform(2, 50), 2),
                "order_status": order_status,
                "supplier_id": f"SUP{random.randint(1, 10):02d}",
                "created_date": datetime.now().isoformat(),
            })
    
    print(f"    ✓ Generated 200 replenishment order records")
    print(f"       Status distribution: {order_statuses}")
    
    # Summary
    print()
    print("=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    print(f"Output directory: {os.path.abspath(output_dir)}")
    print()
    print("Files generated:")
    print(f"  • facilities.csv (5 rows)")
    print(f"  • medications.csv (25 rows)")
    print(f"  • inventory.csv (3,000 rows)")
    print(f"  • consumption.csv (~182,500 rows)")
    print(f"  • transfers.csv (500 rows)")
    print(f"  • external_signals.csv (365 rows)")
    print(f"  • demand_forecast.csv ({forecast_count} rows)")
    print(f"  • replenishment_orders.csv (200 rows)")
    print()
    print("=" * 80)
    print("✓ Synthetic data generation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
