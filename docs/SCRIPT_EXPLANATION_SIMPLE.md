# Script Explanation Summary (For Non-Python Experts)

## Quick 60-Second Overview

**What does `synthetic_data_generator_lite.py` do?**

Imagine you're a manager at a hospital pharmacy. You want to test a new inventory system before it goes live. But you can't use real patient data (privacy laws!). So instead, you use this script to create **fake but realistic pharmacy data** that mimics what real hospitals experience.

The script:
1. Creates 5 fake hospitals
2. Creates 25 fake medications
3. Simulates 1 year of operations (365 days)
4. Generates realistic patterns:
   - More medicine used in winter (flu season)
   - Medicines gradually expiring
   - Medicines being transferred between hospitals
   - Weather affecting demand
   - Disease outbreaks affecting demand

**Output:** 8 CSV files (like Excel spreadsheets) with ~209,000 rows of realistic data

---

## Understanding the Code Structure

### 1. **Imports** (Getting Your Tools)

```python
from datetime import datetime, timedelta    # Tools for working with dates
import random                                # Tool for generating random numbers
import os                                    # Tool for creating folders
import csv                                   # Tool for writing Excel-like files
```

**Real-world analogy:** This is like going to your toolbox and getting:
- A calendar (datetime)
- Dice (random)
- A folder creator (os)
- A spreadsheet writer (csv)

Before you start a task, you gather your tools!

---

### 2. **Configuration** (Your "Recipe Ingredients")

```python
FACILITIES = [
    {"id": "FAC001", "name": "Downtown Medical Center", ...},
    ...
]
```

**What this is:** A list of 5 hospitals with their names, locations, and storage capacity.

**Why?** The script needs to know "which hospitals exist?" before it can simulate them.

```python
MEDICATIONS = [
    {"id": "MED001", "name": "Lisinopril 10mg", "shelf_life_days": 1825},
    ...
]
```

**What this is:** A list of 25 real medications with their expiration timelines.

**Why?** The script needs to know "which drugs expire after how many days?" to create realistic inventory.

---

### 3. **The Main Function** (Your Recipe Instructions)

```python
def main():
    """Generate all synthetic data and export to CSV."""
```

**What this is:** A function is a container for code that does ONE job. This function's job: "Generate all synthetic data."

**Steps in main():**
1. Create output folder
2. Generate facilities CSV
3. Generate medications CSV
4. Generate inventory CSV
5. Generate consumption CSV
6. Generate transfers CSV
7. Generate external signals CSV
8. Generate demand forecast CSV
9. Generate replenishment orders CSV
10. Print summary

Think of it like a recipe: "Step 1: Preheat oven. Step 2: Mix ingredients. Step 3: Bake."

---

## Detailed Walkthrough: The Inventory Generation (Most Important!)

This is where the "Expiration Management" feature data comes from.

```python
for i in range(3000):
    # Step 1: Pick a random hospital and a random drug
    facility = random.choice(FACILITIES)
    medication = random.choice(MEDICATIONS)
```

**Translation:**
- Loop 3,000 times
- Each time: Pick a random hospital and a random drug
- Result: 3,000 combinations like (Downtown Medical + Lisinopril), (Northgate + Metformin), etc.

```python
    # Step 2: Calculate how many units they have
    base_qty = facility["capacity"] * random.uniform(0.05, 0.30) / len(MEDICATIONS)
    quantity_on_hand = max(int(base_qty * (1 + random.gauss(0, 0.3))), 10)
```

**Breaking it down:**

1. `facility["capacity"]` = hospital storage capacity
   - Example: Downtown Medical has 10,000 unit capacity
   
2. `random.uniform(0.05, 0.30)` = random percentage between 5-30%
   - Hospital doesn't keep all medications stocked
   - They keep 5-30% of their capacity filled with each type of medication

3. `/ len(MEDICATIONS)` = divide by 25 (number of drugs)
   - They have 25 different drugs
   - So each drug gets 1/25th of their stocked capacity
   
4. Example: 
   - Capacity = 10,000 units
   - Fill level = 20% (0.20)
   - Number of drugs = 25
   - Lisinopril gets: 10,000 × 0.20 ÷ 25 = 80 units

5. `random.gauss(0, 0.3)` = add realistic variation using a "bell curve"
   - Some drugs have more, some have less
   - Like: "We planned for 80 units, but actually have 95" (±30% variation)

6. `max(..., 10)` = ensure minimum of 10 units
   - Never show 0 units (hospitals always keep minimum stock)

```python
    # Step 3: Calculate when the medication was purchased and expires
    purchase_date = start_date + timedelta(days=random.randint(0, 365))
    expiration_date = purchase_date + timedelta(days=medication["shelf_life_days"])
    days_to_expiry = (expiration_date - datetime.now()).days
```

**Breaking it down:**

1. `purchase_date = start_date + timedelta(days=random.randint(0, 365))`
   - Pick a random day in the past 365 days
   - Example: "This batch was purchased 200 days ago"

