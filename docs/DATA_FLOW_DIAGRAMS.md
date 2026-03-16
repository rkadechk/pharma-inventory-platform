# Data Flow Diagrams - Visual Guide

## 1. High-Level Data Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│     SYNTHETIC DATA GENERATOR (synthetic_data_generator.py)   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ┌────────┐          ┌───────┐          ┌──────────┐
    │ CONFIG │          │ LOGIC │          │ RANDOMNESS
    │        │          │       │          │
    │• Facil-│          │ Risk  │          │• Random  
    │ities  │ ────────▶│ Calc  │ ────────▶│ numbers
    │• Meds │          │       │          │• Normal
    │        │          │ Date  │          │ curves
    └────────┘          │ Calc  │          │• Choices
                        │       │          └──────────┘
                        └───────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   8 CSV FILES   │
                    │                 │
                    │• Facilities     │
                    │• Medications    │
                    │• Inventory      │
                    │• Consumption    │
                    │• Transfers      │
                    │• Ext. Signals   │
                    │• Forecast       │
                    │• Orders         │
                    └─────────────────┘
```

---

## 2. Inventory Table Structure (Expiration Management)

```
INVENTORY.CSV
═════════════════════════════════════════════════════════════════

inventory_id    facility_id    medication_id    batch_number    quantity_on_hand
─────────────   ───────────    ─────────────    ────────────    ────────────────
INV000001       FAC001         MED001           BATCH123456     500
INV000002       FAC001         MED002           BATCH123457     320
INV000003       FAC002         MED001           BATCH123458     50
...

reorder_level   purchase_date   expiration_date   days_to_expiry   risk_level
─────────────   ─────────────   ───────────────   ──────────────   ──────────
125             2025-06-01      2030-05-31        1217             LOW
80              2025-08-15      2028-08-14        915              LOW
10              2025-11-10      2026-11-09        313              MEDIUM
...

storage_location   last_counted   created_date
─────────────────  ────────────   ────────────
SHELF_5            2025-06-05     2026-02-01T10:30:00
SHELF_12           2025-08-20     2026-02-01T10:30:00
SHELF_3            2025-11-15     2026-02-01T10:30:00
...

RISK CALCULATION LOGIC
━━━━━━━━━━━━━━━━━━━━━━

expiration_date = purchase_date + shelf_life_days
days_to_expiry = (expiration_date - TODAY).days

IF days_to_expiry <= 0      → EXPIRED       🔴 (Delete/Destroy)
IF days_to_expiry <= 30     → CRITICAL      🔴 (Use ASAP or Transfer)
IF days_to_expiry <= 90     → HIGH          🟠 (Monitor closely)
IF days_to_expiry <= 180    → MEDIUM        🟡 (Normal monitoring)
IF days_to_expiry > 180     → LOW           🟢 (No concerns)
```

---

## 3. Consumption Table Structure (Demand Forecasting)

```
CONSUMPTION.CSV - Daily Drug Usage Records
═════════════════════════════════════════════════════════════════

transaction_id    facility_id    medication_id    transaction_date    transaction_type
──────────────    ───────────    ─────────────    ────────────────    ────────────────
TXN00000001       FAC001         MED001           2025-06-15          CONSUMPTION
TXN00000002       FAC001         MED002           2025-06-15          CONSUMPTION
TXN00000003       FAC002         MED001           2025-06-15          CONSUMPTION
...

quantity    unit_price    total_cost    department    prescriber_id
────────    ──────────    ──────────    ──────────    ─────────────
10          15.50         155.00        ICU           DOC234
5           25.00         125.00        ER            DOC567
15          10.00         150.00        Pharmacy      DOC890
...

SEASONALITY PATTERN
━━━━━━━━━━━━━━━━━━

