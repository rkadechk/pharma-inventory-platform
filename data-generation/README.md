# Data Generation Module

This module generates realistic synthetic pharmaceutical inventory data for the Pharmaceutical Inventory Optimization Platform.

## Quick Start

### Run the Generator
```bash
cd pharma-inventory-platform/data-generation
python synthetic_data_generator_lite.py
```

**Output:** 8 CSV files in `synthetic_data/` directory

### Generated Files Summary

| File | Rows | Purpose |
|------|------|---------|
| `facilities.csv` | 5 | Healthcare facilities in the network |
| `medications.csv` | 25 | Pharmaceutical drug SKUs |
| `inventory.csv` | 3,000 | Current and historical stock with expiration risk |
| `consumption.csv` | ~187,578 | 1-year transaction history (demand pattern) |
| `transfers.csv` | 500 | Inter-facility medication transfers |
| `external_signals.csv` | 365 | Daily weather, disease, and event signals |
| `demand_forecast.csv` | 4,500 | ML-generated 90-day forward forecasts |
| `replenishment_orders.csv` | 200 | Purchase order history |

## Features Supported

### 1. Expiration Management (Agentic AI)
- **Data:** `inventory.csv`
- **Key Metric:** Risk-level distribution (EXPIRED, CRITICAL, HIGH, MEDIUM, LOW)
- **Use Case:** Identify near-expiry stock and recommend transfers or clinical prioritization
- **Sample Query:**
  ```sql
  SELECT * FROM inventory
  WHERE risk_level IN ('CRITICAL', 'HIGH')
  ORDER BY days_to_expiry ASC;
  ```

### 2. Multi-Facility Coordination
- **Data:** `transfers.csv`, `facilities.csv`, `inventory.csv`
- **Key Metric:** Transfer success rate (60% COMPLETED)
- **Use Case:** Match surplus stock at one facility with shortage at another using multi-criteria algorithm
- **Matching Criteria:**
  - Geographic distance (5–100 miles)
  - Facility storage capacity
  - Transfer completion probability
  - Regulatory compliance

### 3. Demand Forecasting (ML)
- **Data:** `consumption.csv`, `external_signals.csv`, `demand_forecast.csv`
- **Key Metrics:**
  - 1-year consumption history (~187K transactions)
  - 365 daily signals (weather, disease, events)
  - 90-day forward forecasts with confidence intervals
- **Seasonality:** Winter demand +30%, summer demand -20%
- **External Factors:** COVID surges, flu spikes, weather events

### 4. Decision Support Analytics (Power BI)
- **Data:** All tables (star schema)
- **Key Dashboards:**
  - Inventory health (expiration risk, stock levels)
  - Transfer performance (success rate, cost per unit)
  - Demand forecast vs. actual (forecast accuracy)
  - Replenishment order tracking

## Data Characteristics

### Realistic Patterns

**Consumption Seasonality:**
- Winter (Nov–Feb): +30% demand spike (flu season)
- Spring/Fall (Mar–Apr, Sep–Oct): Normal demand
- Summer (May–Aug): -20% lower demand

**Expiration Risk Distribution:**
- EXPIRED: 0% (managed proactively)
- CRITICAL (≤30 days): 0.3%
- HIGH (31–90 days): 0.5%
- MEDIUM (91–180 days): 1%
- LOW (>180 days): 98%

**Transfer Success Rate:**
- COMPLETED: 60% (successful transfers)
- PENDING: 19% (in transit)
- REJECTED: 21% (declined or failed)

**Average Transfer Time:** 4.5 days (source to destination)

### Medication Coverage
- **Categories:** Cardiovascular, Antibiotic, GI, Psychiatric, Pain, Endocrine, etc.
- **Shelf Lives:**
  - Long: 1,825 days (~5 years) – most chronic-use drugs
  - Medium: 1,095 days (~3 years) – GI and respiratory
  - Short: 730 days (~2 years) – antibiotics
  - Very short: 365 days (~1 year) – insulin and biologics

### Facility Network
- 5 healthcare facilities across WA state
- Capacities: 3,000–10,000 units per facility
- Realistic geographic distances for transfer matching

## Data Quality Checks

