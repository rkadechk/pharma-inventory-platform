# Pharmaceutical Inventory Optimization Platform
## Capstone Project - Data & Architecture Foundation

**Project:** Pharmaceutical Inventory Optimization Platform for Healthcare Networks  
**Advisor:** Sivakumar Visweswaran  
**Program:** MS in Computer Science, School of Technology & Computing (CityU)  
**Status:** 🟢 Data Generation Complete (Phase 1/5)  
**Date:** February 1, 2026

---

## 📋 Project Overview

### Problem Statement
Healthcare facilities waste **$4.5B annually** on medications due to:
- Medication expiration (shelf-life constraints)
- Demand uncertainty (seasonal spikes, outbreaks)
- Poor coordination (one facility discards excess while another faces shortage)
- Reactive systems (static alerts, manual processes)

### Solution: AI-Driven Inventory Platform
Transform pharmaceutical inventory management from **reactive** (today) to **predictive** (future):
- **Expiration Management:** Proactively identify near-expiry stock across facilities
- **Multi-Facility Coordination:** Enable real-time inventory sharing using AI matching
- **Demand Forecasting:** Anticipate usage spikes using ML + external signals
- **Decision Support:** Interactive Power BI dashboards for pharmacists & administrators

### Expected Impact
- ✅ Reduce medication waste by 30–50%
- ✅ Prevent drug shortages through proactive redistribution
- ✅ Improve patient access and clinical outcomes
- ✅ Support regulatory compliance (audit trails, tracking)
- ✅ Decrease operational costs (logistics optimization)

---

## 🎯 Core Features (4/4 Supported by Data)

### 1️⃣ Expiration Management (Agentic AI)
**Status:** ✅ Data Ready  
**Data Source:** `inventory.csv` (3,000 batches)  
**Key Metric:** 25 items at risk (CRITICAL or HIGH)  
**Technology:** Python agents, AWS Lambda, Step Functions  
**KPIs:**
- Items prevented from expiring (waste reduction)
- Avg days to transfer before expiry
- Success rate of recommended actions

### 2️⃣ Multi-Facility Coordination (Transfer Matching)
**Status:** ✅ Data Ready  
**Data Sources:** `transfers.csv` + `inventory.csv` + `facilities.csv`  
**Key Metric:** 60% transfer success rate (historical)  
**Technology:** Python matching engine, AWS SNS/SQS, optimization algorithms  
**Algorithm Inputs:**
- Geographic distance (minimize cost)
- Facility capacity constraints
- Clinical urgency (expiration risk)
- Regulatory compliance

### 3️⃣ Demand Forecasting (ML)
**Status:** ✅ Data Ready  
**Data Sources:** `consumption.csv` (187K transactions) + `external_signals.csv`  
**Key Metric:** 365 days history + 4,500 forward forecasts  
**Technology:** Prophet (Facebook), SageMaker, Lambda batch jobs  
**Model Features:**
- Time-series decomposition (trend, seasonality)
- External regressors (weather, disease, events)
- Confidence intervals (80%, 95%)
- Anomaly detection

### 4️⃣ Decision Support Analytics (Power BI)
**Status:** ✅ Data Ready  
**Data Schema:** Star (facts + dimensions)  
**Dashboards Planned:**
1. Inventory Health (risk levels, expiration timeline)
2. Transfer Performance (success rate, cost, lead time)
3. Demand vs. Forecast (accuracy, trends, anomalies)
4. Replenishment Orders (on-time rate, supplier performance)

---

## 📊 Synthetic Dataset (Phase 0 - Complete ✅)

### 8 Generated CSV Files
Located in: `data-generation/synthetic_data/`

| File | Rows | Size | Coverage |
|------|------|------|----------|
| `facilities.csv` | 5 | <1 KB | 5 WA healthcare facilities |
| `medications.csv` | 25 | <5 KB | 25 drug SKUs (8 categories) |
| `inventory.csv` | 3,000 | 1.2 MB | Current stock + expiration risk |
| `consumption.csv` | 187,578 | 12 MB | 1-year transaction history |
| `transfers.csv` | 500 | 45 KB | 6-month transfer records |
| `external_signals.csv` | 365 | 40 KB | Daily weather/disease/events |
| `demand_forecast.csv` | 4,500 | 380 KB | 90-day forward predictions |
| `replenishment_orders.csv` | 200 | 18 KB | 3-month purchase history |