Month(s)              Season          Demand Factor    Reason
─────────             ──────          ──────────────   ──────────
Nov, Dec, Jan, Feb    WINTER          1.3x (HIGH)      Flu, colds, respiratory
Mar, Apr, Sep, Oct    SPRING/FALL     1.0x (NORMAL)    Transition seasons
May, Jun, Jul, Aug    SUMMER          0.8x (LOW)       Fewer illnesses

EXAMPLE TIME SERIES
━━━━━━━━━━━━━━━━━━

Date            Consumption    Comment
────            ───────────    ──────────────────────────
2025-06-01      420 units      Summer - LOW demand (0.8x)
2025-11-01      650 units      Winter - HIGH demand (1.3x)
2025-12-01      680 units      Winter - HIGH demand (1.3x)
2026-01-01      710 units      Winter - HIGH demand (1.3x)
2026-06-01      420 units      Summer - LOW demand (0.8x)
```

---

## 4. Transfers Table Structure (Multi-Facility Coordination)

```
TRANSFERS.CSV - Inter-Facility Drug Movements
═════════════════════════════════════════════════════════════════

transfer_id    source_facility_id    target_facility_id    medication_id
───────────    ──────────────────    ──────────────────    ─────────────
TRF000001      FAC001                FAC002                MED001
TRF000002      FAC001                FAC003                MED005
TRF000003      FAC002                FAC001                MED010
...

quantity_requested    quantity_transferred    transfer_date    received_date
──────────────────    ────────────────────    ─────────────    ─────────────
200                   200                     2025-09-01       2025-09-04
300                   300                     2025-09-05       2025-09-08
100                   0                       2025-09-10       [EMPTY]
...

transfer_status    reason                    distance_miles    cost_usd
───────────────    ──────────────────────    ──────────────    ────────
COMPLETED          Shortage Prevention       15.3              250.00
COMPLETED          Expiration Management     22.1              350.00
REJECTED           [No reason needed]        18.5              0.00
...

MATCHING ENGINE LOGIC
━━━━━━━━━━━━━━━━━━━━

SOURCE FACILITY (has excess drug)         TARGET FACILITY (needs drug)
├─ Current inventory > reorder_level      ├─ Current inventory < reorder_level
├─ No immediate expiration risk           ├─ Facing shortage risk
└─ Available for transfer                 └─ Requesting transfer

MULTI-CRITERIA DECISION
┌──────────────────────────────────────────────┐
│ Score = distance + regulatory_check + urgency│
│         + capacity + timing                  │
└──────────────────────────────────────────────┘

STATUS OUTCOMES
COMPLETED  = Transfer happened successfully (200/200 units)
PENDING    = Awaiting approval or in transit (5 days average)
REJECTED   = Failed regulatory check or capacity issues (0 units)
```

---

## 5. External Signals Table Structure (Demand Forecasting)

```
EXTERNAL_SIGNALS.CSV - Context That Affects Demand
═════════════════════════════════════════════════════════════════

signal_date    weather_condition    weather_severity    disease_signal
───────────    ─────────────────    ────────────────    ──────────────
2025-11-15     SUNNY                NORMAL              NONE
2025-12-20     SNOW                 COLD_WAVE           NONE
2026-01-10     SUNNY                NORMAL              FLU_SPIKE
2026-01-25     CLOUDY               NORMAL              COVID_SURGE
...

hospital_event             external_demand_factor    created_date
──────────────             ──────────────────────    ────────────
NONE                       1.0                       2026-02-01T10:30:00
NONE                       1.2                       2026-02-01T10:30:00
NONE                       1.3                       2026-02-01T10:30:00
CONFERENCE                 0.9                       2026-02-01T10:30:00
...

DEMAND FACTOR MULTIPLIER
━━━━━━━━━━━━━━━━━━━━━━━

