# CrewAI + PowerBI + FastAPI Architecture Overview

## 🏗️ Complete Pharmaceutical Platform Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                               │
├─────────────────────┬─────────────────────┬─────────────────────┤
│   PowerBI Desktop   │  API Integration    │   Mobile/Web App    │
│  (Dashboards)       │  (Custom Apps)      │  (Future)           │
└──────────┬──────────┴──────────┬──────────┴──────────┬───────────┘
           │                     │                     │
┌──────────▼───────────────────────────────────────────▼───────────┐
│                    FASTAPI WEB LAYER (port 8000)                  │
├──────────────────────────────────────────────────────────────────┤
│  Routes:                                                           │
│  ├─ /api/v1/health (status checks)                               │
│  ├─ /api/v1/optimization/* (7 existing routes)                   │
│  ├─ /api/v1/demand/* (demand forecasts)                          │
│  ├─ /api/v1/inventory/* (inventory analysis)                     │
│  ├─ /api/v1/supply/* (supply chain)                              │
│  ├─ /api/v1/powerbi/* (3 dashboard endpoints)                    │
│  └─ /api/v1/crew/* (4 CrewAI agent endpoints) ← NEW!            │
└──────────┬──────────────────────────────────────────────────────┘
           │
    ┌──────▼──────────┐
    │   BUSINESS      │
    │    LOGIC        │
    │    LAYER        │
    └──┬──────────────┘
       │
       ├─────────────────┬──────────────────────┬────────────────┐
       │                 │                      │                │
┌──────▼───────┐  ┌──────▼──────────┐  ┌───────▼────────┐  ┌────▼─────────┐
│   FastAPI    │  │  Data Loaders   │  │   CrewAI       │  │  Validators  │
│  (Existing)  │  │  (CSV-based)    │  │   Agents       │  │  (Existing)  │
│              │  │                 │  │                │  │              │
│ - Health     │  │ - inventory.csv │  │ ✅ Risk Agent │  │ - Pydantic   │
│ - Endpoints  │  │ - transfers.csv │  │ ✅ Opt Agent  │  │ - 255 tests  │
│ - Routes     │  │ - forecast.csv  │  │ ✅ Demand Ag. │  │              │
│              │  │ - medicinal.csv │  │ ✅ Report Ag. │  │              │
└──────────────┘  │ - facility.csv  │  └──────┬────────┘  └──────────────┘
                  └──────────────────┘         │
                                               │
                       ┌─────────────────────────┘
                       │
                ┌──────▼──────────────────────┐
                │   LLM INTEGRATION          │
                ├────────────────────────────┤
                │  - Langchain               │
                │  - OpenAI (GPT-4-Turbo)    │
                │  - CrewAI Framework        │
                │                            │
                │  Agents Coordinate:        │
                │  - Sequential reasoning    │
                │  - Data analysis           │
                │  - Recommendations         │
                │  - Report synthesis        │
                └────────────────────────────┘
                         │
             ┌───────────▼──────────┐
             │   DATA SOURCES       │
             ├──────────────────────┤
             │  CSVs (196K records) │
             │  ├─ inventory        │  3,000 records
             │  ├─ transfers        │    500 records
             │  ├─ forecasts        │  4,500 records
             │  ├─ consumption      │187,579 records
             │  └─ others           │      600 records
             │                      │
             │ (Real synthetic data │
             │  from generators)    │
             └──────────────────────┘
```

---

## 🔄 Data Flow Examples

### Scenario 1: User Views PowerBI Dashboard

```
1. User opens PowerBI Desktop
2. Loads data from: /api/v1/powerbi/export/expiration-risk?format=json
3. API loads: inventory.csv + medications.csv + facilities.csv
4. PowerBI renders 3 dashboards with 3,000+ records
5. User sees visual analytics
```

### Scenario 2: User Requests AI Analysis

```
1. User calls: POST /api/v1/crew/analyze/expiration-risk
2. FastAPI route receives request
3. PharmacyCrew loads all CSV data
4. ExpirationRiskAnalyst calculates metrics (34 critical, $245K risk)
5. CrewAI Risk Agent (GPT-4) analyzes this data
6. Agent generates recommendations
7. Response returned in 45 seconds
```

### Scenario 3: Full Assessment (Multi-Agent)

```
1. User calls: POST /api/v1/crew/analyze/full-assessment
2. PharmacyCrew loads all data (8,000+ records)
3. Agents run sequentially:
   a) Risk Agent analyzes expiration risks
   b) Optimization Agent analyzes transfers
   c) Demand Agent analyzes forecasts
   d) Report Agent synthesizes all findings
4. Each agent sends context to GPT-4 for reasoning
5. Final executive report generated
6. Response returned in 1-2 minutes
```

---

## 📊 Data Integration Points

### PowerBI Integration
```
PowerBI Desktop
    ↓
Web.Contents("http://localhost:8000/api/v1/powerbi/export/...")
    ↓
FastAPI Route (powerbi.py)
    ↓
CSV Data Loaders
    ↓
PowerBI Refresh (3-5 sec)
    ↓
Dashboards Update
```

### CrewAI Integration
```
API Client (curl/Python/etc)
    ↓
POST /api/v1/crew/analyze/*
    ↓
FastAPI Route (crew.py)
    ↓
PharmacyCrew Initialization
    ↓
Data Loaders (CSV)
    ↓
CrewAI Agents
    ↓
GPT-4-Turbo (LLM)
    ↓
AI Recommendations (JSON)
```

---

## 🎯 Use Case: Daily Operations

### 8:00 AM - Start of Day

```bash
# 1. Get AI risk assessment
curl -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk

# 2. Risk Summary
# "34 critical batches, $245K at-risk"
# "Recommend immediate transfers to 5 facilities"
# "Can reduce waste by 95%"

# 3. Team reviews recommendations
# 4. Execute approved transfers
```

### 10:00 AM - Before Transfer Approval

```bash
# 1. Get transfer optimization recommendations
curl -X POST http://localhost:8000/api/v1/crew/analyze/transfer-optimization

# 2. Transfer Recommendations
# "Top 3 transfers generate $45K savings"
# "Hospital A → Hospital B: $12K savings"
# "Clinic C → Hospital D: $8K savings"

# 3. Approve and execute
# 4. Monitor in PowerBI (real-time update)
```

### 2:00 PM - Reorder Planning

```bash
# 1. Get demand forecast analysis
curl -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast

# 2. Forecast Analysis
# "12 medications at critical urgency"
# "Recommend orders: 500 units Amoxicillin, 300 units Ibuprofen"
# "Expected demand spike due to flu season signal"

# 3. Place orders with procurement
```

### 4:00 PM - Weekly Review

```bash
# 1. Get comprehensive assessment
curl -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment

# 2. Executive Report Includes:
# - Risk summary with recommendations
# - Top 10 transfer opportunities
# - Demand forecast highlights
# - Financial impact ($XXK savings potential)
# - Implementation timeline

# 3. Share report with leadership
# 4. Update PowerBI dashboards
```

---

## 🔧 Technical Stack

### Core Components
| Component | Purpose | Status |
|-----------|---------|--------|
| **FastAPI** | Web framework | ✅ Active |
| **Uvicorn** | ASGI server | ✅ Active |
| **Pandas** | Data processing | ✅ Active |
| **Pydantic** | Data validation | ✅ Active |
| **SQLite/CSV** | Data storage | ✅ Active |

### Intelligence Layer (NEW)
| Component | Purpose | Status |
|-----------|---------|--------|
| **CrewAI** | Agent orchestration | ✅ NEW |
| **Langchain** | LLM integration | ✅ NEW |
| **OpenAI GPT-4** | Reasoning engine | ✅ NEW |

### Visualization
| Component | Purpose | Status |
|-----------|---------|--------|
| **PowerBI** | Dashboards | ✅ Active |
| **Web UI** | JSON APIs | ✅ Active |

---

## 📈 Capability Matrix

### Before CrewAI
```
Data Available: ✅ (8,000+ records from CSVs)
Dashboards: ✅ (PowerBI with real data)
Analysis: ⚠️ (Manual only)
Recommendations: ⚠️ (Manual only)
Executive Reports: ⚠️ (Manual only)
Intelligence: ❌ (Not present)
```

### After CrewAI
```
Data Available: ✅ (8,000+ records from CSVs)
Dashboards: ✅ (PowerBI with real data)
Analysis: ✅ (AI-powered analysis)
Recommendations: ✅ (AI-generated, prioritized)
Executive Reports: ✅ (AI-synthesized)
Intelligence: ✅ (4 specialized AI agents)
```

---

## 🚀 Deployment Architecture

### Local Development
```
Your Computer
├─ FastAPI (localhost:8000)
├─ PowerBI Desktop
├─ CrewAI Agents (GPT-4 via API)
└─ CSVs (local storage)
```

### Cloud Ready (Future)
```
AWS/Azure
├─ FastAPI (ECS/ACI)
├─ PowerBI Service
├─ CrewAI Dashboard (Lambda/Functions)
├─ S3/Blob Storage (CSVs)
└─ CloudWatch/Logs
```

---

## 📊 API Endpoints Summary

### Data Endpoints (PowerBI)
- `GET /api/v1/powerbi/export/expiration-risk` (3,000 rows)
- `GET /api/v1/powerbi/export/transfer-coordination` (500 rows)
- `GET /api/v1/powerbi/export/demand-forecast` (4,500 rows)
- `GET /api/v1/powerbi/export/summary-statistics` (KPIs)

### CrewAI Endpoints
- `POST /api/v1/crew/analyze/expiration-risk` (30-60s)
- `POST /api/v1/crew/analyze/transfer-optimization` (30-60s)
- `POST /api/v1/crew/analyze/demand-forecast` (30-60s)
- `POST /api/v1/crew/analyze/full-assessment` (1-2m)
- `GET /api/v1/crew/status` (agent status)
- `GET /api/v1/crew/docs/agents` (documentation)

### Existing Endpoints
- `GET /api/v1/health` (system status)
- `POST /api/v1/optimization/run` (optimization pipeline)
- `POST /api/v1/demand/forecast` (demand forecasting)
- ... (7+ more existing routes)

---

## 🎓 Architecture Benefits

### Scalability
- Add new agents without changing core API
- Scale LLM calls independently
- Cache results for repeated requests

### Maintainability
- Clean separation of concerns
- FastAPI handles routing
- CrewAI handles orchestration
- Pandas handles data

### Flexibility
- PowerBI for visualization
- CrewAI for intelligence
- Existing endpoints for operations
- All parts work together

### Extensibility
- Add new data sources (databases, APIs)
- Add new agents (more specialized roles)
- Add new dashboards (PowerBI)
- Build custom applications on top

---

## 🎯 Why This Architecture?

1. **Best of Both Worlds**
   - PowerBI: Visual analytics you know
   - CrewAI: AI intelligence you just added

2. **Real Data**
   - No hardcoded samples
   - 196K+ records to analyze
   - Live-updated CSVs

3. **Accessible**
   - Simple API endpoints
   - No special tools needed
   - Just curl or Python

4. **Powerful**
   - MutliAgent coordination
   - LLM reasoning on your data
   - Executive-grade insights

5. **Cost Effective**
   - Local architecture
   - Only pay for LLM calls (~$50/month)
   - No cloud infrastructure needed

---

## 📚 Documentation Structure

```
pharma-inventory-platform/
├─ README.md (overview)
├─ CREWAI_QUICK_START.md (get started in 5 min)
├─ CREWAI_INTEGRATION_GUIDE.md (complete reference)
├─ CREWAI_ARCHITECTURE.md (this file)
├─ POWERBI_QUICK_START.md (dashboard guide)
├─ POWERBI_EXACT_LAYOUT_GUIDE.md (detailed specs)
├─ POWERBI_DATA_INTEGRATION_COMPLETE.md (data endpoints)
└─ app/
   ├─ main.py (FastAPI app)
   ├─ routes/
   │  ├─ crew.py (CrewAI endpoints)
   │  ├─ powerbi.py (PowerBI data export)
   │  └─ (other routes)
   └─ agents/
      └─ crewai_pharmacy.py (agent definitions)
```

---

**Created:** February 19, 2025
**Status:** ✅ Ready to Deploy
**Next:** Follow CREWAI_QUICK_START.md to get running in 5 minutes
