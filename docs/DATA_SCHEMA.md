# Pharmaceutical Inventory Platform - Synthetic Data Schema

## Overview
This document describes the synthetic dataset structure generated for the Pharmaceutical Inventory Optimization Platform. The data supports four core features:

1. **Expiration Management** – detect near-expiry stock across facilities
2. **Multi-Facility Coordination** – enable inter-facility inventory sharing
3. **Demand Forecasting** – predict medication demand with external signals
4. **Decision Support Analytics** – Power BI dashboards for operational insight

---

## Data Files

### 1. `facilities.csv`
**Purpose:** Master data for healthcare facilities in the network  
**Rows:** 5 facilities  
**Use Cases:** Join key for facility-level aggregations, geographic routing in transfer matching  

| Column | Type | Description |
|--------|------|-------------|
| id | String | Unique facility identifier (FAC001–FAC005) |
| name | String | Facility name |
| city | String | City location |
| state | String | State code |
| capacity | Integer | Total storage capacity (units) |
| created_date | Timestamp | Record creation timestamp |
| last_updated | Timestamp | Last update timestamp |

**Sample:**
```
FAC001,Downtown Medical Center,Seattle,WA,10000,...
FAC002,Northgate Community Hospital,Seattle,WA,5000,...
```

---

### 2. `medications.csv`
**Purpose:** Master data for medication SKUs  
**Rows:** 25 medications  
**Use Cases:** Medication attribute lookups, shelf-life calculations for expiration alerts  

| Column | Type | Description |
|--------|------|-------------|
| id | String | Unique medication identifier (MED001–MED025) |
| name | String | Brand/generic name and strength |
| category | String | Drug category (Cardiovascular, Antibiotic, etc.) |
| shelf_life_days | Integer | Days until expiration from manufacture date |
| created_date | Timestamp | Record creation timestamp |
| last_updated | Timestamp | Last update timestamp |

**Sample:**
```
MED001,Lisinopril 10mg,Cardiovascular,1825,...
MED005,Amoxicillin 500mg,Antibiotic,730,...
```

**Shelf Life Ranges:**
- Long-term: 1825 days (~5 years) – most cardiovascular, psychiatric meds
- Medium-term: 1095 days (~3 years) – GI, respiratory drugs
- Short-term: 730 days (~2 years) – antibiotics
- Very short: 365 days (~1 year) – Insulin and biologics

---

### 3. `inventory.csv`
**Purpose:** Current and historical inventory batches  
**Rows:** 3,000 batches  
**Features Supported:** Expiration Management, Decision Support Analytics  
**Use Cases:**
- Identify near-expiry stock (CRITICAL, HIGH risk levels)
- Alert pharmacists to urgent transfers
- Track inventory by facility/medication/risk level
- Calculate waste prevention potential

| Column | Type | Description |
|--------|------|-------------|
| inventory_id | String | Unique batch identifier |
| facility_id | String | FK to facilities.csv |
| medication_id | String | FK to medications.csv |
| batch_number | String | Manufacturer batch/lot number |
| quantity_on_hand | Integer | Current units in stock |
| reorder_level | Integer | Reorder trigger point (~25% of on-hand) |
| purchase_date | Date | Date batch was received/purchased |
| expiration_date | Date | Manufacturer expiration date |
| days_to_expiry | Integer | Days until expiration (can be negative if expired) |
| risk_level | String | **EXPIRED** \| **CRITICAL** (≤30d) \| **HIGH** (31-90d) \| **MEDIUM** (91-180d) \| **LOW** (>180d) |
| storage_location | String | Physical shelf/bin identifier (SHELF_1–SHELF_20) |
| last_counted | Date | Last inventory count date |
| created_date | Timestamp | Record creation timestamp |

**Risk Distribution (from 3,000 records):**
```
EXPIRED:  0 items
CRITICAL: 10 items (0.3%) – Urgent actions required
HIGH:     15 items (0.5%) – Schedule transfers/use
MEDIUM:   31 items (1%) – Monitor closely
LOW:      2,944 items (98%) – Normal stock
```