Scenario                    Factor    Impact on Demand
─────────────────────────   ──────    ────────────────
Normal day                  1.0x      No change
Cold wave / snow            1.2x      ↑↑ More respiratory drugs
Flu spike                   1.3x      ↑↑↑ More antibiotics & pain meds
COVID surge                 1.3x      ↑↑↑ More antiviral & ICU supplies
Hospital conference         0.9x      ↓ Fewer patients admitted
Emergency drill             0.7x      ↓↓ Reduced actual consumption
```

---

## 6. Demand Forecast Table Structure (Decision Support)

```
DEMAND_FORECAST.CSV - 90-Day Forward Predictions
═════════════════════════════════════════════════════════════════

forecast_id       facility_id    medication_id    forecast_date
────────────      ───────────    ─────────────    ─────────────
FCT00000001       FAC001         MED001           2026-02-05
FCT00000002       FAC001         MED001           2026-02-06
FCT00000003       FAC001         MED001           2026-02-07
...

forecast_quantity    confidence_interval_lower    confidence_interval_upper
─────────────────    ─────────────────────────    ─────────────────────────
150                  120                          180
155                  124                          186
148                  118                          178
...

forecast_method    created_date
────────────────   ────────────
Prophet            2026-02-01T10:30:00
Prophet            2026-02-01T10:30:00
Prophet            2026-02-01T10:30:00
...

CONFIDENCE INTERVALS
━━━━━━━━━━━━━━━━━━━

        | 80% Confidence Range
        |
  180   |         ╱╲
        |        ╱  ╲
  150   |       │ 150 │ ◄─── Point forecast (most likely)
        |       │     │
  120   |        ╲  ╱
        |         ╲╱
        └─────────────
          Upper bound
          120 units

If we predict 150 units but range is 120-180:
→ 80% chance actual demand will be between 120-180 units
→ We should stock 180 units to be safe (cover upper bound)
```

---

## 7. Replenishment Orders Table Structure (Decision Support)

```
REPLENISHMENT_ORDERS.CSV - Supplier Purchases
═════════════════════════════════════════════════════════════════

order_id    facility_id    medication_id    order_date    delivery_date
────────    ───────────    ─────────────    ──────────    ─────────────
ORD000001   FAC001         MED001           2025-08-10    2025-08-15
ORD000002   FAC001         MED002           2025-08-12    2025-08-17
ORD000003   FAC002         MED001           2025-08-15    [EMPTY]
...

order_quantity    unit_cost    order_status    supplier_id
──────────────    ─────────    ────────────    ───────────
500               18.75        DELIVERED       SUP01
800               12.50        DELIVERED       SUP03
1000              15.00        PENDING         SUP02
...

LEAD TIME ANALYSIS
━━━━━━━━━━━━━━━━━

Status        Meaning                  Avg Lead Time
──────        ─────────────────────    ─────────────
DELIVERED     Order arrived            ~5-10 days
PENDING       In transit               ~3-7 days
CANCELLED     Never arriving           N/A

DELIVERY FORECAST
━━━━━━━━━━━━━━━━

Order Date       Delivery Date    Days to Delivery
──────────       ─────────────    ────────────────
2025-08-10       2025-08-15       5 days
2025-08-12       2025-08-17       5 days
2025-08-15       [PENDING]        ~3-7 days (estimate)

