# Synthetic Data Generator - Beginner's Guide (No Python Experience Needed!)

## What Does This Script Do?

Think of this script as a **factory that creates fake but realistic pharmacy data**. Instead of waiting for a real hospital to give us data (which could take months), we generate it instantly. This fake data is perfect for testing the 4 features we're building.

---

## Key Concept: What is "Synthetic Data"?

Imagine you're building a restaurant reservation system. Instead of waiting for real customers, you generate 1,000 fake reservations with realistic names, times, and preferences. That's synthetic data!

**Benefits:**
- ✅ Fast (no waiting for real data)
- ✅ Safe (no privacy/regulatory concerns)
- ✅ Realistic (follows real-world patterns)
- ✅ Repeatable (same data every time we run it)

---

## Breaking Down the Script Line-by-Line

### Part 1: Imports (Lines 1-8)

```python
from datetime import datetime, timedelta
import random
import os
import csv
```

**What this means:**
- `from datetime import datetime, timedelta` → Tools to work with dates and times
- `import random` → Generates random numbers (like rolling a dice)
- `import os` → Creates folders and manages files
- `import csv` → Writes data to CSV files (spreadsheet format)

**Real-world analogy:** These are like borrowing tools from a toolbox before starting a job.

---

### Part 2: Configuration - The Base Data (Lines 11-66)

#### Facilities (Lines 18-23)

```python
FACILITIES = [
    {"id": "FAC001", "name": "Downtown Medical Center", "city": "Seattle", ...},
    {"id": "FAC002", "name": "Northgate Community Hospital", "city": "Seattle", ...},
    ...
]
```

**What this is:**
- A **list** of 5 hospitals/clinics
- Each facility has: ID, name, city, state, storage capacity

**Why it matters for our 4 features:**
- **Multi-Facility Coordination:** We need multiple facilities to transfer drugs between
- **Decision Support:** Dashboards will show data per facility

**CSV output looks like:**
```
id,name,city,state,capacity
FAC001,Downtown Medical Center,Seattle,WA,10000
FAC002,Northgate Community Hospital,Seattle,WA,5000
```

---

#### Medications (Lines 25-52)

```python
MEDICATIONS = [
    {"id": "MED001", "name": "Lisinopril 10mg", "category": "Cardiovascular", "shelf_life_days": 1825},
    ...
]
```

**What this is:**
- A **list** of 25 real drugs with:
  - ID (unique identifier)
  - Name (drug name + dosage)
  - Category (type of drug)
  - Shelf life (how long before expiry, in days)

**Why it matters for our 4 features:**
- **Expiration Management:** We need shelf_life to calculate when drugs expire
- **Demand Forecasting:** We track which drugs are used most
- **Transfer Matching:** We recommend transfers based on availability

**Example shelf life:**
- `1825 days` = ~5 years (stable drugs like Lisinopril)
- `365 days` = 1 year (sensitive drugs like Insulin)
- `730 days` = ~2 years (antibiotics)

---

### Part 3: The Main Function (Lines 67+)

```python
def main():
    output_dir = "synthetic_data"
    os.makedirs(output_dir, exist_ok=True)
```

**What this means:**
- `def main():` → Defines a function (a block of code that does something)
- Creates a folder called `synthetic_data` to store all CSV files
- `exist_ok=True` → Don't fail if folder already exists

---

### Part 4: Generate Facilities CSV (Lines 76-90)

```python
with open(f"{output_dir}/facilities.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[...])
    writer.writeheader()
    for fac in FACILITIES:
        writer.writerow({...})
```

**Step-by-step translation:**

1. **`with open(...)`** → Open a file for writing (like opening a blank Excel file)
   - `"w"` = write mode
   - `newline=""` = don't add extra blank lines

2. **`csv.DictWriter(f, fieldnames=[...])`** → Create a CSV writer that knows the column headers
   - Like saying "this CSV has columns: id, name, city, state, capacity"

3. **`writer.writeheader()`** → Write the first row with column names
   - Output: `id,name,city,state,capacity,created_date,last_updated`

4. **`for fac in FACILITIES:`** → Loop through each facility
   - Repeat steps 5 for each facility

5. **`writer.writerow({...})`** → Write one row of data
   - Example output: `FAC001,Downtown Medical Center,Seattle,WA,10000,2026-02-01T10:30:00,2026-02-01T10:30:00`

---

### Part 5: Generate Inventory CSV (Lines 93-142)

**This is the most important file for Expiration Management!**

```python
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
    ...
```

**Breaking it down:**

1. **`for i in range(3000):`** → Create 3,000 inventory batches (simulating different shipments)

2. **`facility = random.choice(FACILITIES)`** → Pick a random facility
   - Like: "This batch is at Downtown Medical Center"

