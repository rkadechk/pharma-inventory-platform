# Phase 2: Core Agent Implementation

## 🎯 Overview

Phase 2 implements the **3 core agents** that operationalize the pharmaceutical inventory optimization architecture designed in Phase 1.

```
Phase 1 (Architecture) → Phase 2 (Implementation) → Phase 3 (Enhancement)
```

## ✅ What Was Built

### 1. **Data Models** (`agents/models.py` - 380 lines)
Pydantic-based type-safe contracts for all agent I/O.

**Key Models:**
- `InventoryBatch`: Medication batch with expiry tracking
- `TransferRecommendation`: Inventory agent output (cost-benefit analysis)
- `DemandForecast`: ML forecast with anomalies
- `SupplyChainDecision`: Supply chain agent decision
- `SupplyOption`: Reorder vs Transfer comparison
- `AgentMetrics`: Performance tracking

### 2. **Demand Forecasting Agent** (`agents/demand_agent.py` - 350 lines)
Predicts medication demand using ML + external signals.

**Capabilities:**
- Multi-medication forecasting (async)
- **Prophet** time-series model with seasonality
- **ARIMA** fallback model
- Anomaly detection (spike/dip identification)
- External signal integration (disease outbreaks, seasonal trends)
- 30-day forecast with confidence intervals
- MAPE accuracy reporting

**Key Methods:**
```python
await demand_agent.generate_forecasts(
    consumption_history: pd.DataFrame,
    external_signals: List[Dict]
) → List[DemandForecast]

# Individual medication forecast
await demand_agent._forecast_medication(
    medication_id: str,
    history: pd.Series,
    external_signals: List[Dict]
) → DemandForecast
```

**ML Pipeline:**
```
Historical Consumption → Feature Engineering → Prophet/ARIMA
         ↓
    30-Day Forecast + Confidence Interval + Anomalies
```

### 3. **Inventory Optimization Agent** (`agents/inventory_agent.py` - 395 lines)
Identifies at-risk medication batches and recommends waste-prevention transfers.

**Capabilities:**
- Batch-level evaluation (expiry, demand mismatch)
- Transfer opportunity discovery
- Cost-benefit analysis
  - Disposal cost: $18,000 per batch (regulatory)
  - Transfer cost: Distance/volume based
  - ROI: Transfer savings % vs disposal
- Confidence scoring (HIGH/MEDIUM/LOW)

**Key Decision Logic:**
```
At-Risk Batch (expiring < 14 days)
    ↓
Query Demand Forecast
    ↓
├─ No Demand  → DISPOSE ($18K cost)
└─ Has Demand → Find Transfer Options
                      ↓
                  Compare Facilities (capacity, utilization)
                      ↓
                  Calculate Transfer Cost (base + distance + handling)
                      ↓
                  ├─ Cost < Disposal → TRANSFER (save $15K+)
                  └─ No Options → DISPOSE
```

**Key Methods:**
```python
await inventory_agent.evaluate_all_batches(
    inventory_df: pd.DataFrame,
    demand_forecasts: Dict[str, DemandForecast]
) → List[TransferRecommendation]

# Cost-benefit analysis example:
{
    "disposal_cost": 18000,
    "transfer_cost": 2100,
    "savings": 15900,
    "roi": "756%"
}
```

### 4. **Supply Chain Coordination Agent** (`agents/supply_chain_agent.py` - 700 lines)
Makes supply decisions: REORDER from supplier or TRANSFER from other facility?

**Capabilities:**
- Supplier evaluation (price, lead time, reliability)
- Transfer opportunity discovery across facility network
- Cost comparison: Reorder vs Transfer vs Hold
- Lead-time aware optimization
- Risk assessment

**Decision Options:**
1. **REORDER**: Buy from supplier
   - Cost: Unit price × quantity + lead time penalty
   - Lead time: 2-7 days (supplier dependent)
   - Reliability: Based on supplier on-time delivery rate

