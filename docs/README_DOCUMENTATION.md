# Synthetic Data Generation - Complete Documentation Index

## 📚 Documentation Files (Read in This Order)

### For Complete Beginners (No Python Experience)

1. **START HERE:** [`SCRIPT_EXPLANATION_SIMPLE.md`](SCRIPT_EXPLANATION_SIMPLE.md)
   - ✅ 60-second overview
   - ✅ Line-by-line explanation with real-world analogies
   - ✅ Common questions answered
   - ✅ Key concepts defined
   - **Time to read:** 20-30 minutes

2. **THEN READ:** [`DATA_FLOW_DIAGRAMS.md`](DATA_FLOW_DIAGRAMS.md)
   - ✅ Visual ASCII diagrams (no code, just flow)
   - ✅ Table structure explained
   - ✅ How each CSV file relates to the 4 features
   - ✅ Data generation process flow
   - **Time to read:** 15-20 minutes

3. **FINALLY:** [`BEGINNER_GUIDE.md`](BEGINNER_GUIDE.md)
   - ✅ Comprehensive section-by-section breakdown
   - ✅ Python concept explanations
   - ✅ Example outputs shown
   - ✅ Troubleshooting guide
   - ✅ Customization tips
   - **Time to read:** 30-40 minutes

---

### For Developers / Data Engineers

- **Quick Reference:** [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) (if exists)
- **Data Schema:** [`DATA_SCHEMA.md`](DATA_SCHEMA.md) (if exists)
- **Source Code:** [`synthetic_data_generator_lite.py`](synthetic_data_generator_lite.py)

---

## 📊 Generated Output Files

After running the script, you'll find these CSV files in `./synthetic_data/`:

| File | Rows | Purpose | Feature |
|------|------|---------|---------|
| **facilities.csv** | 5 | Hospital/clinic reference | Multi-Facility Coordination |
| **medications.csv** | 25 | Drug master data | All Features |
| **inventory.csv** | 3,000 | Current stock + expiration | Expiration Management + Decision Support |
| **consumption.csv** | ~182,500 | Daily usage history | Demand Forecasting |
| **transfers.csv** | 500 | Inter-facility movements | Multi-Facility Coordination |
| **external_signals.csv** | 365 | Weather, disease, events | Demand Forecasting |
| **demand_forecast.csv** | ~22,500 | Predicted future demand | Decision Support |
| **replenishment_orders.csv** | 200 | Supplier orders | Expiration Management + Decision Support |

**Total:** ~209,000 data rows

---

## 🎯 The 4 Features This Data Supports

### Feature 1: Expiration Management (Agentic AI)
- **Primary Data:** `inventory.csv` (risk_level column)
- **Agent Logic:** 
  1. Read inventory.csv
  2. Filter WHERE risk_level IN ('EXPIRED', 'CRITICAL')
  3. Recommend action: Use ASAP, Transfer, or Destroy
  4. Output recommendation to Power BI + trigger alerts
- **Success Metric:** % of near-expiry items successfully redistributed

### Feature 2: Multi-Facility Coordination / Transfer Matching
- **Primary Data:** `inventory.csv` + `transfers.csv`
- **Matching Logic:**
  1. Find excess (current > reorder * 2)
  2. Find shortages (current < reorder)
  3. Score matches: distance + urgency + capacity
  4. Create transfer recommendations
- **Success Metric:** Cost saved from prevented waste

### Feature 3: Demand Forecasting (ML)
- **Primary Data:** `consumption.csv` + `external_signals.csv`
- **ML Logic:**
  1. Train model on consumption history (182K rows)
  2. Factor in seasonality, weather, disease
  3. Forecast 90 days forward
  4. Validate against actual (prevent over-stocking)
- **Success Metric:** MAE (Mean Absolute Error) < target threshold

### Feature 4: Decision Support Analytics (Power BI)
- **All Data:** All 8 CSV files
- **Dashboards:**
  1. Inventory status by facility/category
  2. Expiration risk heat map
  3. Demand forecast vs actual
  4. Transfer success rate
  5. Supply chain health metrics
- **Success Metric:** Time to insight reduced

---

## 🚀 Quick Start

### Step 1: Run the Generator
```bash
cd "c:\Users\kadec\Documents\Interview prep\Capstone Project\pharma-inventory-platform\data-generation"
python synthetic_data_generator_lite.py
```

### Step 2: Check Output
```bash
ls synthetic_data/
# Should see 8 CSV files created
```

### Step 3: Verify Data
```bash
# Open in Excel or:
head -5 synthetic_data/inventory.csv
```

### Step 4: Next Steps
- **For agents:** Read inventory.csv and transfers.csv
- **For ML:** Read consumption.csv + external_signals.csv → demand_forecast.csv
- **For Power BI:** Import all 8 CSVs into Power BI Desktop
- **For validation:** Compare your forecasts to demand_forecast.csv