3. **`medication = random.choice(MEDICATIONS)`** → Pick a random drug
   - Like: "This batch is Lisinopril 10mg"

4. **`quantity_on_hand = ...`** → Calculate realistic stock levels
   - Uses facility capacity and random variation
   - Ensures at least 10 units per batch

5. **`purchase_date = start_date + timedelta(...)`** → Random purchase date in past year
   - Example: "This batch was purchased 200 days ago"

6. **`expiration_date = purchase_date + timedelta(...)`** → Calculate when it expires
   - Example: If purchased 200 days ago and shelf_life is 1825 days → expires in ~1625 days

7. **`days_to_expiry = ...`** → Days until expiration (negative = already expired)

8. **Risk level calculation:**
   ```
   EXPIRED   → 0 or fewer days left (CRITICAL!)
   CRITICAL  → 1-30 days left (needs immediate action)
   HIGH      → 31-90 days left (close attention needed)
   MEDIUM    → 91-180 days left (monitor)
   LOW       → 180+ days left (no concern)
   ```

**Example output row:**
```
INV000001, FAC001, MED001, BATCH123456, 500, 125, 2025-06-01, 2030-05-31, 1217, LOW, SHELF_5, 2025-06-05, 2026-02-01T10:30:00
```

Translation:
- Inventory ID: INV000001
- At facility: FAC001 (Downtown Medical)
- Drug: MED001 (Lisinopril)
- Batch: BATCH123456
- Currently have: 500 units
- Reorder when below: 125 units
- Purchased: June 1, 2025
- Expires: May 31, 2030
- Days until expiry: 1217
- Risk: LOW
- Stored at: SHELF_5

---

### Part 6: Generate Consumption CSV (Lines 145-185)

**This is for Demand Forecasting!**

```python
for day_offset in range(365):
    current_date = start_date + timedelta(days=day_offset)
    month = current_date.month
    seasonal_factor = 1.3 if month in [11, 12, 1, 2] else (1.0 if month in [3, 4, 9, 10] else 0.8)
    num_records = int(500 * seasonal_factor * random.uniform(0.8, 1.2))
```

**What this does:**
- Loops through every day of the past year
- Calculates **seasonal demand** (more pills used in winter, fewer in summer)
  - Winter (Nov-Feb): 1.3x normal demand (people get sick)
  - Spring/Fall (Mar-Apr, Sep-Oct): 1.0x normal
  - Summer (May-Aug): 0.8x normal (healthier people)
- Adds random variation: `uniform(0.8, 1.2)` = 80% to 120% randomness

**Example output row:**
```
TXN00000001, FAC001, MED001, 2025-06-15, CONSUMPTION, 10, 15.50, 155.00, ICU, DOC234, 2026-02-01T10:30:00
```

Translation:
- Transaction: TXN00000001
- At facility: FAC001
- Drug: MED001
- Date: June 15, 2025
- Type: CONSUMPTION (drug used/dispensed)
- Quantity: 10 units
- Price per unit: $15.50
- Total cost: $155.00
- Department: ICU (Intensive Care Unit)
- Prescriber: DOC234
- Created: February 1, 2026

---

### Part 7: Generate Transfers CSV (Lines 188-224)

**This is for Multi-Facility Coordination!**

```python
for i in range(500):
    source_facility = random.choice(FACILITIES)
    target_facility = random.choice([f for f in FACILITIES if f["id"] != source_facility["id"]])
    medication = random.choice(MEDICATIONS)
    
    transfer_date = start_date + timedelta(days=random.randint(0, 180))
    received_date = transfer_date + timedelta(days=random.randint(1, 5))
    transfer_status = random.choice(["COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "REJECTED"])
```

