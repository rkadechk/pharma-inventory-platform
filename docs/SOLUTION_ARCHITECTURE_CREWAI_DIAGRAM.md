# High-Level Solution Architecture - CrewAI
## Pharmaceutical Inventory Optimization Platform

This document provides a diagram-friendly architecture overview for the pharmaceutical inventory optimization platform using CrewAI.

---

## 1. System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHARMACEUTICAL INVENTORY                      │
│                  OPTIMIZATION PLATFORM (CrewAI)                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE LAYER                        │
│  (CLI / Jupyter / API - triggers crew execution)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CREWAI ORCHESTRATION LAYER                     │
│  • Manages agent communication                                   │
│  • Sequences tasks (Task1 → Task2 → Task3)                       │
│  • Maintains shared memory between agents                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌─────────┐          ┌──────────┐
   │ AGENT 1 │          │ AGENT 2 │          │ AGENT 3  │
   │ Expiry  │          │Transfer │          │Forecasting
   │Manager  │          │Coordinator         │Analyst
   └────┬────┘          └────┬────┘          └────┬─────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  ┌──────────┐          ┌──────────┐        ┌──────────┐
  │Inventory │          │ Transfer │        │Forecasting
  │  Tools   │          │  Tools   │        │  Tools
  │ (5 tools)│          │(6 tools) │        │(5 tools)
  └────┬─────┘          └────┬─────┘        └────┬─────┘
       │                     │                    │
       └─────────────────────┼────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   DATA LAYER        │
                  │  SQLite Database    │
                  │  (Synthetic Data)   │
                  └─────────────────────┘
```

---

## 2. Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    CREWAI AGENTS                         │
└──────────────────────────────────────────────────────────┘

┌────────────────────┐
│   AGENT 1          │
│ EXPIRATION MANAGER │
├────────────────────┤
│ Role:              │
│ Inventory Analysis │
│                    │
│ Goal:              │
│ Prevent Waste      │
│                    │
│ Memory: ENABLED    │
│ Model: Claude 3.5  │
│ Delegation: NO     │
├────────────────────┤
│ Assigned Tools:    │
│ • query_inventory()│
│ • get_expiring()   │
│ • check_capacity() │
│ • create_alert()   │
│ • get_summary()    │
└────────────────────┘

        ↓ Output: Expiring Items Report

┌────────────────────┐
│   AGENT 2          │
│TRANSFER COORD.     │
├────────────────────┤
│ Role:              │
│ Transfer Optim.    │
│                    │
│ Goal:              │
│ Optimize Distrib.  │
│                    │
│ Memory: ENABLED    │
│ Model: Claude 3.5  │
│ Delegation: NO     │
├────────────────────┤
│ Assigned Tools:    │
│ • find_matches()   │
│ • calc_cost()      │
│ • create_proposal()│
│ • check_comply()   │
│ • approve_xfer()   │
└────────────────────┘

        ↓ Output: Transfer Proposals

┌────────────────────┐
│   AGENT 3          │
│FORECASTING ANAL.   │
├────────────────────┤
│ Role:              │
│ Demand Forecast    │
│                    │
│ Goal:              │
│ Prevent Shortage   │
│                    │
│ Memory: ENABLED    │
│ Model: Claude 3.5  │
│ Delegation: NO     │
├────────────────────┤
│ Assigned Tools:    │
│ • run_forecast()   │
│ • detect_anomaly() │
│ • get_signals()    │
│ • assess_risk()    │
│ • recommend_repl() │
└────────────────────┘

        ↓ Output: Replenishment Strategy
```

---

## 3. Tool Architecture