**Total:** ~195,978 rows | 15 MB uncompressed | Ready for AWS

### Data Quality ✅
- ✅ No NULL values in required fields
- ✅ Referential integrity (all FKs valid)
- ✅ Logical consistency (dates, quantities)
- ✅ Realistic distributions (seasonality, risk levels)
- ✅ Statistical validity (no impossible values)

---

## 🏗️ Architecture & Tech Stack

### Technology Stack
```
Language:    Python 3.10+
Cloud:       AWS (S3, Glue, Lambda, Redshift/RDS, SageMaker, Step Functions)
BI:          Power BI (DirectQuery or scheduled import)
ML:          Prophet, scikit-learn, PyTorch
Orchestration: AWS Step Functions or Apache Airflow
Monitoring:   CloudWatch, GuardDuty
IaC:         Terraform
CI/CD:       GitHub Actions
```

### High-Level Data Flow
```
Synthetic Data (CSV)
       ↓
    S3 Raw Layer
       ↓
   AWS Glue ETL
       ↓
    S3 Curated Layer (Parquet)
       ↓
  Redshift Data Warehouse
       ├── → Power BI Dashboards
       ├── → Agentic AI Agents
       └── → ML Training Pipeline
```

### Deployment Architecture (AWS)
```
                    ┌─ Power BI (BI)
                    │
    Redshift/RDS ◄──┼─ Lambda/API (Agents & APIs)
         △          │
         │          └─ SageMaker (ML Inference)
         │
    S3 (Curated)
         △
         │
    Glue ETL Job ◄── S3 (Raw)
         △              ▲
         │              │
    Step Functions ──── SNS/SQS (Triggers)
                          │
                    Data Source APIs
                  (Pharmacy Systems, EHRs)
```

---

## 📁 Project Structure

```
pharma-inventory-platform/
│
├── 📦 data-generation/          ✅ COMPLETE (Phase 0)
│   ├── synthetic_data/          (8 CSV files, 195K rows)
│   ├── synthetic_data_generator_lite.py
│   ├── README.md                (Quick start)
│   ├── DATA_SCHEMA.md          (Full data dictionary)
│   └── SUMMARY.md              (Detailed breakdown)
│
├── 🔧 etl/                      📋 NEXT (Phase 1)
│   ├── glue_jobs/
│   │   └── csv_to_parquet.py   (CSV → Parquet transformation)
│   ├── lambdas/
│   │   └── data_loader.py       (S3 → Warehouse)
│   └── requirements.txt
│
├── 📊 dashboards/               📋 PHASE 2
│   ├── power_bi/
│   │   ├── pharma_inventory.pbix
│   │   └── measures.dax
│   └── README.md
│
├── 🤖 agents/                   📋 PHASE 3
│   ├── expiration_manager.py    (Detect near-expiry, recommend actions)
│   ├── transfer_matcher.py      (Multi-criteria facility matching)
│   └── README.md
│
├── 🧠 ml/                       📋 PHASE 3–4
│   ├── demand_forecasting/
│   │   ├── train_prophet.py
│   │   ├── predict.py
│   │   └── model_monitor.py
│   └── requirements.txt
│
├── ☁️ infra/                    📋 PHASE 5
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── s3.tf
│   │   ├── glue.tf
│   │   ├── redshift.tf
│   │   └── lambda.tf
│   ├── github_actions/
│   │   └── deploy.yml
│   └── README.md
│
├── ✅ tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── 📚 docs/
│   ├── architecture.md
│   ├── deployment_guide.md
│   └── troubleshooting.md
│
├── QUICK_REFERENCE.md          (Start here!)
├── README.md                   (Project overview)
└── requirements.txt
```

---

## 🚀 5-Week Implementation Roadmap

### Week 1: ETL + Data Warehouse (Phase 1)
**Goal:** Data warehouse operational with all synthetic data loaded