**Key Analytics:**
- **Expiration Management Agent** queries `risk_level IN ('EXPIRED', 'CRITICAL', 'HIGH')` to generate transfer recommendations
- **Power BI Alerts** surface CRITICAL items for immediate action

---

### 4. `consumption.csv`
**Purpose:** Historical transaction log of medication consumption  
**Rows:** ~187,578 transactions (1-year history)  
**Features Supported:** Demand Forecasting, Decision Support Analytics  
**Use Cases:**
- Train time-series forecasting models (Prophet, ARIMA)
- Detect demand seasonality (flu season → winter spike)
- Calculate per-facility, per-medication baseline consumption
- Detect anomalies (unusual usage patterns)

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | String | Unique transaction identifier |
| facility_id | String | FK to facilities.csv |
| medication_id | String | FK to medications.csv |
| transaction_date | Date | Date of consumption |
| transaction_type | String | "CONSUMPTION" (for future: "RETURN", "ADJUSTMENT") |
| quantity | Integer | Units consumed (1–20 units per transaction) |
| unit_price | Float | Unit cost in USD |
| total_cost | Float | Quantity × unit_price |
| department | String | ICU \| ER \| Pharmacy \| General Ward \| Surgery |
| prescriber_id | String | Clinician identifier (DOC###) |
| created_date | Timestamp | Record creation timestamp |

**Seasonality Pattern:**
- **Winter (Nov–Feb):** 1.3× baseline (flu season, respiratory infections)
- **Spring/Fall (Mar–Apr, Sep–Oct):** 1.0× baseline (normal)
- **Summer (May–Aug):** 0.8× baseline (lower infection rates)

**Daily Volumes:**
- Average: ~500 transactions/day (varies by seasonality ±20%)
- Monthly: ~15,000–18,000 transactions
- Yearly: ~187,578 transactions

**Use in Forecasting:**
```python
# Example: Rolling 7-day consumption average
consumption_pivot = consumption_df.pivot_table(
    values='quantity',
    index='transaction_date',
    columns=['facility_id', 'medication_id'],
    aggfunc='sum'
)
# Train Prophet on each medication×facility timeseries
```

---

### 5. `transfers.csv`
**Purpose:** Historical inter-facility medication transfers  
**Rows:** 500 transfer records (6-month history)  
**Features Supported:** Multi-Facility Coordination, Decision Support Analytics  
**Use Cases:**
- Analyze successful transfer patterns (distance, status, cost)
- Train transfer matching/routing algorithm
- Calculate transfer lead times (2–10 days typical)
- Cost optimization for multi-facility network
- Audit trail for regulatory compliance

| Column | Type | Description |
|--------|------|-------------|
| transfer_id | String | Unique transfer identifier |
| source_facility_id | String | FK to facilities.csv (sending facility) |
| target_facility_id | String | FK to facilities.csv (receiving facility) |
| medication_id | String | FK to medications.csv |
| quantity_requested | Integer | Units requested by target facility |
| quantity_transferred | Integer | Units actually transferred (0 if REJECTED) |
| transfer_date | Date | Date transfer initiated |
| received_date | Date | Date received at target facility (NULL if not completed) |
| transfer_status | String | **COMPLETED** (60%) \| **PENDING** (19%) \| **REJECTED** (21%) |
| reason | String | Shortage Prevention \| Expiration Management \| Demand Spike \| Regulatory |
| distance_miles | Float | Distance between facilities (5–100 miles) |
| cost_usd | Float | Transfer cost in USD (includes logistics, handling) |
| created_date | Timestamp | Record creation timestamp |

**Status Distribution (500 records):**
```
COMPLETED: 300 (60%) – Successful transfers
PENDING:   94 (19%) – In transit or awaiting approval
REJECTED:  106 (21%) – Declined due to capacity/timing
```

**Average Lead Time (completed transfers):** 4.5 days

**Multi-Criteria Matching Features:**
- `distance_miles` – minimize logistics cost
- `transfer_status` – predict completion probability
- `reason` – prioritize expiration management transfers
- `quantity_transferred / quantity_requested` – fulfillment ratio

**Power BI Visualizations:**
- Transfer success rate by facility pair
- Cost per unit transferred
- Expiration-driven vs. demand-driven transfers

---

### 6. `external_signals.csv`
**Purpose:** External factors influencing demand (weather, disease, events)  
**Rows:** 365 daily signals (1-year history)  
**Features Supported:** Demand Forecasting  
**Use Cases:**
- Augment time-series forecasting with external regressors
- Detect demand spikes triggered by external events
- Improve forecast accuracy in crisis scenarios
- Scenario planning: "What if COVID surge?"

| Column | Type | Description |
|--------|------|-------------|
| signal_date | Date | Date of signal |
| weather_condition | String | SUNNY \| COLD_WAVE \| SNOW (affects flu seasonality) |
| weather_severity | String | NORMAL \| COLD_WAVE \| SNOW |
| disease_signal | String | NONE \| FLU_SPIKE \| COVID_SURGE \| RSV_OUTBREAK |
| hospital_event | String | NONE \| EMERGENCY_DRILL \| CONFERENCE \| HOLIDAY (affects ops) |
| external_demand_factor | Float | Multiplier on baseline demand (1.0 = normal, 1.3 = surge) |
| created_date | Timestamp | Record creation timestamp |

**Demand Factor Logic:**
- Weather severe: +20% factor
- Disease signal active: +30% factor
- Hospital event: -10% factor
- Normal conditions: 1.0× factor

**Integration with Forecasting:**
```python
# Merge external signals into consumption data
consumption_with_signals = consumption_df.merge(
    signals_df,
    left_on='transaction_date',
    right_on='signal_date'
)
# Train Prophet with external regressors
model = Prophet()
model.add_regressor('external_demand_factor')
model.fit(consumption_with_signals)
```

---

### 7. `demand_forecast.csv`
**Purpose:** Machine learning baseline demand forecast (90-day forward)  
**Rows:** 4,500 forecast records  
**Features Supported:** Demand Forecasting, Decision Support Analytics  
**Use Cases:**
- Seed Power BI with forecast data for scenario planning
- Compare actual vs. forecast performance
- Inform replenishment orders
- Detect forecast drift (retrain trigger)

| Column | Type | Description |
|--------|------|-------------|
| forecast_id | String | Unique forecast record identifier |
| facility_id | String | FK to facilities.csv |
| medication_id | String | FK to medications.csv |
| forecast_date | Date | Date of forecasted demand |
| forecast_quantity | Integer | Predicted units needed |
| confidence_interval_lower | Integer | 80th percentile CI lower bound |
| confidence_interval_upper | Integer | 80th percentile CI upper bound |
| forecast_method | String | "Prophet" (Prophet library) |
| created_date | Timestamp | Forecast generation timestamp |

**Forecast Horizon:** 90 days forward from today  
**Coverage:**  
- 5 facilities × 10 top medications × 90 days = 4,500 records  
- Includes seasonality adjustments (winter demand +30%)

**Power BI Integration:**
```
SELECT
  facility_id,
  medication_id,
  forecast_date,
  forecast_quantity,
  confidence_interval_lower,
  confidence_interval_upper
FROM demand_forecast
WHERE forecast_date BETWEEN GETDATE() AND DATEADD(day, 90, GETDATE())
ORDER BY forecast_date, facility_id, medication_id;
```

---

### 8. `replenishment_orders.csv`
**Purpose:** Purchase orders and replenishment history  
**Rows:** 200 order records (3-month history)  
**Features Supported:** Decision Support Analytics  
**Use Cases:**
- Optimize reorder quantities and timing
- Predict order fulfillment status
- Track supplier performance
- Calculate days-to-delivery

| Column | Type | Description |
|--------|------|-------------|
| order_id | String | Unique order identifier |
| facility_id | String | FK to facilities.csv (ordering facility) |
| medication_id | String | FK to medications.csv |
| order_date | Date | Date order was placed |
| delivery_date | Date | Expected/actual delivery date (NULL if PENDING/CANCELLED) |
| order_quantity | Integer | Units ordered (100–1,000 units) |
| unit_cost | Float | Cost per unit in USD |
| order_status | String | **DELIVERED** (64.5%) \| **PENDING** (17.5%) \| **CANCELLED** (18%) |
| supplier_id | String | Supplier identifier (SUP01–SUP10) |
| created_date | Timestamp | Record creation timestamp |

**Order Status Distribution:**
```
DELIVERED: 129 (64.5%) – Completed orders
PENDING:   35 (17.5%) – In transit/processing
CANCELLED: 36 (18%) – Cancelled or unfulfilled
```

**Average Lead Time (delivered):** 6 days

**Power BI Dashboard Metrics:**
- On-time delivery rate by supplier
- Average order-to-delivery time
- Cost per unit by supplier
- Order fulfillment status heatmap

---

## Feature-to-Data Mapping

### 1. Expiration Management (Agentic AI)
**Primary Tables:** `inventory.csv`, `medications.csv`, `facilities.csv`  
**Key Query Pattern:**
```sql
SELECT
  i.inventory_id, i.facility_id, i.medication_id,
  m.name, m.shelf_life_days,
  i.days_to_expiry, i.risk_level,
  i.quantity_on_hand,
  i.expiration_date
FROM inventory i
JOIN medications m ON i.medication_id = m.id
WHERE i.risk_level IN ('EXPIRED', 'CRITICAL', 'HIGH')
ORDER BY i.days_to_expiry ASC;
```
**Agent Actions:**
1. Query inventory for high-risk items
2. Look up facility contact info
3. Recommend: use first, transfer, or discard
4. Alert: create notification to pharmacist

---

### 2. Multi-Facility Coordination (Transfer Matching Engine)
**Primary Tables:** `inventory.csv`, `transfers.csv`, `facilities.csv`, `medications.csv`  
**Key Query Pattern:**
```sql
SELECT
  source.facility_id AS source_facility,
  target.facility_id AS target_facility,
  f1.name, f2.name,
  i.medication_id, m.name,
  i.quantity_on_hand,
  SQRT(POWER(LAT1 - LAT2, 2) + POWER(LON1 - LON2, 2)) AS distance_miles
FROM inventory i
JOIN facilities f1 ON i.facility_id = f1.id
JOIN facilities f2 ON f2.id != f1.id
JOIN medications m ON i.medication_id = m.id
WHERE i.risk_level IN ('CRITICAL', 'HIGH')
  AND i.quantity_on_hand > f2.reorder_level
ORDER BY distance_miles ASC;
```
**Agent Actions:**
1. Identify high-risk inventory
2. Find facilities with capacity to receive
3. Rank by: distance, urgency, completion probability
4. Create transfer request (human approval)
5. Track transfer status

---

### 3. Demand Forecasting (ML)
**Primary Tables:** `consumption.csv`, `external_signals.csv`, `demand_forecast.csv`, `medications.csv`  
**Model Inputs:**
- Historical consumption (time-series per facility-medication)
- Seasonality signals
- External demand factors (weather, disease, events)
- Historical forecast accuracy

**Model Outputs:**
- 90-day forward point estimate
- Confidence intervals (80%, 95%)
- Anomaly flags

**Key Statistics:**
```
Time period: 365 days of consumption history
Granularity: daily transactions
Frequency: ~500 transactions/day
Seasonality: winter +30%, summer -20%
External factors: disease outbreaks, weather, events
```

---

### 4. Decision Support Analytics (Power BI)
**Primary Tables:** All tables (fact star schema)  
**Fact Tables:** `consumption.csv`, `transfers.csv`, `replenishment_orders.csv`  
**Dimension Tables:** `facilities.csv`, `medications.csv`, `inventory.csv`  

**Example Power BI Measures:**
```
Expiration Risk = 
  COUNTROWS(
    FILTER(inventory, 
      inventory[risk_level] IN {"CRITICAL", "HIGH"})
  )

Transfer Success Rate = 
  DIVIDE(
    COUNTROWS(
      FILTER(transfers, transfers[transfer_status] = "COMPLETED")
    ),
    COUNTROWS(transfers)
  )

Forecast Accuracy = 
  DIVIDE(
    SUM(FILTER(consumption, ABS(actual - forecast) < tolerance)),
    COUNTROWS(consumption)
  )
```

---

## Data Quality & Validation Checks

### Inventory Quality
- ✓ No NULL values in required fields
- ✓ days_to_expiry = DATEDIFF(expiration_date, TODAY())
- ✓ risk_level consistent with days_to_expiry ranges
- ✓ quantity_on_hand ≥ 0
- ✓ All facility_id and medication_id are valid FKs

### Consumption Quality
- ✓ All transaction_dates within 365-day window
- ✓ quantity ≥ 1
- ✓ total_cost = quantity × unit_price
- ✓ transaction_type valid (currently all "CONSUMPTION")
- ✓ Department values from known set

### Transfer Quality
- ✓ source_facility_id ≠ target_facility_id
- ✓ transfer_date ≤ received_date (if not NULL)
- ✓ quantity_transferred ≤ quantity_requested
- ✓ If status = "REJECTED", quantity_transferred = 0
- ✓ transfer_status valid

### External Signals Quality
- ✓ signal_date covers entire year (365 days, no gaps)
- ✓ external_demand_factor ≥ 0.7 and ≤ 1.5
- ✓ weather_severity and disease_signal consistent with demand_factor

### Forecast Quality
- ✓ forecast_date ≥ TODAY() (future dates only)
- ✓ confidence_interval_lower ≤ forecast_quantity
- ✓ forecast_quantity ≤ confidence_interval_upper
- ✓ All facility_id × medication_id pairs within coverage

---

## Next Steps: ETL & Data Loading

### 1. AWS S3 Upload
```bash
aws s3 cp synthetic_data/ s3://pharma-inventory-raw/data/ --recursive
```

### 2. AWS Glue Data Catalog
Create Glue tables for each CSV:
```python
glue_client.create_table(
    DatabaseName='pharma_inventory',
    TableInput={
        'Name': 'inventory',
        'StorageDescriptor': {
            'Columns': [
                {'Name': 'inventory_id', 'Type': 'string'},
                {'Name': 'facility_id', 'Type': 'string'},
                # ...
            ],
            'Location': 's3://pharma-inventory-raw/data/inventory.csv',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
            }
        }
    }
)
```

### 3. Load into Redshift/RDS
```sql
-- Create tables in Redshift
CREATE TABLE facilities (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    capacity INT
);

-- COPY from S3
COPY facilities FROM 's3://pharma-inventory-raw/data/facilities.csv'
    IAM_ROLE 'arn:aws:iam::ACCOUNT:role/redshift-role'
    IGNOREHEADER 1
    DELIMITER ',';
```

### 4. Power BI Direct Query or Import
- **Option A:** DirectQuery to Redshift (real-time)
- **Option B:** Import Parquet files (daily refresh)

---

## Summary Statistics

| Dataset | Rows | Time Span | Key Metric |
|---------|------|-----------|-----------|
| facilities | 5 | N/A | 5 healthcare facilities |
| medications | 25 | N/A | 25 drug SKUs across 8 categories |
| inventory | 3,000 | Current snapshot | 10 critical+high-risk items |
| consumption | ~187,578 | 365 days | ~500 transactions/day |
| transfers | 500 | 180 days | 60% completion rate |
| external_signals | 365 | 365 days | Seasonality + crisis events |
| demand_forecast | 4,500 | 90 days forward | 5 facilities × 10 meds × 90 days |
| replenishment_orders | 200 | 90 days | 64% on-time delivery |

**Total Records:** ~195,978 transactions  
**Data Volume:** ~15–20 MB (uncompressed CSV)  
**Compressed (gzip):** ~2–3 MB

---

## Contact & Documentation
- **Data Generator:** `synthetic_data_generator_lite.py`
- **Generated:** February 1, 2026
- **Purpose:** Pharmaceutical Inventory Optimization Platform (Capstone Project)