---

## 📖 How to Read Each Documentation File

### SCRIPT_EXPLANATION_SIMPLE.md

**Best for:** Understanding what the code does without reading code

**Sections:**
1. Quick 60-second overview
2. Code structure (imports, config, main function)
3. Detailed walkthrough of 4 key sections:
   - Inventory generation (most complex)
   - Consumption generation (seasonal patterns)
   - External signals (real-world context)
   - Each explained with real-world analogies
4. How each section connects to the 4 features
5. Common questions answered
6. Key concepts with definitions

**Key Learning:** Understand the LOGIC, not the syntax

---

### DATA_FLOW_DIAGRAMS.md

**Best for:** Seeing how data flows through the system

**Sections:**
1. High-level generation flow diagram
2. Table structure diagrams for each CSV:
   - Column names
   - Example data
   - Risk calculations
   - Matching logic
3. Complete data relationship diagram
4. Feature mapping (which CSV feeds which feature)
5. Detailed process flow (step-by-step)
6. Quick reference: "Which CSV to use for which question?"

**Key Learning:** Data structures and relationships

---

### BEGINNER_GUIDE.md

**Best for:** Deep dive into each line of code

**Sections:**
1. What does this script do? (high-level)
2. Concept: What is synthetic data?
3. Line-by-line breakdown:
   - Imports and what each does
   - Configuration data (facilities, medications)
   - Main function structure
   - Each of 8 CSV generation steps
4. Summary table: What each CSV file does
5. How to run the script
6. Python concepts explained (lists, dicts, loops, etc.)
7. Customization tips
8. Troubleshooting
9. Questions answered

**Key Learning:** Complete understanding of every piece

---

## 🔄 Learning Path Recommendation

### Path A: "I want to understand code"
1. Read: SCRIPT_EXPLANATION_SIMPLE.md (30 min)
2. Read: BEGINNER_GUIDE.md (40 min)
3. Read: Source code line-by-line (20 min)
4. Run: The script yourself (5 min)
5. Experiment: Modify a few parameters and re-run

### Path B: "I want to build features immediately"
1. Skim: SCRIPT_EXPLANATION_SIMPLE.md (5 min)
2. Read: DATA_FLOW_DIAGRAMS.md (10 min)
3. Run: The script (5 min)
4. Import: CSVs into Power BI (10 min)
5. Start: Building feature logic

### Path C: "I need the data RIGHT NOW"
1. Run: The script (5 min)
2. Check: Output files exist (1 min)
3. Import: Into Power BI or Python (5 min)
4. Reference: DATA_FLOW_DIAGRAMS.md when you need details

---

## 🎓 Python Concepts Used (Explained Simply)

### Imports
```python
from datetime import datetime, timedelta
import random
```
**Simple explanation:** Borrowing tools you'll use later

### Lists (Arrays)
```python
FACILITIES = [item1, item2, item3]
for facility in FACILITIES:
    print(facility)
```
**Simple explanation:** A collection of items you can loop through

### Dictionaries (Maps)
```python
facility = {"id": "FAC001", "name": "Downtown Medical"}
print(facility["id"])  # Outputs: FAC001
```
**Simple explanation:** A labeled box where you access items by name, not position

### Random
```python
random.choice(FACILITIES)        # Pick random item
random.randint(1, 100)           # Random number 1-100
random.uniform(0.8, 1.2)         # Random decimal
random.gauss(0, 0.3)             # Bell curve distribution
```
**Simple explanation:** Different ways to generate randomness for realism

### Loops
```python
for i in range(5):               # Repeat 5 times: 0,1,2,3,4
    print(i)

for facility in FACILITIES:      # Repeat once for each facility
    print(facility["name"])
```
**Simple explanation:** "Do this thing X times" or "Do this for each item"

### Conditionals (Decision Trees)
```python
if days_to_expiry <= 0:
    risk = "EXPIRED"
elif days_to_expiry <= 30:
    risk = "CRITICAL"
else:
    risk = "LOW"
```
**Simple explanation:** If/else logic: "If X, do A. Else if Y, do B. Else do C."

### Date/Time
```python
from datetime import datetime, timedelta
today = datetime.now()
tomorrow = today + timedelta(days=1)
```
**Simple explanation:** Adding/subtracting dates like math: 2025-01-01 + 5 days = 2025-01-06

### CSV Writing
```python
with open("file.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["col1", "col2"])
    writer.writeheader()
    writer.writerow({"col1": "value1", "col2": "value2"})
```
**Simple explanation:** 
1. Open file
2. Set up columns
3. Write header row
4. Write data rows
5. Close file (automatic with `with`)