```
┌─────────────────────────────────────────────────────────┐
│              TOOL LAYER (16 Tools Total)                │
└─────────────────────────────────────────────────────────┘

INVENTORY MANAGEMENT TOOLS (5 tools)
├─ query_inventory()
│  └─ Input: facility_id, medication_id (optional)
│     Output: Inventory details with expiry status
│
├─ get_expiring_medications()
│  └─ Input: days_threshold (default 14)
│     Output: List of expiring items sorted by urgency
│
├─ check_facility_capacity()
│  └─ Input: facility_id
│     Output: Storage utilization %, alert level
│
├─ create_alert()
│  └─ Input: type, severity, facility, message
│     Output: Alert notification sent
│
└─ get_inventory_summary()
   └─ Input: facility_id (optional)
      Output: Total units, value, coverage days


TRANSFER OPTIMIZATION TOOLS (6 tools)
├─ find_transfer_matches()
│  └─ Input: medication_id (optional)
│     Output: List of viable transfer pairs
│
├─ calculate_transfer_cost()
│  └─ Input: from_fac, to_fac, quantity
│     Output: Cost breakdown, distance, total
│
├─ create_transfer_proposal()
│  └─ Input: med_id, from_fac, to_fac, qty, reason
│     Output: Proposal with ID, status, timeline
│
├─ check_regulatory_constraints()
│  └─ Input: med_id, from_fac, to_fac, qty
│     Output: Compliance status, constraints list
│
├─ approve_transfer()
│  └─ Input: proposal_id, approved_by, notes
│     Output: Approval notification, next steps
│
└─ get_transfer_history()
   └─ Input: facility_id (optional), days (30)
      Output: Historical transfer records


DEMAND FORECASTING TOOLS (5 tools)
├─ run_demand_forecast()
│  └─ Input: medication_id, facility_id, days (30)
│     Output: Predictions with confidence intervals
│
├─ detect_demand_anomaly()
│  └─ Input: medication_id, facility_id, days (30)
│     Output: Anomalies with Z-scores, severity
│
├─ get_external_signals()
│  └─ Input: facility_id, signal_type (optional)
│     Output: Weather, disease, seasonal signals
│
├─ assess_stockout_risk()
│  └─ Input: medication_id, facility_id
│     Output: Coverage days, risk level, recommendation
│
└─ recommend_replenishment()
   └─ Input: medication_id, facility_id
      Output: Order quantity, priority, lead time
```

---

## 4. Task Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│              SEQUENTIAL TASK EXECUTION                   │
└─────────────────────────────────────────────────────────┘

TASK 1: EXPIRATION ANALYSIS
═══════════════════════════════════════════════════════════
Agent: Expiration Manager
Tools Used: query_inventory, get_expiring, check_capacity
Duration: ~30 seconds

Process:
  1. Query all inventory across facilities
  2. Identify items expiring within 14 days
  3. Check facility capacity utilization
  4. Calculate at-risk value
  5. Create priority alerts

Input:  (None - starts analysis)
Output: Expiration Report
  ├─ Items expiring within 14 days: 127
  ├─ Total at-risk value: $847,320
  ├─ Facilities at capacity: 3
  ├─ Critical alerts (7 days): 32 items
  └─ Actions required: YES (HIGH priority)

         │
         ▼

TASK 2: TRANSFER COORDINATION
═══════════════════════════════════════════════════════════
Agent: Transfer Coordinator
Tools Used: find_matches, calc_cost, create_proposal, 
            check_comply, approve_xfer
Duration: ~45 seconds

Process:
  1. Analyze Task 1 expiring items
  2. Find surplus/shortage facility pairs
  3. Calculate transfer logistics costs
  4. Check regulatory compliance
  5. Create transfer proposals
  6. Recommend approvals

Input:  Task 1 Output (expiring items + capacity)
Output: Transfer Coordination Report
  ├─ Total viable matches: 42
  ├─ Estimated waste prevention: $42,000
  ├─ Total transfer cost: $18,354 (avg $437/transfer)
  ├─ Compliance constraints: 3 (managed)
  ├─ Ready for approval: 38 transfers
  └─ Requires review: 4 transfers

         │
         ▼

TASK 3: DEMAND FORECASTING & VALIDATION
═══════════════════════════════════════════════════════════
Agent: Forecasting Analyst
Tools Used: run_forecast, detect_anomaly, get_signals,
            assess_risk, recommend_repl
