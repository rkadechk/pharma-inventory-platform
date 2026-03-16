# Quick Reference: Synthetic Data & Next Steps

## 🎯 What We Just Built

Generated **realistic pharmaceutical inventory data** for your 4-feature platform:

### 8 CSV Files Ready (in `synthetic_data/`)
```
✓ facilities.csv           (5 healthcare facilities)
✓ medications.csv          (25 drug SKUs)
✓ inventory.csv            (3,000 batches with expiration risk)
✓ consumption.csv          (187,578 transactions, 1-year history)
✓ transfers.csv            (500 inter-facility transfers)
✓ external_signals.csv     (365 daily weather/disease signals)
✓ demand_forecast.csv      (4,500 90-day forward forecasts)
✓ replenishment_orders.csv (200 purchase orders)
```

**Total:** ~195,978 rows | ~15 MB | Ready for AWS

---

## 📊 Feature Support Matrix

| Feature | Data Source | Status | Next Action |
|---------|-------------|--------|-------------|
| **Expiration Management** | inventory.csv | ✅ Ready | Build agent to query risk items |
| **Transfer Matching** | transfers.csv + inventory.csv | ✅ Ready | Implement multi-criteria matcher |
| **Demand Forecasting** | consumption.csv + signals | ✅ Ready | Train Prophet model |
| **Power BI Dashboards** | All tables | ✅ Ready | Connect to warehouse (Phase 2) |

---

## 🚀 Three-Phase Build Plan

### Phase 1: ETL + Data Warehouse (Week 1)
```bash
# 1. Create S3 buckets
aws s3 mb s3://pharma-inventory-raw
aws s3 mb s3://pharma-inventory-curated

# 2. Upload synthetic data
aws s3 cp synthetic_data/ s3://pharma-inventory-raw/ --recursive

# 3. Create Glue Data Catalog (tables)
# 4. Build Glue ETL job (CSV → Parquet)
# 5. Load to Redshift/RDS
```

**Deliverable:** Data warehouse with 8 tables, ready for BI

---

### Phase 2: Power BI Dashboards (Week 2)
```
1. Connect Power BI to Redshift
2. Create 4 dashboards:
   • Inventory health (expiration risk)
   • Transfer performance (success rate, cost)
   • Demand vs. forecast (accuracy, trends)
   • Replenishment orders (on-time rate)
3. Add drill-down interactivity
4. Share with stakeholders
```

**Deliverable:** Interactive dashboards for decision support

---

### Phase 3: Agents + ML (Week 3–4)
```python
# Expiration Management Agent
SELECT inventory WHERE risk_level IN ('CRITICAL', 'HIGH')
→ Recommend: transfer, prioritize, discard
→ Create notifications

# Transfer Matching Engine
Compare: source excess + target shortage
→ Optimize: distance, cost, urgency
→ Propose transfer (human approval)

# Demand Forecasting
Train Prophet on consumption + external signals
→ Forecast 90 days forward
→ Alert on anomalies
```

**Deliverable:** Automated agents running daily

---

## 📋 Key Data Points

### Expiration Risk (inventory.csv)
```
CRITICAL (≤30 days):  10 items  → Urgent transfers
HIGH (31-90 days):    15 items  → Schedule moves
MEDIUM-LOW (>90 days): 2,975 items → Monitor
```

### Transfer Success Rate (transfers.csv)
```
COMPLETED: 60% (realistic performance)
PENDING:   19%
REJECTED:  21%
Avg Time: 4.5 days
```

### Demand Seasonality (consumption.csv)
```
Winter (Nov-Feb):  +30% demand spike (flu season)
Summer (May-Aug):  -20% lower demand
Average: ~500 transactions/day
```

### Forecast Coverage (demand_forecast.csv)
```
Horizon: 90 days forward
Coverage: 5 facilities × 10 medications
Confidence intervals: 80% & 95%
Method: Prophet (built-in seasonality)
```

---

## 🔧 How to Use Each File

### For ETL Pipeline
```bash
# 1. Load CSVs to Redshift
COPY inventory FROM 's3://pharma-inventory-raw/inventory.csv'
    IAM_ROLE 'arn:aws:iam::ACCOUNT:role/redshift-role'
    IGNOREHEADER 1
    DELIMITER ',';

# 2. Transform to Parquet (Glue job)
# 3. Create curated tables (normalized, indexed)
```

### For Power BI
```
Data Source: Redshift (DirectQuery) or S3 (Parquet)
Tables: Star schema (facts + dimensions)
Relationships:
  - consumption → facilities (facility_id)
  - consumption → medications (medication_id)
  - inventory → facilities, medications
  - transfers → facilities (source/target)
  - forecast → facilities, medications
```

### For Agents (Python)
```python
# Expiration queries
df_risk = pd.read_sql(
    "SELECT * FROM inventory WHERE risk_level IN ('CRITICAL', 'HIGH')",
    conn
)

# Transfer matching
source_excess = query_excess_inventory()
target_shortages = query_forecast_shortages()
matches = match_by_criteria(source_excess, target_shortages)

# Demand forecasting
model = Prophet()
model.fit(consumption_history + external_signals)
forecast = model.predict(periods=90)
```