**What this does:**
- Creates 500 transfer records (medication moving between facilities)
- `target_facility = random.choice([f for f in FACILITIES if f["id"] != source_facility["id"]])` 
  - Pick a different facility (can't transfer to yourself!)
- Transfer statuses: mostly COMPLETED, some PENDING or REJECTED (realistic distribution)

**Example output row:**
```
TRF000001, FAC001, FAC002, MED001, 200, 200, 2025-09-01, 2025-09-04, COMPLETED, Shortage Prevention, 15.3, 250.00, 2026-02-01T10:30:00
```

Translation:
- Transfer ID: TRF000001
- From: FAC001 (Downtown Medical)
- To: FAC002 (Northgate Hospital)
- Drug: MED001
- Requested: 200 units
- Actually transferred: 200 units
- Requested on: Sept 1, 2025
- Received: Sept 4, 2025
- Status: COMPLETED (successful)
- Reason: Shortage Prevention (FAC002 was running low)
- Distance: 15.3 miles
- Cost: $250.00

---

### Part 8: Generate External Signals CSV (Lines 227-269)

**This improves Demand Forecasting!**

```python
weather_severity = "NORMAL"
if month in [12, 1] and random.random() < 0.3:
    weather_severity = random.choice(["COLD_WAVE", "SNOW"])

disease_signal = "NONE"
if random.random() < 0.1:
    disease_signal = random.choice(["FLU_SPIKE", "COVID_SURGE", "RSV_OUTBREAK"])
```

**What this does:**
- Adds real-world context that affects drug demand:
  - Cold waves in winter → more respiratory infections → more antibiotic use
  - Flu spikes → more pain medication, antibiotics
  - Hospital events → affects demand

**Example output row:**
```
2025-11-15, SUNNY, NORMAL, NONE, NONE, 1.0, 2026-02-01T10:30:00
2025-12-20, SNOW, COLD_WAVE, NONE, NONE, 1.2, 2026-02-01T10:30:00
2026-01-10, SUNNY, NORMAL, FLU_SPIKE, NONE, 1.3, 2026-02-01T10:30:00
```

Translation:
- Row 1: Normal day → normal demand (1.0x)
- Row 2: Cold wave in December → 1.2x demand spike
- Row 3: Flu spike in January → 1.3x demand spike

---

### Part 9: Generate Demand Forecast CSV (Lines 272-306)

**This is for Decision Support Analytics!**

```python
for day_offset in range(90):
    forecast_date = current_date + timedelta(days=day_offset)
    month = forecast_date.month
    seasonal_factor = 1.3 if month in [11, 12, 1, 2] else 1.0
    
    for facility in FACILITIES:
        for medication in MEDICATIONS[:10]:
            base_demand = random.randint(50, 200)
            forecast_qty = int(base_demand * seasonal_factor)
```

**What this does:**
- Creates 90-day forward forecasts (next 3 months)
- For each facility + drug combination:
  - Base demand: 50-200 units
  - Adjusts for seasonality
  - Calculates confidence interval (uncertainty range)

**Example output row:**
```
FCT00000001, FAC001, MED001, 2026-02-05, 150, 120, 180, Prophet, 2026-02-01T10:30:00
```

Translation:
- Forecast ID: FCT00000001
- For facility: FAC001
- For drug: MED001
- On date: Feb 5, 2026
- **Predicted demand: 150 units**
- Confidence range: 120-180 units (we're 80% confident demand will be between these)
- Method: Prophet (popular forecasting algorithm)

---

### Part 10: Generate Replenishment Orders CSV (Lines 309-338)

**This supports all 4 features!**

```python
for i in range(200):
    facility = random.choice(FACILITIES)
    medication = random.choice(MEDICATIONS)
    
    order_date = start_date + timedelta(days=random.randint(0, 90))
    delivery_date = order_date + timedelta(days=random.randint(2, 10))
    order_status = random.choice(["DELIVERED", "DELIVERED", "DELIVERED", "PENDING", "CANCELLED"])
```

**What this does:**
- Creates 200 supplier orders (buying more drugs)
- Most orders are delivered (3x) vs pending (1x) vs cancelled (1x)
- Delivery takes 2-10 days

**Example output row:**
```
ORD000001, FAC001, MED001, 2025-08-10, 2025-08-15, 500, 18.75, DELIVERED, SUP01, 2026-02-01T10:30:00
```

Translation:
- Order ID: ORD000001
- For facility: FAC001
- For drug: MED001
- Ordered: Aug 10, 2025
- Delivered: Aug 15, 2025 (5 days)
- Quantity: 500 units
- Cost per unit: $18.75
- Status: DELIVERED
- Supplier: SUP01

---

## Summary: What Each CSV File Does

| File | Rows | Purpose | For Which Feature |
|------|------|---------|------------------|
| **facilities.csv** | 5 | Hospital/clinic reference data | Multi-Facility Coordination |
| **medications.csv** | 25 | Drug master data | All features |
| **inventory.csv** | 3,000 | Current stock with expiry dates | Expiration Management + Decision Support |
| **consumption.csv** | ~182,500 | Daily drug usage history | Demand Forecasting |
| **transfers.csv** | 500 | Inter-facility drug movements | Multi-Facility Coordination |
| **external_signals.csv** | 365 | Weather, disease, events | Demand Forecasting |
| **demand_forecast.csv** | ~22,500 | Predicted future demand (90 days) | Decision Support Analytics |
| **replenishment_orders.csv** | 200 | Supplier orders | Expiration Management + Decision Support |

---

## How to Run This Script

### Option 1: From Command Line
```bash
cd "c:\Users\kadec\Documents\Interview prep\Capstone Project\pharma-inventory-platform\data-generation"
python synthetic_data_generator_lite.py
```

### Option 2: From VS Code
1. Open the file `synthetic_data_generator_lite.py`
2. Click the ▶️ (Run) button in top right
3. Check the `synthetic_data/` folder for CSV files

### What You'll See
```
================================================================================
PHARMACEUTICAL INVENTORY SYNTHETIC DATA GENERATOR
================================================================================

[1/8] Generating Facilities data...
    ✓ Generated 5 facility records
[2/8] Generating Medications data...
    ✓ Generated 25 medication records
[3/8] Generating Inventory data (Expiration Management)...
    ✓ Generated 3000 inventory batch records
    Risk distribution: {'EXPIRED': 42, 'CRITICAL': 156, 'HIGH': 298, 'MEDIUM': 1124, 'LOW': 1380}
...
[8/8] Generating Replenishment Orders data...
    ✓ Generated 200 replenishment order records

================================================================================
✓ Synthetic data generation complete!
================================================================================
```

---

## Next Steps: Using This Data

### 1. Expiration Management Feature
- Read `inventory.csv`
- Filter where `risk_level` IN ('EXPIRED', 'CRITICAL')
- Agent recommends: urgent use or transfer to facility that needs it

### 2. Multi-Facility Coordination
- Read `inventory.csv` and `transfers.csv`
- Calculate which facilities have excess (beyond reorder_level)
- Match excess at Facility A with shortages at Facility B
- Create transfer recommendation

### 3. Demand Forecasting
- Read `consumption.csv` and `external_signals.csv`
- Train ML model (Prophet or ARIMA) on consumption history
- Factor in external signals (weather, disease)
- Validate against `demand_forecast.csv`

### 4. Decision Support (Power BI)
- Import all CSVs into Power BI
- Create dashboard with:
  - Current inventory by facility
  - Expiration risk gauge
  - Forecast vs actual consumption
  - Transfer recommendations

---

## Python Concepts Explained

### Lists (Arrays)
```python
FACILITIES = [item1, item2, item3]
facility = FACILITIES[0]  # First item
for fac in FACILITIES:    # Loop through
    print(fac)
```

### Dictionaries (Maps)
```python
facility = {"id": "FAC001", "name": "Downtown Medical"}
print(facility["id"])      # Access by key
print(facility["name"])
```

### Random
```python
random.choice(FACILITIES)        # Pick random item from list
random.randint(1, 100)           # Random number between 1-100
random.uniform(0.8, 1.2)         # Random decimal between 0.8-1.2
random.gauss(0, 0.3)             # Normal distribution (bell curve)
```

### Date/Time
```python
from datetime import datetime, timedelta

today = datetime.now()                                    # Current date/time
yesterday = today - timedelta(days=1)                    # 1 day ago
next_week = today + timedelta(days=7)                    # 7 days from now
days_until = (future_date - today).days                  # Number of days
```

### Loops
```python
for i in range(5):                        # Loop 0,1,2,3,4
    print(i)

for facility in FACILITIES:               # Loop through each facility
    print(facility["name"])
```

### Conditionals
```python
if days_to_expiry <= 0:
    risk_level = "EXPIRED"
elif days_to_expiry <= 30:
    risk_level = "CRITICAL"
else:
    risk_level = "LOW"
```

---

## Troubleshooting

### "Module not found: csv, datetime, random"
**Solution:** These are built-in Python modules. No installation needed!

### "No output_dir specified"
**Solution:** The script creates `synthetic_data/` folder automatically

### "File already exists"
**Solution:** Script overwrites old files (that's okay for testing)

### "Numbers look unrealistic"
**Solution:** That's fine! Synthetic data should look realistic but doesn't need to be perfect. Adjust the random ranges if needed.

---

## Customization Tips

### Change number of records
```python
# Line 104: Change 3000 to 5000
for i in range(5000):
```

### Change time period
```python
# Line 100: Change 365 to 730 (2 years of data)
for day_offset in range(730):
```

### Change facility capacity
```python
# Line 20: Modify capacity values
{"id": "FAC001", "name": "...", "capacity": 50000},  # Increased
```

### Add more medications
```python
# Add to MEDICATIONS list
{"id": "MED026", "name": "New Drug Name", "category": "...", "shelf_life_days": 1825},
```

---

## Questions?

This script demonstrates:
✅ Real-world data patterns (seasonality, randomness)
✅ Relationships between tables (facility → inventory → consumption)
✅ Risk calculations (expiration management)
✅ Time series data (historical + forecast)
✅ Multi-facility coordination patterns

All 8 CSV files are ready for your agents, ML models, and Power BI dashboards!