Duration: ~60 seconds

Process:
  1. Review Tasks 1 & 2 findings
  2. Run 30-day demand forecasts
  3. Detect consumption anomalies
  4. Analyze external signals
  5. Assess stockout risks
  6. Adjust transfer recommendations
  7. Recommend replenishment orders

Input:  Task 1 + Task 2 Outputs
Output: Demand Forecasting & Strategy Report
  ├─ Demand spike detected: 5 medications
  ├─ Anomalies found: 12
  ├─ External signals: Flu season +15% demand
  ├─ Stockout risk (7 days): 3 critical
  ├─ Modified transfers: 4 (of 42)
  ├─ Replenishment orders: 23 medications
  └─ Lead time consideration: 3-7 days

         │
         ▼

FINAL OUTPUT: COMPREHENSIVE STRATEGY
═══════════════════════════════════════════════════════════
Combined insights from all three agents:
  • Expiration prevention: $42,000 value
  • Transfer optimization: 38 approved transfers
  • Demand forecasting: 23 replenishment orders
  • Risk assessment: 3 critical, 12 medium
  • Implementation timeline: 24-48 hours
```

---

## 5. Data Flow Architecture

```
┌──────────────────────────────────────────────────────┐
│               DATA FLOW ARCHITECTURE                  │
└──────────────────────────────────────────────────────┘

INPUT DATA SOURCES
══════════════════════════════════════════════════════
  
CSV Files (Synthetic Data)
├─ facilities.csv (10 locations)
├─ medications.csv (3,000 drugs)
├─ inventory.csv (50,000 batches)
├─ consumption.csv (90 days history)
├─ demand_forecast.csv (30-day forecasts)
├─ transfers.csv (transfer history)
├─ replenishment_orders.csv (order history)
└─ external_signals.csv (weather, disease, events)

     │
     ▼

DATA LOADING LAYER
══════════════════════════════════════════════════════

SyntheticDataLoader
├─ load_csv_files()
│  └─ Reads 8 CSV files into Pandas DataFrames
├─ create_sqlite_db()
│  └─ Converts DataFrames to SQLite tables
└─ get_connection()
   └─ Returns SQLite connection for queries

     │
     ▼

DATABASE LAYER
══════════════════════════════════════════════════════

SQLite Database (pharma_dev.db)
├─ facilities (10 rows)
├─ medications (3,000 rows)
├─ inventory (50,000 rows)
├─ consumption (90 × 3,000 = 270,000 rows)
├─ demand_forecast (30 × 3,000 = 90,000 rows)
├─ transfers (1,000 rows)
├─ replenishment_orders (500 rows)
└─ external_signals (500 rows)

Total: 500,000+ data points

     │
     ▼

QUERY INTERFACE
══════════════════════════════════════════════════════

Tools make SQL queries:
├─ Inventory Tools → SELECT from inventory, medications
├─ Transfer Tools → SELECT with JOINs on facilities
└─ Forecasting Tools → SELECT with aggregations

     │
     ▼

AGENT PROCESSING
══════════════════════════════════════════════════════

Agents receive structured data:
├─ Task 1: Raw query results + analysis
├─ Task 2: Task 1 insights + facility matches
└─ Task 3: Tasks 1&2 insights + demand patterns

     │
     ▼

OUTPUT GENERATION
══════════════════════════════════════════════════════

Three reports with reasoning:
├─ Expiration Report
├─ Transfer Proposals
└─ Replenishment Strategy

     │
     ▼

STORAGE & REPORTING
══════════════════════════════════════════════════════