**Tasks:**
- [ ] Create S3 buckets (raw, curated, archive)
- [ ] Set up IAM roles & policies
- [ ] Create Redshift cluster or RDS Postgres
- [ ] Build Glue Data Catalog (8 table definitions)
- [ ] Implement Glue ETL job (CSV → Parquet)
- [ ] Load data to warehouse
- [ ] Validate schemas, row counts, data types
- [ ] Set up CloudWatch monitoring

**Deliverables:**
- S3 prefix structure: `s3://pharma-inventory-{raw|curated|archive}/`
- Redshift/RDS with 8 tables (indexed, partitioned)
- Glue job scheduled for daily refresh
- Data quality dashboard (CloudWatch)

**Success Metrics:**
- ✅ All 195K rows loaded successfully
- ✅ Schema matches `DATA_SCHEMA.md`
- ✅ Query performance <2s for key dashboards

---

### Week 2: Power BI Dashboards (Phase 2)
**Goal:** Interactive dashboards for stakeholder demo

**Tasks:**
- [ ] Create Power BI data source (DirectQuery/import)
- [ ] Build fact/dimension model (star schema)
- [ ] Implement Dashboard 1: Inventory Health
- [ ] Implement Dashboard 2: Transfer Performance
- [ ] Implement Dashboard 3: Demand vs. Forecast
- [ ] Implement Dashboard 4: Replenishment Orders
- [ ] Add drill-down interactivity (facility → medication → batch)
- [ ] Create KPI cards (waste, transfers, forecast accuracy)
- [ ] Add tooltips & drill-throughs
- [ ] Share with stakeholders (demo access)

**Deliverables:**
- Power BI Desktop file (.pbix)
- 4 operational dashboards
- 15+ KPI measures
- Sample PDF exports

**Success Metrics:**
- ✅ Dashboards load <3s
- ✅ Filters work correctly
- ✅ Stakeholders provide feedback

---

### Week 3–4: Agentic AI + ML (Phases 3–4)
**Goal:** Agents and forecasting models operational

#### Phase 3: Agentic AI (Week 3)
**Tasks:**
- [ ] Implement Expiration Management Agent
  - Query high-risk inventory (CRITICAL, HIGH)
  - Rank by urgency (days_to_expiry)
  - Generate recommendations (use first, transfer, discard)
  - Create alerts (Power BI, email, SMS)
- [ ] Implement Transfer Matching Engine
  - Query source excess + target shortages
  - Multi-criteria optimization (distance, cost, urgency)
  - Generate transfer proposals
  - Integrate human approval workflow
- [ ] Deploy as Python services (Lambda, containers)
- [ ] Schedule daily via Step Functions
- [ ] Integration with Power BI & SNS/email

**Deliverables:**
- 2 Python modules (~500 LOC each)
- Scheduled Lambda/container jobs
- Alert system (SNS, email, Power BI)
- Audit logs (audit table in warehouse)

#### Phase 4: ML + Forecasting (Week 4)
**Tasks:**
- [ ] Prepare data for modeling (consumption + external signals)
- [ ] Train Prophet model (25 series: 5 facilities × 5 medications)
- [ ] Add external regressors (weather, disease, events)
- [ ] Generate 90-day forward forecasts
- [ ] Evaluate model accuracy (MAPE, MAE)
- [ ] Implement drift detection (retrain trigger)
- [ ] Deploy to SageMaker endpoint
- [ ] Schedule batch predictions (daily Lambda)
- [ ] Integrate forecasts into Power BI

**Deliverables:**
- Prophet model (pickled, versioned)
- SageMaker endpoint (inference API)
- Daily batch job (~4,500 forecasts/day)
- Forecast accuracy dashboard
- Model monitoring & alerts

**Success Metrics:**
- ✅ Forecast MAPE <15%
- ✅ Agents generate ≥5 recommendations/day
- ✅ Transfer suggestions have 60%+ acceptance rate

---

### Week 5: Production Hardening (Phase 5)
**Goal:** Platform production-ready