2. **TRANSFER**: Move stock from sister facility
   - Cost: Base ($500) + distance ($2/mile) + handling
   - Lead time: 4-24 hours (same network)
   - Reliability: 95%+ (internal logistics)

3. **HOLD**: Current stock sufficient
   - No action needed

**Key Methods:**
```python
await supply_chain_agent.optimize_supply(
    facility_id: str,
    medication_id: str,
    current_stock: int,
    demand_forecast: DemandForecast,
    suppliers: List[Supplier],
    facility_inventory: pd.DataFrame,
    transfer_cost_matrix: Dict[tuple, float]
) → SupplyChainDecision

# Example output:
{
    "decision_type": "TRANSFER",
    "from_facility": "FACILITY_B",
    "quantity": 150,
    "total_cost": 1200,
    "lead_time_hours": 4,
    "confidence_score": 0.92,
    "alternative_options": [...]
}
```

### 5. **Orchestrator** (`agents/orchestrator.py` - 650 lines)
Coordinates all 3 agents in an integrated optimization pipeline.

**5-Stage Execution:**
```
Stage 1: Demand Forecasting
    ↓ Generates: DemandForecast for each medication
Stage 2: Inventory Optimization
    ↓ Generates: TransferRecommendation for at-risk batches
Stage 3: Supply Chain Coordination
    ↓ Generates: SupplyChainDecision for supply needs
Stage 4: Action Plan Synthesis
    ↓ Generates: Prioritized action list + risk alerts
Stage 5: System Metrics
    ↓ Generates: Overall health score + impact analysis
```

**Output:**
```python
{
    "status": "completed",
    "execution_time_seconds": 12.34,
    "action_plan": {
        "priority_actions": [...],  # Urgent disposals
        "routine_actions": [...],   # Transfers + reorders
        "risk_alerts": [...]        # High-demand medications
    },
    "system_metrics": {
        "total_facilities": 4,
        "total_medications": 50,
        "stock_value": "$1.2M",
        "system_health_score": 0.87
    },
    "agent_metrics": {
        "demand_agent": {...},
        "inventory_agent": {...},
        "supply_chain_agent": {...}
    }
}
```

### 6. **Main Entry Point** (`phase2_main.py`)
End-to-end orchestration with synthetic data loading and result export.

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│         PharmaceuticalInventoryOrchestrator         │
│  (Coordinates 5-stage optimization pipeline)        │
└────┬──────────────┬──────────────────┬──────────────┘
     │              │                  │
     ↓              ↓                  ↓
┌─────────────┐ ┌──────────────┐ ┌───────────────────┐
│   Demand    │ │ Inventory    │ │  Supply Chain     │
│ Forecasting │ │ Optimization │ │  Coordination     │
│   Agent     │ │    Agent     │ │     Agent         │
└─────────────┘ └──────────────┘ └───────────────────┘
     ↓              ↓                  ↓
  Prophet       Cost Analysis      Supplier/
  ARIMA         Batch Expiry       Transfer
  Anomaly       Transfer Scoring   Comparison
  Detection     Confidence

All agents inherit from BaseAgent (logging, metrics, error handling)
All inputs/outputs validated with Pydantic models
All async methods for scalability
```

## 🚀 How to Use

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Recommended packages are already in requirements.txt:
# - pandas, numpy, scikit-learn
# - prophet, statsmodels (forecasting)
# - pydantic (type validation)
```

### Run Full Optimization
```python
from phase2_main import Phase2MainExecutor
import asyncio

executor = Phase2MainExecutor(db_path="pharma_dev.db")
results = await executor.run_full_optimization()
```