Results (JSON/CSV)
├─ crew_execution_results.json
├─ transfer_proposals.csv
└─ replenishment_orders.csv
```

---

## 6. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              COMPONENT INTERACTION FLOW                      │
└─────────────────────────────────────────────────────────────┘

USER
  │
  ├─ python main.py
  │
  ▼
MAIN.PY
  ├─ Validates prerequisites (API key, data, agents)
  ├─ Creates three agents
  ├─ Assigns tools to agents
  ├─ Defines three tasks
  └─ Calls crew.kickoff()
  │
  ▼
CREWAI ORCHESTRATOR
  │
  ├─ Initialize Crew with agents & tasks
  │
  ├─ EXECUTE TASK 1
  │  └─ Expiration Manager + Inventory Tools
  │     ├─ data_loader.query_inventory()
  │     ├─ data_loader.get_expiring_items()
  │     ├─ data_loader.check_facility_capacity()
  │     └─ Returns: Expiration Report
  │
  ├─ EXECUTE TASK 2 (with Task 1 memory)
  │  └─ Transfer Coordinator + Transfer Tools
  │     ├─ Uses Task 1 output for context
  │     ├─ transfer_tools.find_transfer_matches()
  │     ├─ transfer_tools.calculate_transfer_cost()
  │     ├─ transfer_tools.check_regulatory_constraints()
  │     └─ Returns: Transfer Proposals
  │
  ├─ EXECUTE TASK 3 (with Tasks 1&2 memory)
  │  └─ Forecasting Analyst + Forecasting Tools
  │     ├─ Uses Tasks 1&2 output for context
  │     ├─ forecasting_tools.run_demand_forecast()
  │     ├─ forecasting_tools.detect_demand_anomaly()
  │     ├─ forecasting_tools.assess_stockout_risk()
  │     └─ Returns: Replenishment Strategy
  │
  ▼
RESULTS AGGREGATOR
  │
  ├─ Combines all three task outputs
  ├─ Generates comprehensive strategy
  ├─ Saves to crew_execution_results.json
  │
  ▼
USER (receives comprehensive report)
```

---

## 7. Architecture Layers

```
┌────────────────────────────────────────────────────────────┐
│                 PRESENTATION LAYER                         │
│         (CLI, Jupyter, Future API/Dashboard)               │
└────────────────────┬───────────────────────────────────────┘
                     │
┌────────────────────┴───────────────────────────────────────┐
│                 APPLICATION LAYER                          │
│            (CrewAI Orchestration, Tasks)                   │
│  • Crew initialization                                     │
│  • Task sequencing                                         │
│  • Memory management                                       │
│  • Agent coordination                                      │
└────────────────────┬───────────────────────────────────────┘
                     │
            ┌────────┴────────┐
            │                 │
┌───────────▼────────┐  ┌─────▼──────────────┐
│  AGENT LAYER       │  │  BUSINESS LOGIC    │
│  (3 Agents)        │  │  (Complex Reasoning)
│  • Expiration      │  │  • Cost analysis   │
│  • Transfer        │  │  • Risk assessment │
│  • Forecasting     │  │  • Compliance check│
└────────┬───────────┘  └─────┬──────────────┘
         │                    │
┌────────▼────────────────────▼───────────────┐
│           TOOL LAYER (16 Tools)             │
│  • Inventory (5)                            │
│  • Transfer (6)                             │
│  • Forecasting (5)                          │
└────────┬─────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────┐
│           DATA ACCESS LAYER                  │
│  • SQL query builder                         │
│  • Data transformations                      │
│  • Cache management                          │
└────────┬─────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────┐
│         PERSISTENCE LAYER                    │
│  • SQLite database                           │
│  • CSV files                                 │
│  • JSON results                              │
└───────────────────────────────────────────────┘
```

---

## 8. Integration Points

```
┌────────────────────────────────────────────────────────────┐
│            EXTERNAL INTEGRATION POINTS                      │
└────────────────────────────────────────────────────────────┘

Claude API (Anthropic)
├─ Endpoint: https://api.anthropic.com/v1/messages
├─ Model: claude-3-5-sonnet-20241022
├─ Used by: All 3 agents for reasoning
└─ Configuration: Via ANTHROPIC_API_KEY in .env

Future Integrations (Phase 2+)
├─ Weather API
│  └─ For demand forecasting signals
├─ Disease Surveillance API
│  └─ For outbreak detection
├─ AWS Services
│  └─ Lambda, RDS, DynamoDB, Step Functions
└─ Pharmacy Management ERP
   └─ For real inventory data
```