USE FOR INVENTORY PLANNING
→ If forecast shows demand spike on Aug 20
→ And current inventory runs out Aug 15
→ Order by Aug 10 to arrive by Aug 15 (just in time!)
```

---

## 8. Complete Data Relationship Diagram

```
                    MASTER TABLES
                    ═════════════

            ┌──────────────┐  ┌───────────────┐
            │  FACILITIES  │  │  MEDICATIONS  │
            │              │  │               │
            │ • FAC001     │  │ • MED001      │
            │ • FAC002     │  │ • MED002      │
            │ • FAC003     │  │ • MED003      │
            │ ...          │  │ ...           │
            └──────┬───────┘  └───────┬───────┘
                   │                  │
        ┌──────────┴──────────────────┴────────────┐
        │                                          │
        ▼                                          ▼
    ┌──────────────────┐              ┌────────────────────┐
    │ INVENTORY        │              │ CONSUMPTION        │
    │ (Current Stock)  │              │ (Usage History)    │
    │                  │              │                    │
    │ • How much we    │              │ • What we used     │
    │   have right now │──────┐       │   in the past      │
    │ • Where it is    │      │       │ • When we used it  │
    │ • When it        │      │       │ • Who used it      │
    │   expires        │      │       └────────────────────┘
    │ • Risk level     │      │
    └──────────────────┘      │
                              │
                    ┌─────────┴──────────┐
                    │                    │
                    ▼                    ▼
            ┌─────────────────┐  ┌────────────────────┐
            │ DEMAND FORECAST │  │ EXTERNAL SIGNALS   │
            │ (Predictions)   │  │ (Context)          │
            │                 │  │                    │
            │ • What we'll    │  │ • Weather          │
            │   use tomorrow  │  │ • Disease outbreaks│
            │ • Confidence    │  │ • Hospital events  │
            │   intervals     │  │ • Demand factor    │
            └─────────────────┘  └────────────────────┘


            TRANSACTION TABLES
            ══════════════════

    ┌──────────────────────────┐  ┌──────────────────────────┐
    │ TRANSFERS                │  │ REPLENISHMENT ORDERS     │
    │ (Inter-Facility Moves)   │  │ (Supplier Purchases)     │
    │                          │  │                          │
    │ • Which facility sending │  │ • What we ordered        │
    │ • Which facility getting │  │ • When it's arriving     │
    │ • What drug             │  │ • Status (delivered/wait)│
    │ • How many units        │  │ • Cost                   │
    │ • Status (completed/etc)│  │                          │
    └──────────────────────────┘  └──────────────────────────┘


FEATURE MAPPING
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│  FEATURE 1: EXPIRATION MANAGEMENT                            │
├──────────────────────────────────────────────────────────────┤
│  Primary: INVENTORY.csv (risk_level column)                  │
│  Secondary: REPLENISHMENT_ORDERS, TRANSFERS                 │
│                                                              │
│  Logic: IF days_to_expiry < 90 THEN recommend action        │
│         → Use in facility (priority ICU/ER)                 │
│         → Transfer to another facility                      │
│         → Destroy if too close to expiry                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  FEATURE 2: MULTI-FACILITY COORDINATION                      │
├──────────────────────────────────────────────────────────────┤
│  Primary: TRANSFERS.csv, INVENTORY.csv                      │
│  Secondary: FACILITIES.csv                                  │
│                                                              │
│  Logic: IF (FAC_A.inventory > threshold AND                 │
│              FAC_B.inventory < threshold AND                 │
│              distance is reasonable AND                      │
│              regulations allow)                             │
│         THEN recommend transfer FAC_A → FAC_B               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  FEATURE 3: DEMAND FORECASTING                               │
├──────────────────────────────────────────────────────────────┤
│  Primary: CONSUMPTION.csv, EXTERNAL_SIGNALS.csv             │
│  Secondary: DEMAND_FORECAST.csv (validation)                │
│                                                              │
│  Logic: Train ML model on CONSUMPTION + EXTERNAL_SIGNALS    │
│         → Predict 7/14/30 days forward                      │
│         → Factor in seasonality, weather, disease           │
│         → Output to DEMAND_FORECAST.csv                     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  FEATURE 4: DECISION SUPPORT ANALYTICS (Power BI)            │
├──────────────────────────────────────────────────────────────┤
│  Primary: ALL CSV files combined                            │
│  Secondary: Computed metrics (waste %, turnover, etc)       │
│                                                              │
│  Dashboards:                                                │
│  1. Inventory Dashboard (by facility, category, risk)       │
│  2. Demand Dashboard (forecast vs actual)                   │
│  3. Expiration Dashboard (at-risk items)                    │
│  4. Transfer Dashboard (movements, costs, status)           │
│  5. Supplier Dashboard (order status, lead times)           │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Data Generation Process Flow