**Tasks:**
- [ ] Implement CI/CD (GitHub Actions)
- [ ] Create Terraform IaC (all resources)
- [ ] Add comprehensive monitoring (CloudWatch dashboards)
- [ ] Implement security (IAM roles, KMS encryption, VPC)
- [ ] Create operational runbooks
- [ ] Perform load testing (1K concurrent users)
- [ ] Security audit & compliance review
- [ ] Create disaster recovery plan
- [ ] Documentation & knowledge transfer

**Deliverables:**
- GitHub Actions workflows (automated tests, deployments)
- Terraform modules (versioned, reusable)
- CloudWatch dashboards (health, performance, costs)
- Security policy & compliance checklist
- Operational runbooks (troubleshooting, escalation)
- DR/BC plan

**Success Metrics:**
- ✅ Zero manual deployments (fully automated)
- ✅ <5min recovery time (RTO)
- ✅ 99.5% uptime (SLA)
- ✅ All security controls passing

---

## 📚 Documentation Guide

### For Stakeholders
Start with: **`QUICK_REFERENCE.md`** (this file summary)
Then: **`README.md`** (project overview & features)

### For Developers
1. **`data-generation/README.md`** – How to run data generator
2. **`data-generation/DATA_SCHEMA.md`** – Complete data dictionary (columns, types, use cases)
3. **`data-generation/SUMMARY.md`** – Phase breakdown & architecture
4. **`QUICK_REFERENCE.md`** – Sample queries & next steps

### For Data Engineers
- **Phase 1:** See `etl/README.md` (Glue, Lambda, Redshift setup)
- **Phase 5:** See `infra/README.md` (Terraform, CI/CD, security)

### For Data Scientists
- **Phase 4:** See `ml/README.md` (Prophet model, training, monitoring)

---

## 🎓 Key Capstone Learning Outcomes

### Technical Skills Demonstrated
1. ✅ **Data Engineering:** ETL pipeline, data warehouse, Glue Data Catalog
2. ✅ **Analytics:** Star schema, Power BI dashboards, KPI design
3. ✅ **AI/ML:** Time-series forecasting, external regressors, model monitoring
4. ✅ **Software Engineering:** Python agents, API design, CI/CD
5. ✅ **Cloud Architecture:** AWS (S3, Glue, Redshift, Lambda, SageMaker)
6. ✅ **System Design:** Multi-agent architecture, event-driven orchestration

### Business Impact
- Reduces pharmaceutical waste by 30–50%
- Prevents drug shortages through proactive redistribution
- Improves patient access & clinical outcomes
- Supports regulatory compliance
- Demonstrates ROI through cost savings

### Real-World Application
- Solves actual problem: $4.5B annual medication waste
- Integrates with healthcare systems (pharmacy, EHR)
- Scales across healthcare networks (5–1,000+ facilities)
- Regulatory-compliant (audit trails, data security)

---

## ✅ Completion Checklist

### Phase 0: Data Generation (✅ COMPLETE)
- ✅ Synthetic data generated (8 CSV files, 195K rows)
- ✅ Data schema documented (`DATA_SCHEMA.md`)
- ✅ All 4 features supported by data
- ✅ Data quality validated
- ✅ Ready for ETL pipeline

### Phase 1: ETL + Warehouse (📋 NEXT)
- ⬜ S3 buckets created
- ⬜ Glue Data Catalog configured
- ⬜ ETL job implemented
- ⬜ Data warehouse loaded
- ⬜ Queries validated

### Phase 2: Power BI Dashboards (📋 PHASE 2)
- ⬜ 4 dashboards created
- ⬜ KPIs defined & implemented
- ⬜ Interactivity added
- ⬜ Stakeholder demo ready

### Phase 3: Agentic AI (📋 PHASE 3)
- ⬜ Expiration agent implemented
- ⬜ Transfer matcher implemented
- ⬜ Scheduled jobs configured
- ⬜ Alert integration complete

### Phase 4: ML & Forecasting (📋 PHASE 4)
- ⬜ Prophet model trained
- ⬜ External regressors added
- ⬜ Batch predictions running
- ⬜ Model monitoring active

### Phase 5: Production (📋 PHASE 5)
- ⬜ CI/CD pipeline operational
- ⬜ IaC (Terraform) complete
- ⬜ Security hardened
- ⬜ Monitoring dashboards live
- ⬜ Documentation complete