### Use Individual Agents
```python
from agents.demand_agent import DemandForecastingAgent
from agents.inventory_agent import InventoryOptimizationAgent
from agents.supply_chain_agent import SupplyChainCoordinationAgent

# Demand forecasting
demand_agent = DemandForecastingAgent()
forecasts = await demand_agent.generate_forecasts(consumption_history)

# Inventory optimization
inventory_agent = InventoryOptimizationAgent()
recommendations = await inventory_agent.evaluate_all_batches(
    facility_inventory, 
    forecasts
)

# Supply chain decisions
supply_agent = SupplyChainCoordinationAgent()
decision = await supply_agent.optimize_supply(
    facility_id="FACILITY_A",
    medication_id="MED_001",
    current_stock=100,
    demand_forecast=forecasts["MED_001"],
    suppliers=suppliers,
    facility_inventory=facility_inventory,
    transfer_cost_matrix=transfer_costs
)
```

## 📈 Key Metrics & Outputs

### Demand Agent Metrics
```python
{
    "forecasts_generated": 50,
    "average_mape": 0.12,  # 12% forecast error
    "anomalies_detected": 3,
    "medications_with_high_demand": 8
}
```

### Inventory Agent Metrics
```python
{
    "batches_evaluated": 127,
    "at_risk_batches": 8,
    "transfer_recommendations": 5,
    "disposal_recommendations": 3,
    "total_waste_prevented_value": 75600  # $75.6K
}
```

### Supply Chain Agent Metrics
```python
{
    "decisions_made": 8,
    "reorder_decisions": 3,
    "transfer_decisions": 5,
    "total_supply_cost": 12500,
    "average_confidence": 0.88
}
```

### System Level
```python
{
    "stock_coverage_days": 28.5,
    "system_health_score": 0.87,
    "risk_alerts": 2,
    "network_transfer_savings": 45000,
    "net_financial_impact": 28000  # Savings after costs
}
```

## 🔍 Examples

### Example 1: Identifying Expiring Medication
```
Batch: FACILITY_A_MED_001_BATCH_5432
├─ Expiry: 5 days (HIGH RISK)
├─ Current stock: 200 units
├─ Demand forecast: 0 units (no facility needs this medication now)
├─ Decision: DISPOSE
│   ├─ Disposal cost: $18,000 (regulatory)
│   └─ Alternative: No transfer option without demand
└─ Recommendation: Execute disposal within 5 days
```

### Example 2: Optimization Through Transfer
```
Problem: FACILITY_B running low on MED_002 (forecast: 250 units needed in 30d)
    ├─ Current stock: 50 units
    └─ Deficit: 200 units

Solution Options:
    1. TRANSFER from FACILITY_C
       ├─ Available: 180 units
       ├─ Distance: 35 miles
       ├─ Cost: $500 + (35 × $2) + (180 × $0.50) = $620
       └─ Lead time: 4 hours ✓ RECOMMENDED

    2. REORDER from Supplier_A
       ├─ Unit price: $35.00
       ├─ Quantity needed: 200 units
       ├─ Cost: $7,000
       └─ Lead time: 5 days

Decision: TRANSFER
Savings: $7,000 - $620 = $6,380 (91% savings)
+ Faster delivery (4h vs 5 days)
```

### Example 3: Supply Chain Optimization
```
Medication: MED_005 (High demand forecast)
Facility: FACILITY_D
├─ Current stock: 75 units
├─ Forecast: 200 units (30-day)
├─ Deficit: 125 units

Evaluated Options:
    Option 1: Reorder from HealthCare Plus
    ├─ Price: $40/unit × 150 = $6,000
    ├─ Lead time: 2 days
    └─ Reliability: 92%

    Option 2: Reorder from MedExpress
    ├─ Price: $32.50/unit × 150 = $4,875
    ├─ Lead time: 3 days
    └─ Reliability: 98% ✓ RECOMMENDED

    Option 3: Transfer from FACILITY_A
    ├─ Available: 50 units (insufficient)
    └─ Rejected: Doesn't meet demand

Decision: REORDER from MedExpress
Confidence: 0.92 (high reliability + reasonable lead time)
```

## 📁 File Structure