---

## 9. Deployment Architecture (Phase 4)

```
┌────────────────────────────────────────────────────────────┐
│           FUTURE AWS DEPLOYMENT (Phase 4)                  │
└────────────────────────────────────────────────────────────┘

TIER 1: API GATEWAY
├─ AWS API Gateway
└─ Route requests to Lambda

TIER 2: COMPUTE
├─ AWS Lambda (serverless execution)
│  ├─ crew_executor (main orchestrator)
│  ├─ task_processor_1 (expiration)
│  ├─ task_processor_2 (transfer)
│  └─ task_processor_3 (forecasting)
└─ Concurrency: Auto-scaling based on load

TIER 3: DATA
├─ AWS RDS (PostgreSQL for normalized data)
├─ AWS Redshift (data warehouse for analytics)
└─ AWS DynamoDB (cache for frequent queries)

TIER 4: MESSAGE QUEUE
├─ AWS SQS (job queue)
└─ AWS SNS (notifications to pharmacists)

TIER 5: STORAGE
├─ AWS S3 (results, logs)
└─ AWS CloudWatch (monitoring)

TIER 6: ORCHESTRATION
└─ AWS Step Functions (workflow orchestration)
```

---

## 10. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Multi-Agent Framework** | CrewAI | Role-based, sequential, low boilerplate |
| **LLM Model** | Claude 3.5 Sonnet | Best reasoning, cost-effective, reliable |
| **Database (Dev)** | SQLite | Fast, local, no setup required |
| **Database (Prod)** | PostgreSQL + Redshift | Scalable, reliable, cost-effective |
| **Data Format** | CSV → SQLite | Simple, portable, standard |
| **Task Sequencing** | Sequential (not parallel) | Dependencies between tasks require order |
| **Agent Memory** | Enabled | Agents need context from previous tasks |
| **Tool Assignment** | Explicit by agent | Clear separation of responsibilities |
| **Reasoning Style** | Verbose (enabled) | Healthcare requires explainability |

---

## 11. Success Metrics

```
Performance Metrics
├─ Waste Prevention: $42K+ per execution
├─ Transfer Accuracy: 95%+ compliance
├─ Forecast Error: <15% MAPE
└─ Execution Time: <2 minutes per cycle

Quality Metrics
├─ Decision Explainability: 100%
├─ Regulatory Compliance: 100%
├─ Alert Accuracy: 92%+
└─ Cost Optimization: 20%+ savings

System Metrics
├─ Uptime: 99.9%
├─ Latency: <5 seconds per query
├─ Throughput: 100+ facilities/cycle
└─ Scalability: Handles 10,000+ items
```

---

## 12. Error Handling & Resilience

```
Failure Points & Recovery
════════════════════════════════════════════════════

1. Data Loading Failure
   └─ Recovery: Fallback to cached data, alert user

2. API Rate Limit
   └─ Recovery: Queue job, retry with exponential backoff

3. Database Connection Lost
   └─ Recovery: Reconnect, retry transaction

4. Agent Reasoning Failure
   └─ Recovery: Log error, escalate to human reviewer

5. Tool Execution Error
   └─ Recovery: Return null, let agent handle gracefully

6. Memory Corruption
   └─ Recovery: Reset memory, restart task from beginning

All failures are logged to CloudWatch for monitoring
```

---

## Summary

This architecture provides:

✅ **Modularity** - Each agent and tool is independent
✅ **Scalability** - Can add new agents/tools easily  
✅ **Maintainability** - Clear separation of concerns
✅ **Explainability** - Agents justify decisions
✅ **Reliability** - Multiple fallback mechanisms
✅ **Extensibility** - Ready for AWS deployment

The CrewAI framework orchestrates everything, managing task dependencies and agent memory automatically, allowing you to focus on domain logic rather than boilerplate.