```
START
  │
  ├─► Import libraries (datetime, random, csv, os)
  │
  ├─► SET SEED (for reproducibility)
  │   └─► Every run generates SAME random numbers
  │
  ├─► CREATE OUTPUT DIRECTORY (synthetic_data/)
  │
  ├─► [1] FACILITIES
  │   └─► Write 5 hospitals to CSV
  │
  ├─► [2] MEDICATIONS
  │   └─► Write 25 drugs to CSV
  │
  ├─► [3] INVENTORY (3,000 rows)
  │   ├─► For each batch:
  │   │   ├─► Pick random facility
  │   │   ├─► Pick random medication
  │   │   ├─► Generate realistic quantity
  │   │   ├─► Calculate expiration date
  │   │   ├─► Assign risk level
  │   │   └─► Write to CSV
  │   └─► Count risk distribution
  │
  ├─► [4] CONSUMPTION (~182,500 rows)
  │   ├─► For each day in past 365 days:
  │   │   ├─► Calculate seasonal demand factor
  │   │   ├─► Generate daily transactions
  │   │   ├─► For each transaction:
  │   │   │   ├─► Pick random facility
  │   │   │   ├─► Pick random medication
  │   │   │   ├─► Generate quantity/price
  │   │   │   └─► Write to CSV
  │   │   └─► Sum all transactions
  │
  ├─► [5] TRANSFERS (500 rows)
  │   ├─► For each transfer:
  │   │   ├─► Pick source facility
  │   │   ├─► Pick different target facility
  │   │   ├─► Pick medication
  │   │   ├─► Assign status (mostly COMPLETED)
  │   │   └─► Write to CSV
  │   └─► Count status distribution
  │
  ├─► [6] EXTERNAL SIGNALS (365 rows)
  │   ├─► For each day:
  │   │   ├─► Check month (seasonality)
  │   │   ├─► Add random weather events
  │   │   ├─► Add random disease signals
  │   │   ├─► Calculate demand factor
  │   │   └─► Write to CSV
  │
  ├─► [7] DEMAND FORECAST (~22,500 rows)
  │   ├─► For next 90 days:
  │   │   ├─► For each facility:
  │   │   │   ├─► For top 10 medications:
  │   │   │   │   ├─► Generate base demand
  │   │   │   │   ├─► Apply seasonal factor
  │   │   │   │   ├─► Calculate confidence interval
  │   │   │   │   └─► Write to CSV
  │
  ├─► [8] REPLENISHMENT ORDERS (200 rows)
  │   ├─► For each order:
  │   │   ├─► Pick random facility
  │   │   ├─► Pick random medication
  │   │   ├─► Assign status (mostly DELIVERED)
  │   │   ├─► Calculate delivery date
  │   │   └─► Write to CSV
  │   └─► Count status distribution
  │
  ├─► PRINT SUMMARY
  │   ├─► File paths
  │   ├─► Row counts
  │   └─► Distributions
  │
  └─► END ✓
```

---

## 10. How the 4 Features Use This Data