```
agents/
├── __init__.py
├── config.py
├── pharma_agents.py (Phase 1: CrewAI stubs)
├── models.py (NEW - Phase 2: Data models)
├── demand_agent.py (NEW - Phase 2: Forecasting)
├── inventory_agent.py (NEW - Phase 2: Batch optimization)
├── supply_chain_agent.py (NEW - Phase 2: Supply decisions)
└── orchestrator.py (NEW - Phase 2: Coordinator)

phase2_main.py (NEW - Phase 2: Entry point)

database/
├── data_loader.py (Existing: Load synthetic data)
└── __pycache__/

output/
└── optimization_results_<timestamp>.json (NEW: Results export)

pharma_optimization.log (NEW: Execution log)
```

## 🔗 Integration with Phase 1

**Phase 1 Created:**
- Architecture design (6 agents → 3 core agents)
- Database schema
- Data source mappings
- UI/UX designs
- Knowledge graph design
- Interview Q&A

**Phase 2 Implementation:**
- ✅ 3 core agents fully coded
- ✅ Pydantic models for type safety
- ✅ Async execution for scalability
- ✅ ML forecasting pipeline
- ✅ Cost optimization
- ✅ Orchestrator for integration

**Phase 3 Will Add:**
- 3 enhancement agents (Compliance, Analytics, Alert/Response)
- Kafka/async messaging between agents
- FastAPI REST endpoints
- Real-time streaming data
- Dashboard implementation
- Monitoring & alerting
- Docker containerization

## 🧪 Testing

### Unit Tests (Ready to implement)
```bash
pytest tests/test_demand_agent.py
pytest tests/test_inventory_agent.py
pytest tests/test_supply_chain_agent.py
pytest tests/test_orchestrator.py
```

### Integration Tests (Ready to implement)
```bash
pytest tests/integration/test_full_pipeline.py
```

### Load Testing (Ready to implement)
```bash
# Test with 1000 medications, 20 facilities
pytest tests/performance/test_load.py
```

## 📝 Code Quality

- ✅ Type hints throughout (Pydantic validation)
- ✅ Logging for debugging and monitoring
- ✅ Async/await for concurrency
- ✅ Error handling and recovery
- ✅ Metrics tracking per agent
- ✅ Docstrings on all public methods
- ✅ DRY principle (BaseAgent inheritance)

## 🎓 Interview Readiness

This Phase 2 implementation demonstrates:

1. **System Design**
   - Multi-agent architecture
   - Separation of concerns
   - Async/concurrent processing

2. **Data Science**
   - Time-series forecasting (Prophet, ARIMA)
   - Anomaly detection
   - Feature engineering

3. **Business Logic**
   - Cost optimization
   - Confidence scoring
   - Risk assessment

4. **Software Engineering**
   - Type safety (Pydantic)
   - Error handling
   - Logging/monitoring
   - Clean code patterns

5. **Domain Knowledge**
   - Pharmaceutical inventory challenges
   - Regulatory constraints
   - Supply chain optimization

## 🚀 Next Steps (Phase 3)

1. **Complete Enhancement Agents**
   - Compliance & Quality Agent
   - Analytics & Insights Agent
   - Alert & Response Agent

2. **Agent Communication**
   - Kafka message queue
   - Async event-driven system

3. **API Exposure**
   - FastAPI REST endpoints
   - WebSocket for real-time updates

4. **Deployment**
   - Docker containerization
   - Kubernetes manifests
   - CI/CD pipeline

5. **Monitoring**
   - ELK stack integration
   - Performance dashboards
   - Alerting rules

## 📚 References

- [Phase 1 Architecture](docs/ARCHITECTURE_AND_PHASES.md)
- [Data Schema](docs/DATA_SCHEMA.md)
- [Development Approach](docs/DEVELOPMENT_APPROACH.md)

---

**Phase 2 Complete**: 3 core agents operational, orchestrator integrated, ready for Phase 3 enhancement.