All synthetic data passes validation:
- ✓ No NULL values in required fields
- ✓ Referential integrity (facility_id, medication_id valid)
- ✓ Logical consistency (risk_level matches days_to_expiry)
- ✓ Quantity constraints (no negative quantities)
- ✓ Date ordering (transfer_date ≤ received_date)
- ✓ Cost calculations (total_cost = quantity × unit_price)

## Integration with ETL Pipeline

### Step 1: Upload to S3 (Raw Layer)
```bash
aws s3 cp synthetic_data/ s3://pharma-inventory-raw/input/ --recursive
```

### Step 2: Process with AWS Glue
```python
import boto3
glue = boto3.client('glue')

# Create Glue Data Catalog entries
glue.create_table(
    DatabaseName='pharma_inventory',
    TableInput={
        'Name': 'inventory_raw',
        'StorageDescriptor': {
            'Location': 's3://pharma-inventory-raw/input/inventory.csv',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'}
        }
    }
)
```

### Step 3: Transform to Parquet (Curated Layer)
```python
import pandas as pd
inventory_df = pd.read_csv('synthetic_data/inventory.csv')
inventory_df.to_parquet('s3://pharma-inventory-curated/inventory.parquet')
```

### Step 4: Load into Redshift/RDS
```sql
-- Create table
CREATE TABLE inventory (
    inventory_id VARCHAR(10) PRIMARY KEY,
    facility_id VARCHAR(10) REFERENCES facilities(id),
    medication_id VARCHAR(10) REFERENCES medications(id),
    quantity_on_hand INT,
    days_to_expiry INT,
    risk_level VARCHAR(20),
    expiration_date DATE
);

-- Load from S3
COPY inventory FROM 's3://pharma-inventory-curated/inventory.parquet'
    IAM_ROLE 'arn:aws:iam::ACCOUNT:role/redshift-role'
    FORMAT PARQUET;
```

### Step 5: Connect Power BI
- **Mode 1:** DirectQuery to Redshift (real-time)
- **Mode 2:** Import Parquet files daily (scheduled refresh)

## Configuration

**Generator File:** `synthetic_data_generator_lite.py`

### Customization Options
```python
# Modify in synthetic_data_generator_lite.py

# Change number of facilities
FACILITIES = [...]  # Add/remove facilities

# Change number of medications
MEDICATIONS = [...]  # Add/remove drugs

# Adjust data volumes
num_batches = 3000  # Inventory records
num_days = 365      # Historical consumption days
records_per_day = 500  # Transactions per day

# Modify seasonality
seasonal_factor = 1.3 if month in [11, 12, 1, 2] else 1.0

# Adjust risk distribution
if days_to_expiry <= 30:
    risk_level = "CRITICAL"  # Threshold customizable
```

## Troubleshooting

### Issue: "Unable to import numpy" error
**Solution:** Run generator from a different directory:
```bash
cd ..
python data-generation/synthetic_data_generator_lite.py
```

### Issue: Missing `synthetic_data/` directory
**Solution:** Generator creates it automatically. Check permissions:
```bash
ls -la synthetic_data/
```

### Issue: CSV encoding problems in Windows
**Solution:** Specify UTF-8 encoding when reading:
```python
df = pd.read_csv('inventory.csv', encoding='utf-8')
```

## Next Steps

1. **Verify Data:** Check CSV files in `synthetic_data/`
2. **Create ETL Pipeline:** Build AWS Glue job to transform CSVs → Parquet
3. **Load to Data Warehouse:** Copy Parquet to Redshift/RDS
4. **Build Power BI Dashboards:** Connect BI tool to warehouse
5. **Develop Agents:** Implement expiration and transfer matching agents in Python
6. **Deploy ML Models:** Train demand forecasting models (Prophet/ARIMA)

## Documentation

- **Full Data Schema:** See `DATA_SCHEMA.md` (detailed column descriptions, use cases, examples)
- **Feature Mapping:** See `DATA_SCHEMA.md` → "Feature-to-Data Mapping" section

## Support

For issues or questions:
1. Check `DATA_SCHEMA.md` for data dictionary
2. Review `synthetic_data_generator_lite.py` comments
3. Verify CSV files have expected row counts
4. Check for NULL values: `grep "^$" *.csv`

---

**Generated:** February 1, 2026  
**Pharmaceutical Inventory Optimization Platform – Capstone Project**