---

## ⚡ Common Use Cases After Generation

### "I need to find expiring drugs"
```
Query: SELECT * FROM inventory WHERE days_to_expiry <= 30 ORDER BY days_to_expiry ASC
Files: inventory.csv
```

### "I need to match surplus with shortage"
```
Logic:
  1. Read inventory.csv
  2. Group by facility + medication
  3. Find surplus: qty > reorder_level * 2
  4. Find shortage: qty < reorder_level
  5. Create matches
Files: inventory.csv → transfers.csv
```

### "I need to forecast next week's demand"
```
Logic:
  1. Read consumption.csv (182K rows of history)
  2. Read external_signals.csv (weather, disease)
  3. Train ML model (Prophet/ARIMA)
  4. Predict next 7 days
  5. Compare to demand_forecast.csv
Files: consumption.csv + external_signals.csv → demand_forecast.csv
```

### "I need a Power BI dashboard"
```
Steps:
  1. Import all 8 CSV files
  2. Create relationships (facility_id, medication_id)
  3. Add measures:
     - Count items by risk level
     - Sum cost by facility
     - AVG shelf life remaining
  4. Create visuals (charts, tables, gauges)
  5. Add interactivity (slicers)
Files: ALL CSV files
```

---

## 🔧 Troubleshooting

| Problem | Solution | Doc Reference |
|---------|----------|---|
| "Where do I start?" | Read SCRIPT_EXPLANATION_SIMPLE.md | SCRIPT_EXPLANATION_SIMPLE.md |
| "How do I understand the data?" | Read DATA_FLOW_DIAGRAMS.md | DATA_FLOW_DIAGRAMS.md |
| "What does line X do?" | Read BEGINNER_GUIDE.md section for that part | BEGINNER_GUIDE.md |
| "Script won't run" | Check troubleshooting in BEGINNER_GUIDE.md | BEGINNER_GUIDE.md → Troubleshooting |
| "Data doesn't look right" | Numbers are meant to be realistic, read BEGINNER_GUIDE.md → Customization Tips | BEGINNER_GUIDE.md → Customization |
| "I want to change the data" | Read BEGINNER_GUIDE.md → Customization Tips | BEGINNER_GUIDE.md → Customization Tips |

---

## 📞 Questions?

### "I'm brand new to Python"
→ Read: SCRIPT_EXPLANATION_SIMPLE.md → Python Concepts Explained section

### "I need to understand the data structure"
→ Read: DATA_FLOW_DIAGRAMS.md → Table Structure sections

### "I need to modify the generator"
→ Read: BEGINNER_GUIDE.md → Customization Tips

### "I want to build a feature"
→ Read: DATA_FLOW_DIAGRAMS.md → Feature Mapping section

---

## 📋 File Checklist

After running the script, verify you have:

- ✅ `synthetic_data/facilities.csv` (5 rows)
- ✅ `synthetic_data/medications.csv` (25 rows)
- ✅ `synthetic_data/inventory.csv` (3,000 rows)
- ✅ `synthetic_data/consumption.csv` (~182,500 rows)
- ✅ `synthetic_data/transfers.csv` (500 rows)
- ✅ `synthetic_data/external_signals.csv` (365 rows)
- ✅ `synthetic_data/demand_forecast.csv` (~22,500 rows)
- ✅ `synthetic_data/replenishment_orders.csv` (200 rows)

**Total:** ~209,000 rows of realistic pharmaceutical inventory data

---

## 🎯 Success Criteria

You've successfully understood this synthetic data generator when you can:

- [ ] Explain what synthetic data is (and why we use it)
- [ ] Describe the 4 features and which CSV each uses
- [ ] Explain how risk_level is calculated
- [ ] Describe seasonal demand patterns
- [ ] Run the script and verify output
- [ ] Identify a record in inventory.csv as CRITICAL expiration risk
- [ ] Identify a matching opportunity (surplus + shortage)
- [ ] Explain how external signals affect demand
- [ ] Describe how to use this data in Power BI
- [ ] Describe how to use this data for ML forecasting

---

## 🚀 Next Steps After Understanding

1. **Run the generator:** Generate the 8 CSV files
2. **Explore data:** Open CSVs in Excel to see structure
3. **Import to Power BI:** Start building dashboards
4. **Build Feature 1:** Expiration Management agent
5. **Build Feature 2:** Transfer Matching engine
6. **Build Feature 3:** Demand Forecasting ML models
7. **Build Feature 4:** Decision Support dashboards

---

**Last Updated:** February 1, 2026
**Total Documentation:** 4 markdown files + 1 Python script
**Total Data Generated:** ~209,000 rows across 8 CSV files
**Estimated Read Time:** 60-90 minutes for complete understanding