---

## 🎯 Next Immediate Actions

### Pick ONE to start Phase 1:

**Option A: Infrastructure First** (Recommended for AWS beginners)
```bash
# 1. Create S3 buckets
aws s3 mb s3://pharma-inventory-raw
aws s3 mb s3://pharma-inventory-curated

# 2. Upload synthetic data
aws s3 cp data-generation/synthetic_data/ \
  s3://pharma-inventory-raw/ --recursive

# 3. Set up Redshift or RDS
# 4. Create Glue tables
```

**Option B: ETL Code First** (For developers)
```python
# Build Glue job or Lambda function
# Input: CSV from S3
# Output: Parquet to curated layer
# Then load to warehouse
```

**Option C: BI First** (For business analysts)
```
# Create Power BI Desktop file
# Load CSV into local Postgres (test)
# Build first dashboard (Inventory Health)
# Get stakeholder feedback
```

---

## 📞 Support & Collaboration

### Team Roles (Suggested)
- **Project Lead:** Project management, stakeholder communication
- **Data Engineer:** Phase 1 (ETL, warehouse, Glue)
- **Data Analyst:** Phase 2 (Power BI dashboards, KPIs)
- **ML Engineer:** Phase 4 (Prophet, model monitoring)
- **DevOps/Cloud Arch:** Phase 5 (Terraform, CI/CD, security)

### Review Checkpoints
- End of Week 1: Data warehouse validated
- End of Week 2: Dashboards reviewed by stakeholders
- End of Week 4: Agents & forecasts tested
- End of Week 5: Security audit passed

---

## 🏆 Success Criteria

### Data Quality ✅
- ✅ All 195,978 rows loaded successfully
- ✅ 100% referential integrity
- ✅ 0 NULL values in required fields
- ✅ Query performance <2s

### Feature Completeness ✅
- ✅ Expiration management: Identifies 25 at-risk items
- ✅ Transfer matching: Suggests 5+ transfers/day
- ✅ Demand forecasting: MAPE <15%
- ✅ Power BI: 4 dashboards, 15+ KPIs

### Production Readiness ✅
- ✅ Automated CI/CD (zero manual steps)
- ✅ Security controls passing
- ✅ 99.5% uptime SLA
- ✅ Disaster recovery plan tested

---

## 📊 Expected Platform Impact (Post-Launch)

### Waste Reduction
- Current: $150K–$250K/hospital/year (waste)
- Target: 30–50% reduction
- Expected: $45K–$125K/hospital/year (savings)

### Shortage Prevention
- Current: 23% of drug shortages preventable
- Target: Prevent 70%+ of preventable shortages
- Expected: Improved patient access, zero critical shortages

### Operational Efficiency
- Transfer lead time: 4.5 → 2 days (faster response)
- Forecast accuracy: Start at 60% → 90%+ with ML
- Manual tasks: 40 → 5 hours/week (90% automation)

---

## 📝 Contact & References

**Project Advisor:** Sivakumar Visweswaran  
**Program:** MS in Computer Science, CityU School of Technology & Computing  
**Capstone Project:** Pharmaceutical Inventory Optimization Platform  
**Start Date:** February 1, 2026  
**Expected Launch:** March 31, 2026

---

## 🎉 Summary

**You now have:**
1. ✅ Realistic synthetic data (195K rows across 8 files)
2. ✅ Complete data schema documentation
3. ✅ Architecture & tech stack defined
4. ✅ 5-week implementation roadmap
5. ✅ Ready to proceed with Phase 1 (ETL + Warehouse)

**Next Action:** Review `QUICK_REFERENCE.md` and choose Phase 1 starting point (Infrastructure, ETL Code, or BI)

**Questions?** Refer to:
- `data-generation/DATA_SCHEMA.md` (data dictionary)
- `data-generation/README.md` (data generation details)
- `data-generation/SUMMARY.md` (full architecture breakdown)

---

**Status:** 🟢 Ready for Phase 1  
**Timeline:** 5 weeks to production  
**Team:** Get together and execute!

Good luck! 🚀