```
EXPIRATION MANAGEMENT AGENT
════════════════════════════════════════════════════════════════

1. READ inventory.csv
2. FILTER WHERE days_to_expiry <= 90
3. RANK BY (risk_level, facility_id, medication_id)
4. FOR EACH at-risk item:
   ├─ CREATE recommendation:
   │  ├─ If days_to_expiry <= 30: "URGENT - Transfer to FAC with ICU"
   │  ├─ If days_to_expiry <= 60: "Priority use in General Ward"
   │  └─ If days_to_expiry <= 90: "Monitor - Consider transfer"
   │
   └─ OUTPUT recommendation to Power BI + trigger alerts
5. TRACK success metrics:
   ├─ Items avoided expiry
   ├─ Medications successfully transferred
   └─ Waste prevented (cost saved)


MULTI-FACILITY COORDINATION ENGINE
════════════════════════════════════════════════════════════════

1. READ inventory.csv (current stock everywhere)
2. CALCULATE for each facility+medication:
   ├─ current_stock
   ├─ reorder_level
   ├─ days_until_expiry
   └─ shortage_risk = (current_stock < reorder_level * 1.2)

3. FIND matching opportunities:
   ├─ SOURCE: current_stock > reorder_level * 2 (excess)
   ├─ TARGET: current_stock < reorder_level (shortage)
   └─ SAME medication_id

4. SCORE each match:
   ├─ Distance (prioritize nearby facilities)
   ├─ Urgency (shortage deadline)
   ├─ Regulatory compliance (yes/no)
   ├─ Capacity (target has space?)
   └─ Time (can deliver before expiry?)

5. CREATE transfer recommendation & write to transfers.csv
6. MONITOR via transfers.csv status column


DEMAND FORECASTING ML PIPELINE
════════════════════════════════════════════════════════════════

1. READ consumption.csv (historical usage)
2. READ external_signals.csv (context)
3. MERGE by signal_date = transaction_date

4. FEATURE ENGINEERING:
   ├─ day_of_week
   ├─ month
   ├─ is_holiday
   ├─ weather_severity
   ├─ disease_signal
   ├─ rolling_mean (7-day average)
   └─ rolling_std (volatility)

5. TRAIN Prophet/ARIMA model:
   ├─ Input: [date, consumption_qty, external_factor]
   ├─ Learn seasonal patterns
   └─ Learn trend

6. FORECAST next 90 days:
   ├─ FOR each facility+medication:
   │  ├─ PREDICT demand_qty
   │  ├─ CALCULATE confidence_interval
   │  └─ WRITE to demand_forecast.csv
   │
   └─ EVALUATE MAE against actual (validation)

7. ALERT if forecast shows:
   ├─ Potential shortage
   ├─ Sudden spike
   └─ Unusual pattern


POWER BI DASHBOARDS
════════════════════════════════════════════════════════════════

Sheet 1: INVENTORY SNAPSHOT
├─ Total units by facility (donut chart)
├─ Total units by category (bar chart)
├─ Risk distribution (stacked bar)
└─ Storage utilization %

Sheet 2: EXPIRATION RISK
├─ At-risk items count (card)
├─ Items by risk_level (pie chart)
├─ Days-to-expiry timeline (line chart)
└─ Top 10 medications at risk (table)

Sheet 3: DEMAND FORECAST
├─ Actual vs Forecast (line chart)
├─ Forecast confidence intervals (area chart)
├─ Forecast by facility (small multiples)
└─ Top 10 medications by demand (bar chart)

Sheet 4: TRANSFERS & COORDINATION
├─ Transfers by status (pie chart)
├─ Transfer reasons (bar chart)
├─ Cost by source facility (tree map)
└─ Pending transfers (table with alerts)

Sheet 5: SUPPLY CHAIN HEALTH
├─ Replenishment status (gauge)
├─ Average lead time (card)
├─ Order completion % (card)
└─ Cost trend (area chart)
```

---

## Quick Reference: Which CSV File to Use

| Question | Answer | CSV File |
|----------|--------|----------|
| What medications do we have? | facilities.csv + inventory.csv | See medications.csv reference |
| Which drugs are about to expire? | CRITICAL & HIGH risk_level | inventory.csv |
| What's our daily usage pattern? | Consumption by date | consumption.csv |
| Which facility needs what drug? | Join inventory with shortage risk | inventory.csv |
| Can we transfer from FAC1 to FAC2? | Check transfers.csv success rate | transfers.csv |
| What's the weather doing? | Check signal_date + weather | external_signals.csv |
| How much will we need next week? | Check forecast_date forecast_qty | demand_forecast.csv |
| When will our orders arrive? | Check order_status + delivery_date | replenishment_orders.csv |