2. `expiration_date = purchase_date + timedelta(days=medication["shelf_life_days"])`
   - Add the shelf life to purchase date = expiry date
   - Example: Purchased 200 days ago, shelf_life 1825 days → expires 1625 days from now

3. `days_to_expiry = (expiration_date - datetime.now()).days`
   - Calculate how many days until it expires
   - Negative number = already expired
   - Positive number = days remaining

```python
    # Step 4: Assign a risk level based on days remaining
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
```

**Translation:**
- `if / elif / else` = decision tree (like "If this, do that; else if that, do this; else do this")
- IF expired (0 or fewer days) → Risk = EXPIRED (throw it away!)
- ELSE IF critical (1-30 days) → Risk = CRITICAL (use ASAP or transfer)
- ELSE IF high (31-90 days) → Risk = HIGH (monitor closely)
- ELSE IF medium (91-180 days) → Risk = MEDIUM (normal monitoring)
- ELSE low (180+ days) → Risk = LOW (relax, it's fresh!)

```python
    # Step 5: Write this data to CSV file
    writer.writerow({
        "inventory_id": f"INV{i:06d}",
        "facility_id": facility["id"],
        "medication_id": medication["id"],
        ...
        "days_to_expiry": days_to_expiry,
        "risk_level": risk_level,
        ...
    })
```

**Translation:**
- `f"INV{i:06d}"` = create an ID: INV000001, INV000002, INV000003, etc.
- Write one row to CSV with all calculated values

---

## Detailed Walkthrough: The Consumption Generation (Demand Pattern)

This is where the "Demand Forecasting" feature data comes from.

```python
for day_offset in range(365):
    current_date = start_date + timedelta(days=day_offset)
    month = current_date.month
    seasonal_factor = 1.3 if month in [11, 12, 1, 2] else (1.0 if month in [3, 4, 9, 10] else 0.8)
```

**Breaking it down:**

1. Loop through all 365 days of the year

2. `month = current_date.month` 
   - Extract month number from date (1=Jan, 2=Feb, ... 12=Dec)

3. `seasonal_factor` = how much demand multiplies based on season
   ```
   IF month is Nov(11), Dec(12), Jan(1), Feb(2)  → seasonal_factor = 1.3  (winter is sick season)
   ELSE IF month is Mar(3), Apr(4), Sep(9), Oct(10) → seasonal_factor = 1.0 (transition)
   ELSE → seasonal_factor = 0.8  (summer is healthy season)
   ```

4. **Example:**
   - Normal daily consumption = 500 transactions
   - January (winter) → 500 × 1.3 = 650 transactions (30% more)
   - July (summer) → 500 × 0.8 = 400 transactions (20% less)

```python
    num_records = int(500 * seasonal_factor * random.uniform(0.8, 1.2))
    
    for _ in range(num_records):
        quantity = random.randint(1, 20)
        unit_price = round(random.uniform(2, 50), 2)
        
        writer.writerow({
            "transaction_id": f"TXN{tx_count:08d}",
            "facility_id": facility["id"],
            "medication_id": medication["id"],
            "transaction_date": current_date.date(),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_cost": round(quantity * unit_price, 2),
            ...
        })
```

**Breaking it down:**

1. `num_records = int(500 * seasonal_factor * random.uniform(0.8, 1.2))`
   - Base: 500 transactions per day
   - Apply seasonal factor (1.3x in winter, 0.8x in summer)
   - Add randomness: ±20% (random 0.8-1.2)
   - Result: realistic daily variation

2. For each transaction:
   - Pick random facility and medication
   - Quantity: 1-20 units (realistic per-prescription amount)
   - Price: $2-50 per unit (realistic drug prices)
   - Calculate total cost

3. **Result after 1 year:**
   - ~182,500 total transactions
   - More in winter months
   - Less in summer months
   - Realistic price variation

---

## Detailed Walkthrough: The External Signals

These help explain **WHY** demand spikes occur:

```python
weather_severity = "NORMAL"
if month in [12, 1] and random.random() < 0.3:
    weather_severity = random.choice(["COLD_WAVE", "SNOW"])
```

**Translation:**
- IF December or January AND (30% chance):
- THEN randomly pick either "COLD_WAVE" or "SNOW"
- Result: 30% of winter days have bad weather

```python
disease_signal = "NONE"
if random.random() < 0.1:
    disease_signal = random.choice(["FLU_SPIKE", "COVID_SURGE", "RSV_OUTBREAK", "NONE", "NONE"])
```

**Translation:**
- IF (10% chance):
- THEN randomly pick a disease (mostly NONE for realism)
- Result: ~36 days per year have a disease spike (realistic)

```python
demand_factor = 1.0
if weather_severity != "NORMAL":
    demand_factor = 1.2    # Bad weather = 20% more demand
elif disease_signal != "NONE":
    demand_factor = 1.3    # Disease = 30% more demand
```

**Translation:**
- Normal day → 1.0x demand (baseline)
- Bad weather → 1.2x demand (people get sick from cold)
- Disease outbreak → 1.3x demand (hospitals swamped)

---

## Why This Pattern Matters for Your Features

### Feature 1: Expiration Management
**Uses:** `inventory.csv` (risk_level column)
- You can find all "CRITICAL" items (expiring within 30 days)
- Agent recommends: Use in facility OR transfer to another hospital
- Power BI shows which medications to prioritize

### Feature 2: Multi-Facility Coordination
**Uses:** `inventory.csv` + `transfers.csv`
- Hospital A has 500 units of Drug X (way more than needed)
- Hospital B has 20 units of Drug X (running low)
- Matching engine suggests transfer A→B
- Transfer.csv logs: who sent what, when, status

### Feature 3: Demand Forecasting
**Uses:** `consumption.csv` + `external_signals.csv`
- ML model learns: "In January with flu spike, we use 40% more antibiotics"
- Model predicts: "Next January, expect 800 units" (with confidence interval)
- Output → `demand_forecast.csv`
- Hospital can proactively order more before shortage happens

### Feature 4: Decision Support (Power BI)
**Uses:** ALL 8 CSV files
- Dashboard 1: "Which medications are running low?" (inventory.csv)
- Dashboard 2: "Which are about to expire?" (inventory.csv + date math)
- Dashboard 3: "What's our forecast?" (demand_forecast.csv)
- Dashboard 4: "How successful are our transfers?" (transfers.csv + status)

---

## Common Questions

### Q: Why do we need synthetic data? Why not use real hospital data?

**A:** 
1. **Privacy:** Real patient data is protected by HIPAA laws (healthcare privacy law)
2. **Speed:** Real data takes months to collect; synthetic takes seconds
3. **Testing:** We can adjust scenarios to test edge cases (e.g., "What if we had 10x demand?")
4. **Safety:** Testing on fake data before deploying to real systems

### Q: Why are the numbers so realistic?

**A:** 
The script uses:
- **Seasonal patterns** (winter flu, summer calm)
- **Random variation** (bell curves, not flat)
- **Capacity constraints** (hospitals can't stock more than space allows)
- **Real medications** (actual drug names from pharmacies)
- **Real shelf lives** (actual expiration times)

Result: Looks like real hospital data!

### Q: What's a "risk_level" and why does it matter?

**A:**
```
EXPIRED    = 0 days left    → DESTROY immediately (regulatory requirement)
CRITICAL   = 1-30 days      → Use ASAP or transfer (URGENT)
HIGH       = 31-90 days     → Monitor closely (consider transfers)
MEDIUM     = 91-180 days    → Normal inventory (no action needed)
LOW        = 180+ days      → Fresh, no concerns (optimal)
```

Your agent uses this to automatically:
- Generate alerts for CRITICAL/EXPIRED
- Suggest transfers to hospitals with upcoming shortages
- Prevent waste (save money)
- Ensure patients get medicine (avoid shortages)

### Q: What's a "confidence interval" in the forecast?

**A:**
If we predict "150 units" with a 120-180 confidence interval:
- We're 80% confident demand will be between 120-180 units
- So hospital should stock 180 units (cover upper bound, be safe)
- If we only stocked 120, we risk stockouts if demand spikes

### Q: How is this used in Power BI?

**A:**
1. Import all 8 CSV files into Power BI
2. Power BI creates relationships between them (joins them)
3. Create visualizations:
   - Chart: Inventory by facility (donut chart)
   - Chart: Expiration risk (bar chart)
   - Chart: Forecast vs actual (line chart)
   - Table: Transfer recommendations (sortable table)
4. Add interactivity:
   - Click on a facility → see only its data
   - Click on a drug → see its timeline
5. Result: Pharmacists make better decisions faster!

---

## Key Takeaways

| Concept | Simple Explanation |
|---------|-------------------|
| **Synthetic Data** | Fake but realistic data for testing before using real data |
| **CSV File** | Like an Excel spreadsheet (rows and columns) |
| **Facility** | A hospital or clinic (5 in our data) |
| **Medication** | A drug (25 in our data) |
| **Inventory** | How much of each drug is at each facility right now |
| **Consumption** | How much of each drug was used each day (history) |
| **Transfer** | Moving a drug from one hospital to another |
| **Risk Level** | How urgent the medication's expiration is (LOW to EXPIRED) |
| **Seasonal Factor** | Multiplier for demand based on season (1.3x in winter, 0.8x in summer) |
| **Forecast** | Prediction of how much drug we'll need in the future |
| **External Signal** | Real-world event that affects demand (weather, disease, etc.) |

---

## Next Steps

1. **Run the script** to generate the 8 CSV files
2. **Open one CSV in Excel** to see the data structure
3. **Use CSVs in Power BI** to create dashboards
4. **Use CSVs in Python** to train ML models (demand forecasting)
5. **Use CSVs in agents** to build expiration management & transfer matching logic

Now you're ready to build the 4 features! 🎯