---

## 📊 Sample Analytics Queries

### 1. Expiration Risk Summary
```sql
SELECT 
  facility_id, 
  COUNT(*) as at_risk_items,
  SUM(quantity_on_hand) as total_units,
  MIN(days_to_expiry) as days_urgent
FROM inventory
WHERE risk_level IN ('CRITICAL', 'HIGH')
GROUP BY facility_id
ORDER BY at_risk_items DESC;
```

### 2. Transfer Success by Facility Pair
```sql
SELECT 
  source_facility_id, 
  target_facility_id,
  COUNT(*) as total_transfers,
  SUM(CASE WHEN transfer_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed,
  ROUND(100.0 * SUM(CASE WHEN transfer_status = 'COMPLETED' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate
FROM transfers
GROUP BY source_facility_id, target_facility_id
ORDER BY success_rate DESC;
```

### 3. Demand Trends by Season
```sql
SELECT 
  DATE_TRUNC('month', transaction_date) as month,
  SUM(quantity) as total_quantity,
  COUNT(*) as transaction_count,
  ROUND(AVG(quantity), 2) as avg_qty_per_transaction
FROM consumption
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month;
```

### 4. Forecast Accuracy (Actual vs. Predicted)
```sql
SELECT 
  f.facility_id,
  f.medication_id,
  f.forecast_date,
  f.forecast_quantity,
  COALESCE(SUM(c.quantity), 0) as actual_quantity,
  ABS(f.forecast_quantity - COALESCE(SUM(c.quantity), 0)) as forecast_error
FROM demand_forecast f
LEFT JOIN consumption c 
  ON f.facility_id = c.facility_id 
  AND f.medication_id = c.medication_id
  AND f.forecast_date = c.transaction_date
GROUP BY f.forecast_id
ORDER BY forecast_error DESC;
```

---

## 🎓 Architecture Overview

```
SYNTHETIC DATA (You Are Here)
           ↓
    ┌──────────┐
    │   ETL    │ Week 1: Glue, Lambda, S3
    │ Pipeline │
    └────┬─────┘
         ↓
   ┌──────────────┐
   │ Data         │ Redshift or RDS PostgreSQL
   │ Warehouse    │ (facts + dimensions)
   └────┬─────────┘
        ├─────────────────────┬────────────────┐
        ↓                     ↓                ↓
   ┌─────────┐         ┌────────────┐   ┌──────────┐
   │ Power   │         │  Agents    │   │   ML     │
   │ BI      │         │  (Python)  │   │ (Prophet)│
   │Dashbrd │         │            │   │          │
   └─────────┘         └────────────┘   └──────────┘
    Week 2              Week 3-4         Week 3-4
```

---

## 🔐 Security Checklist (Before Production)

- [ ] S3 buckets: encryption at rest (KMS)
- [ ] Redshift: encryption enabled, VPC isolated
- [ ] IAM roles: least privilege (separate for Glue, Lambda, Redshift)
- [ ] Data masking: anonymize prescriber_id if needed
- [ ] Audit logs: CloudTrail enabled, S3 access logging
- [ ] Secrets: database credentials in AWS Secrets Manager
- [ ] Network: VPC endpoints for S3, no internet gateway access

---

## 🐛 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| CSV not loading | Check delimiter (`,`), encoding (UTF-8), headers |
| Schema mismatch | Verify column types match data (strings, integers, dates) |
| Missing rows | Check row count in source vs. target |
| Slow queries | Add indexes on facility_id, medication_id, dates |
| Forecast errors | Check for NULL values, date ordering |
| Agent failures | Review logs in CloudWatch, check SQL syntax |

---

## 📚 Documentation Location

All files in: `pharma-inventory-platform/data-generation/`

| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `DATA_SCHEMA.md` | Complete data dictionary (✓ detailed) |
| `SUMMARY.md` | Full phase breakdown |
| `synthetic_data_generator_lite.py` | Source code (customize if needed) |

---

## ✅ Checklist: What's Ready?

- ✅ Synthetic data generated (8 CSV files)
- ✅ Data schema documented
- ✅ All 4 features supported
- ✅ Sample queries provided
- ✅ Integration guide created
- ✅ Next phases outlined

---

## 🎯 Next Immediate Action

**Pick ONE to start Phase 1:**

1. **Option A: AWS Setup**
   - Create S3 buckets, IAM role
   - Set up Glue, Redshift
   - Load synthetic data

2. **Option B: ETL Code**
   - Write Glue job (CSV → Parquet)
   - Create Lambda for data validation
   - Implement data quality checks

3. **Option C: Power BI**
   - Create Power BI Desktop file
   - Connect to local Postgres (test data)
   - Build first dashboard prototype

---

**Capstone Project Status:** 🟢 Data Foundation Complete  
**Ready for:** AWS Infrastructure Setup (Phase 1)  
**Timeline:** 5-week sprint to production  
**Advisor:** Sivakumar Visweswaran (STC, CityU)

**Questions?** Check `DATA_SCHEMA.md` or `README.md`
