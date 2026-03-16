# 🏗️ PHARMACEUTICAL INVENTORY PLATFORM - CREWAI ARCHITECTURE

**Updated Architecture:** CrewAI (Agent Development Kit) + AWS Services  
**Date:** February 4, 2026  
**Status:** Architecture Design Phase

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

### High-Level Architecture (CrewAI Approach)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHARMACEUTICAL INVENTORY PLATFORM                          │
│              (CrewAI Multi-Agent Framework + ETL + ML + Power BI + AWS)     │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ▼

        ┌──────────────────────────────────────────────────────────┐
        │                    DATA SOURCES                          │
        │  • Hospital pharmacy systems (APIs)                      │
        │  • CSV/Excel files (legacy systems)                      │
        │  • Real-time inventory updates                           │
        │  • External data (weather, disease, events)              │
        └──────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │              INGESTION & RAW DATA LAYER                 │
        │  • AWS S3 (raw bucket)                                  │
        │  • Lambda functions (data collectors)                   │
        │  • API Gateway (data intake endpoints)                  │
        │  • Glue Crawlers (metadata discovery)                   │
        └──────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │             ETL & DATA TRANSFORMATION                   │
        │  • AWS Glue jobs (PySpark/Python)                       │
        │  • Airflow (orchestration & scheduling)                 │
        │  • Step Functions (workflow management)                 │
        │  • Data validation & quality checks                     │
        └──────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │           CURATED DATA LAYER                            │
        │  • S3 (curated/processed bucket)                         │
        │  • Parquet format (optimized)                           │
        │  • Glue Data Catalog (metadata)                         │
        │  • Data lineage tracking                                │
        └──────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │           DATA WAREHOUSE LAYER                          │
        │  • AWS Redshift (analytic warehouse)                    │
        │  • RDS PostgreSQL (relational DB)                       │
        │  • Optimized schemas for queries                        │
        │  • Aggregated tables & materialized views               │
        └──────────┬───────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────────┬──────────────────┐
    │              │                  │                  │
    ▼              ▼                  ▼                  ▼
┌────────────┐ ┌──────────┐   ┌────────────┐    ┌──────────────┐
│   CREWAI   │ │   ML     │   │   POWER    │    │   ANALYTICS  │
│   AGENTS   │ │  MODELS  │   │     BI     │    │   & INSIGHTS │
│  (Crew)    │ │ (Prophet) │  │ DASHBOARDS │    │              │
└─────┬──────┘ └────┬─────┘   └─────┬──────┘    └──────┬───────┘
      │             │               │                  │
      └─────────────┴───────────────┴──────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │         DECISION SUPPORT & ACTION LAYER                 │
        │  • CrewAI task outputs (recommendations)                │
        │  • Transfer proposals (multi-agent coordination)        │
        │  • Alerts & notifications (SNS/SES)                     │
        │  • Automated actions (with human approval)              │
        │  • Audit trail & compliance logging                     │
        └──────────┬───────────────────────────────────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │         OBSERVABILITY & GOVERNANCE                      │
        │  • CloudWatch (monitoring/logging)                      │
        │  • X-Ray (distributed tracing)                          │
        │  • CloudTrail (audit logs)                              │
        │  • Cost monitoring & alerts                             │
        │  • Data governance & compliance                         │
        │  • CrewAI agent performance metrics                     │
        └──────────────────────────────────────────────────────────┘
```

---

## 🤖 CREWAI FRAMEWORK OVERVIEW

### What is CrewAI?

CrewAI is an **Agent Development Kit (ADK)** that simplifies building **multi-agent systems** by organizing agents into **Crews** with defined **Roles**, **Tasks**, and **Processes**.

**Key Advantages:**
- ✅ Simple role-based agent definition
- ✅ Built-in collaboration between agents
- ✅ Sequential or hierarchical process management
- ✅ Easy integration with LLMs (Claude, GPT, etc.)
- ✅ Type-safe tool definitions
- ✅ Memory management (short-term & long-term)
- ✅ Minimal boilerplate code

### CrewAI Core Concepts

```
┌────────────────────────────────────────────────────────────────┐
│                         CREW (Team)                            │
│  "Pharmaceutical Inventory Management Crew"                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │      AGENT 1         │  │      AGENT 2         │           │
│  │  Expiration Manager  │  │ Transfer Coordinator │           │
│  │                      │  │                      │           │
│  │  Role: Monitor and   │  │  Role: Match surplus │           │
│  │  identify near-      │  │  at one facility     │           │
│  │  expiry medications  │  │  with shortage at    │           │
│  │                      │  │  another             │           │
│  │  Tools:              │  │                      │           │
│  │  • query_inventory() │  │  Tools:              │           │
│  │  • check_expiry()    │  │  • find_matches()    │           │
│  │  • create_alert()    │  │  • calc_transfer()   │           │
│  │                      │  │  • create_proposal() │           │
│  └──────────────────────┘  └──────────────────────┘           │
│           ▲                           ▲                        │
│           │ Agent 1 Output            │ Agent 1 & 2 Output    │
│           │ (Expiring items)          │ (Transfer proposals)   │
│           │                           │                       │
│  ┌────────▼───────────────────────────▼──────┐               │
│  │            TASKS (Work Queue)              │               │
│  │                                            │               │
│  │  Task 1: Analyze Expiring Inventory      │               │
│  │  └─ Agent: Expiration Manager            │               │
│  │  └─ Input: All inventory data            │               │
│  │  └─ Output: List of critical items       │               │
│  │                                            │               │
│  │  Task 2: Find Transfer Opportunities     │               │
│  │  └─ Agent: Transfer Coordinator          │               │
│  │  └─ Input: Output from Task 1            │               │
│  │  └─ Output: Transfer proposals            │               │
│  │                                            │               │
│  │  Task 3: Check Forecasting Risks         │               │
│  │  └─ Agent: Forecasting Agent             │               │
│  │  └─ Input: All data + proposals          │               │
│  │  └─ Output: Risk alerts & recommendations│               │
│  │                                            │               │
│  └────────────────────────────────────────────┘               │
│                      ▲                                         │
│                      │                                         │
│  ┌──────────────────┴────────────────────┐                   │
│  │     PROCESS (Workflow Manager)         │                   │
│  │     Sequential / Hierarchical          │                   │
│  │     Error Handling & Retries            │                   │
│  │     Memory Management                   │                   │
│  └────────────────────────────────────────┘                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 👥 CREW COMPOSITION: THREE SPECIALIZED AGENTS

### Agent 1: Expiration Management Agent

```python
# agents/expiration_agent.py

from crewai import Agent
from tools.inventory_tools import (
    query_inventory,
    check_facility_capacity,
    create_alert
)

expiration_manager = Agent(
    role="Inventory Expiration Manager",
    goal="Identify medications at risk of expiration and prevent waste",
    backstory="""
    You are an expert pharmaceutical inventory analyst with 10 years 
    of experience in healthcare supply chain management. Your primary 
    responsibility is to monitor medication expiration dates across 
    all 20 facilities and ensure no valuable medications are wasted.
    
    You understand regulatory requirements, storage constraints, and 
    the urgency of identifying items expiring within 7-14 days.
    """,
    tools=[query_inventory, check_facility_capacity, create_alert],
    llm=claude_client,  # Uses Claude 3.5 Sonnet
    memory=True,        # Maintains conversation history
    verbose=True        # Log all decisions
)
```

### Agent 2: Transfer Coordination Agent

```python
# agents/transfer_agent.py

from crewai import Agent
from tools.transfer_tools import (
    find_transfer_matches,
    calculate_transfer_cost,
    create_transfer_proposal,
    check_regulatory_constraints
)

transfer_coordinator = Agent(
    role="Multi-Facility Transfer Coordinator",
    goal="Optimize pharmaceutical inventory distribution across facilities",
    backstory="""
    You are a logistics and inventory optimization specialist. Your role 
    is to identify where medications are in surplus at one facility and 
    needed at another, then coordinate cost-effective transfers.
    
    You consider distance, regulatory compliance, storage capacity, and 
    transfer costs. You understand that coordinating transfers between 
    facilities can save lives by preventing shortages while reducing waste.
    """,
    tools=[
        find_transfer_matches,
        calculate_transfer_cost,
        create_transfer_proposal,
        check_regulatory_constraints
    ],
    llm=claude_client,
    memory=True,
    verbose=True
)
```

### Agent 3: Forecasting & Risk Agent

```python
# agents/forecasting_agent.py

from crewai import Agent
from tools.forecasting_tools import (
    run_demand_forecast,
    get_external_signals,
    detect_demand_anomaly,
    recommend_replenishment
)

forecasting_analyst = Agent(
    role="Demand Forecasting & Risk Analyst",
    goal="Predict demand spikes and prevent medication shortages",
    backstory="""
    You are a data scientist specializing in healthcare demand forecasting. 
    You use machine learning models, weather patterns, disease surveillance data, 
    and historical consumption patterns to predict future demand.
    
    Your insights help procurement teams order the right quantities at the 
    right time, preventing both shortages and excess inventory.
    """,
    tools=[
        run_demand_forecast,
        get_external_signals,
        detect_demand_anomaly,
        recommend_replenishment
    ],
    llm=claude_client,
    memory=True,
    verbose=True
)
```

---

## 📋 TASK DEFINITIONS

### Task 1: Analyze Expiring Inventory

```python
# tasks/expiration_tasks.py

from crewai import Task

analyze_expiring_task = Task(
    description="""
    Analyze current inventory data and identify all medications expiring 
    within 14 days. For each critical item (expiring within 7 days):
    
    1. Query the inventory database for items with days_to_expiry < 14
    2. Check facility storage capacity constraints
    3. Categorize by urgency (CRITICAL: < 7 days, WARNING: 7-14 days)
    4. Estimate financial impact (units × unit_cost)
    5. Flag items that must be transferred or safely disposed of
    
    Provide a comprehensive report with:
    - Total items at risk
    - High-risk items requiring immediate action
    - Estimated waste value if no action taken
    - Recommended actions for each item
    """,
    agent=expiration_manager,
    expected_output="""
    A structured report containing:
    - Summary: 500 items expiring, 25 critical
    - Critical items list with expiry dates and quantities
    - Financial impact: $125,000 potential waste
    - Preliminary actions: X items need transfers, Y items for disposal
    """
)
```

### Task 2: Find Transfer Opportunities

```python
# tasks/transfer_tasks.py

from crewai import Task

find_transfer_opportunities_task = Task(
    description="""
    Based on the expiring inventory analysis, find facilities that need 
    the identified medications and can receive transfers.
    
    For each critical medication:
    1. Identify which facilities have surplus (expiring items)
    2. Identify which facilities need the medication (below reorder point)
    3. Calculate transfer costs (distance, handling, insurance)
    4. Check regulatory constraints (state-to-state transfers, cold chain)
    5. Create optimal transfer proposals
    
    Prioritize transfers that:
    - Prevent the most waste (high-value items)
    - Prevent the most shortages (urgent needs)
    - Cost the least to execute
    - Comply with all regulations
    """,
    agent=transfer_coordinator,
    expected_output="""
    Transfer coordination plan containing:
    - 12 transfer proposals (from → to, medication, qty)
    - Cost analysis for each: $412.50 average
    - Total cost: $5,250, savings: $42,500
    - Compliance status: All transfers approved
    - Execution timeline: Ready for approval
    """
)
```

### Task 3: Assess Forecasting Risks

```python
# tasks/forecasting_tasks.py

from crewai import Task

assess_forecasting_risks_task = Task(
    description="""
    Review demand forecasts and external signals to assess whether 
    proposed transfers and current inventory levels are adequate.
    
    Steps:
    1. Run 30-day demand forecasts for critical medications
    2. Check external signals (weather, disease, events)
    3. Detect anomalies in consumption patterns
    4. Evaluate if transfer proposals address shortage risks
    5. Identify any items still at risk despite transfers
    6. Recommend preventive restocking
    
    Consider:
    - Seasonal patterns (flu season, summer allergies)
    - Disease outbreaks (local epidemiological data)
    - Weather impacts (storms, temperature extremes)
    - Special events (conferences, holidays)
    """,
    agent=forecasting_analyst,
    expected_output="""
    Risk assessment report:
    - Forecast summary: 40% spike predicted in respiratory meds next week
    - Anomalies detected: 3 facilities showing unusual consumption
    - Transfer assessment: Proposed transfers cover 85% of predicted shortage
    - Additional risk: 15% shortage risk for 2 items
    - Recommendations: Rush order 500 units of Item X
    - Confidence level: 92%
    """
)
```

---

## 🚀 CREW SETUP & EXECUTION

### Crew Definition

```python
# crew/pharma_crew.py

from crewai import Crew, Process
from agents.expiration_agent import expiration_manager
from agents.transfer_agent import transfer_coordinator
from agents.forecasting_agent import forecasting_analyst
from tasks.expiration_tasks import analyze_expiring_task
from tasks.transfer_tasks import find_transfer_opportunities_task
from tasks.forecasting_tasks import assess_forecasting_risks_task

pharma_inventory_crew = Crew(
    agents=[
        expiration_manager,
        transfer_coordinator,
        forecasting_analyst
    ],
    tasks=[
        analyze_expiring_task,
        find_transfer_opportunities_task,
        assess_forecasting_risks_task
    ],
    process=Process.SEQUENTIAL,  # Tasks execute in order
    verbose=True,
    memory=True  # Agents remember context between tasks
)
```

### Execution Flow

```python
# main.py - Lambda Handler

from crew.pharma_crew import pharma_inventory_crew
import json
import boto3

def lambda_handler(event, context):
    """
    Triggered by CloudWatch Events (hourly)
    Executes the PharmaceuticalInventory Crew
    """
    
    try:
        print("Starting Pharmaceutical Inventory Crew...")
        
        # Kick off crew execution
        result = pharma_inventory_crew.kickoff(
            inputs={
                "current_datetime": datetime.now().isoformat(),
                "facilities_count": 20,
                "critical_threshold_days": 7,
                "warning_threshold_days": 14
            }
        )
        
        print("Crew execution completed successfully")
        print(f"Output: {result}")
        
        # Parse and persist results
        recommendations = parse_crew_output(result)
        
        # Store in DynamoDB for audit trail
        persist_recommendations(recommendations)
        
        # Send notifications
        send_notifications(recommendations)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Crew executed successfully",
                "proposals_created": len(recommendations["transfers"]),
                "alerts_sent": len(recommendations["alerts"])
            })
        }
        
    except Exception as e:
        print(f"Error executing crew: {str(e)}")
        
        # Log error
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ["ERROR_SNS_TOPIC"],
            Subject="PharmaceuticalInventory Crew Error",
            Message=str(e)
        )
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def parse_crew_output(result: str) -> dict:
    """
    Parse CrewAI output into structured recommendations
    """
    return {
        "transfers": extract_transfer_proposals(result),
        "alerts": extract_alerts(result),
        "forecasts": extract_forecasts(result),
        "raw_output": result
    }

def persist_recommendations(recommendations: dict):
    """
    Store recommendations in DynamoDB for audit trail
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pharma-recommendations')
    
    table.put_item(Item={
        "recommendation_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "crew_output": json.dumps(recommendations),
        "status": "PENDING_REVIEW"
    })

def send_notifications(recommendations: dict):
    """
    Send SNS notifications to stakeholders
    """
    sns = boto3.client('sns')
    
    message = f"""
    Pharmaceutical Inventory Crew Report
    ====================================
    
    Transfer Proposals: {len(recommendations['transfers'])}
    Alerts: {len(recommendations['alerts'])}
    
    Transfer Details:
    {json.dumps(recommendations['transfers'], indent=2)}
    
    Critical Alerts:
    {json.dumps(recommendations['alerts'], indent=2)}
    """
    
    sns.publish(
        TopicArn=os.environ["WAREHOUSE_SNS_TOPIC"],
        Subject="Pharmacy Inventory Crew Report",
        Message=message
    )
```

---

## 🛠️ TOOL DEFINITIONS

### Inventory Tools (with Type Safety)

```python
# tools/inventory_tools.py

from crewai_tools import tool
from typing import Optional, List
import redshift_connector
from pydantic import BaseModel, Field

class InventoryItem(BaseModel):
    """Type-safe inventory item structure"""
    medication_id: str = Field(..., description="Medication ID")
    facility_id: str = Field(..., description="Facility ID")
    quantity_on_hand: int = Field(..., description="Units in stock")
    expiry_date: str = Field(..., description="ISO format expiry date")
    days_to_expiry: int = Field(..., description="Days until expiration")
    batch_id: str = Field(..., description="Batch identifier")

@tool("Query Inventory")
def query_inventory(
    facility_id: Optional[str] = None,
    medication_id: Optional[str] = None,
    days_to_expiry_threshold: int = 14
) -> List[InventoryItem]:
    """
    Query inventory data from Redshift.
    
    Args:
        facility_id: Filter by specific facility (optional)
        medication_id: Filter by specific medication (optional)
        days_to_expiry_threshold: Show items expiring within N days
    
    Returns:
        List of InventoryItem objects matching criteria
    """
    conn = redshift_connector.connect(
        host=os.environ["REDSHIFT_HOST"],
        database="pharma_db",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )
    
    cursor = conn.cursor()
    query = """
        SELECT 
            medication_id,
            facility_id,
            quantity_on_hand,
            expiry_date,
            days_to_expiry,
            batch_id
        FROM inventory
        WHERE days_to_expiry < %s
    """
    
    params = [days_to_expiry_threshold]
    if facility_id:
        query += " AND facility_id = %s"
        params.append(facility_id)
    if medication_id:
        query += " AND medication_id = %s"
        params.append(medication_id)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    items = [
        InventoryItem(
            medication_id=r[0],
            facility_id=r[1],
            quantity_on_hand=r[2],
            expiry_date=r[3].isoformat(),
            days_to_expiry=r[4],
            batch_id=r[5]
        )
        for r in results
    ]
    
    return items

@tool("Check Facility Capacity")
def check_facility_capacity(facility_id: str) -> dict:
    """
    Check storage capacity and utilization at a facility.
    """
    query = """
        SELECT 
            total_storage_capacity,
            COALESCE(SUM(i.quantity_on_hand), 0) as total_stock,
            ROUND(100.0 * COALESCE(SUM(i.quantity_on_hand), 0) / 
                  f.total_storage_capacity, 2) as utilization_percent
        FROM facilities f
        LEFT JOIN inventory i ON f.facility_id = i.facility_id
        WHERE f.facility_id = %s
        GROUP BY f.total_storage_capacity
    """
    
    cursor.execute(query, [facility_id])
    result = cursor.fetchone()
    
    return {
        "facility_id": facility_id,
        "total_capacity": result[0],
        "current_stock": result[1],
        "utilization_percent": result[2],
        "available_capacity": result[0] - result[1]
    }

@tool("Create Alert")
def create_alert(
    facility_id: str,
    medication_id: str,
    alert_type: str,  # "CRITICAL" or "WARNING"
    quantity: int,
    message: str
) -> dict:
    """
    Create an alert for pharmacists/warehouse managers.
    """
    alert_id = str(uuid.uuid4())
    
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=os.environ["PHARMACIST_SNS_TOPIC"],
        Subject=f"[{alert_type}] Medication Alert - {medication_id}",
        Message=f"""
        Facility: {facility_id}
        Medication: {medication_id}
        Quantity at Risk: {quantity} units
        
        Alert Message:
        {message}
        """
    )
    
    return {
        "alert_id": alert_id,
        "status": "SENT",
        "recipients": "pharmacists, warehouse managers"
    }
```

### Transfer Tools

```python
# tools/transfer_tools.py

from crewai_tools import tool
from pydantic import BaseModel
from typing import List

class TransferMatch(BaseModel):
    facility_id: str
    facility_name: str
    shortage_quantity: int
    available_capacity: int
    distance_km: float

@tool("Find Transfer Matches")
def find_transfer_matches(
    medication_id: str,
    surplus_quantity: int,
    source_facility: str
) -> List[TransferMatch]:
    """
    Find facilities that need medication and can receive it.
    """
    query = """
        SELECT 
            f.facility_id,
            f.facility_name,
            (r.reorder_point - COALESCE(i.quantity_on_hand, 0)) as shortage_qty,
            f.storage_capacity_available,
            SQRT(
                POWER(f.latitude - sf.latitude, 2) + 
                POWER(f.longitude - sf.longitude, 2)
            ) * 111 as distance_km
        FROM facilities f
        LEFT JOIN inventory i ON f.facility_id = i.facility_id 
            AND i.medication_id = %s
        LEFT JOIN reorder_points r ON f.facility_id = r.facility_id 
            AND r.medication_id = %s
        JOIN facilities sf ON sf.facility_id = %s
        WHERE f.facility_id != %s
            AND (r.reorder_point - COALESCE(i.quantity_on_hand, 0)) > 0
            AND f.storage_capacity_available >= %s
        ORDER BY distance_km ASC
        LIMIT 10
    """
    
    cursor.execute(query, [
        medication_id, medication_id, source_facility,
        source_facility, surplus_quantity
    ])
    
    matches = [
        TransferMatch(
            facility_id=m[0],
            facility_name=m[1],
            shortage_quantity=m[2],
            available_capacity=m[3],
            distance_km=round(m[4], 2)
        )
        for m in cursor.fetchall()
    ]
    
    return matches

@tool("Create Transfer Proposal")
def create_transfer_proposal(
    source_facility: str,
    destination_facility: str,
    medication_id: str,
    quantity: int,
    reasoning: str
) -> dict:
    """
    Create a transfer proposal with full audit trail.
    """
    proposal_id = str(uuid.uuid4())
    
    proposal = {
        "id": proposal_id,
        "source_facility": source_facility,
        "destination_facility": destination_facility,
        "medication_id": medication_id,
        "quantity": quantity,
        "reasoning": reasoning,
        "status": "PENDING_APPROVAL",
        "created_by": "crewai-agent",
        "created_at": datetime.now().isoformat()
    }
    
    # Store in RDS
    insert_to_db(proposal)
    
    # Store in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pharma-proposals')
    table.put_item(Item=proposal)
    
    # Notify stakeholders
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=os.environ["WAREHOUSE_SNS_TOPIC"],
        Subject=f"New Transfer Proposal: {medication_id}",
        Message=json.dumps(proposal, indent=2)
    )
    
    return {
        "proposal_id": proposal_id,
        "status": "CREATED",
        "message": "Transfer proposal created and awaiting approval"
    }
```

---

## 📊 AWS DEPLOYMENT ARCHITECTURE

### Lambda + CrewAI Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS DEPLOYMENT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ CloudWatch Events (Triggers)                             │ │
│  │                                                          │ │
│  │ • Hourly: Full crew execution                          │ │
│  │ • Real-time (SNS): Reactive crew execution             │ │
│  │                                                          │ │
│  └────────────────┬─────────────────────────────────────────┘ │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────────┐ │
│  │ AWS Lambda (CrewAI Executor)                            │ │
│  │                                                          │ │
│  │ Runtime: Python 3.11                                    │ │
│  │ Memory: 3008 MB                                         │ │
│  │ Timeout: 900 seconds (15 min)                           │ │
│  │ EBS Volume: 10 GB (for models)                          │ │
│  │                                                          │ │
│  │ Installed Packages:                                     │ │
│  │ • crewai==0.35.0                                        │ │
│  │ • anthropic==0.28.0 (Claude client)                     │ │
│  │ • redshift-connector==2.0.920                           │ │
│  │ • boto3==1.34.0                                         │ │
│  │ • pydantic==2.5.0                                       │ │
│  │                                                          │ │
│  │ Environment Variables:                                  │ │
│  │ • ANTHROPIC_API_KEY (Secrets Manager)                  │ │
│  │ • REDSHIFT_HOST, DB_USER, DB_PASSWORD                  │ │
│  │ • AWS_REGION, SNS_TOPICS                               │ │
│  │                                                          │ │
│  │ Execution:                                              │ │
│  │ 1. Initialize CrewAI agents                             │ │
│  │ 2. Load three specialized agents                        │ │
│  │ 3. Execute pharma_inventory_crew.kickoff()              │ │
│  │ 4. Parse crew output                                    │ │
│  │ 5. Persist to DynamoDB                                  │ │
│  │ 6. Send SNS notifications                               │ │
│  │                                                          │ │
│  └────────────────┬─────────────────────────────────────────┘ │
│                   │                                            │
│  ┌────────────────▼─────────────────────────────────────────┐ │
│  │ Data Services                                           │ │
│  │                                                          │ │
│  │ ├─ Redshift (Query inventory)                          │ │
│  │ ├─ RDS PostgreSQL (Store proposals)                    │ │
│  │ ├─ DynamoDB (Audit trail & recommendations)            │ │
│  │ ├─ S3 (Models, logs, cache)                            │ │
│  │ ├─ SNS (Notifications)                                 │ │
│  │ └─ SES (Email alerts)                                  │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### VPC & Network Architecture

```
┌─────────────────────────────────────────────────────┐
│              VPC (Private Network)                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Lambda Function                                   │
│  • Executes in VPC (IAM role)                     │
│  • VPC Endpoints for:                             │
│    ├─ Redshift (port 5439)                        │
│    ├─ RDS (port 5432)                             │
│    ├─ DynamoDB                                    │
│    ├─ S3                                          │
│    ├─ SNS                                         │
│    ├─ SES                                         │
│    └─ Secrets Manager                             │
│  • Security Groups restrict to Lambda             │
│                                                     │
│  Databases (Private Subnet)                        │
│  • Redshift: VPC endpoint, no internet            │
│  • RDS PostgreSQL: VPC endpoint, no internet      │
│  • DynamoDB: VPC endpoint, no internet            │
│                                                     │
│  Secrets Manager                                  │
│  • API keys encrypted & rotated                   │
│  • Lambda retrieves at runtime                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 EXECUTION TIMELINE

### Crew Execution Cycle (Hourly)

```
00:00:00 - CloudWatch Event Triggers
├─ Invoke Lambda with CrewAI executor
└─ Pass context: datetime, facility count, thresholds

00:00:01 - Lambda Initialization
├─ Load Anthropic SDK (Claude 3.5 Sonnet)
├─ Initialize 3 agents (Expiration, Transfer, Forecasting)
├─ Load tools and connect to Redshift/RDS
└─ Setup memory for agent collaboration

00:00:05 - Task 1: Analyze Expiring Inventory
├─ Expiration Manager Agent queries Redshift
├─ Agent processes: "Find items expiring within 14 days"
│  ├─ Calls query_inventory() tool → 500 items found
│  ├─ Calls check_facility_capacity() → 12 facilities at 80%+ capacity
│  ├─ Categorizes: 25 CRITICAL (< 7 days), 200 WARNING (7-14 days)
│  ├─ Calculates: $125,000 potential waste
│  └─ Reasoning: "Facility A has 50 units expiring in 3 days"
├─ Agent completes analysis
└─ Task 1 Output: "500 items at risk, 25 critical, $125K impact"

00:00:45 - Task 2: Find Transfer Opportunities
├─ Transfer Coordinator reads Task 1 output (agent memory)
├─ Agent processes: "Match surplus with shortages"
│  ├─ Calls find_transfer_matches() 12 times (12 critical medications)
│  ├─ Agent reasoning: "Med-001: Facility A has 50 excess, Facility B needs 40"
│  ├─ Calls calculate_transfer_cost() → $412.50 per transfer
│  ├─ Calls check_regulatory_constraints() → All approved
│  └─ Calls create_transfer_proposal() 12 times → Creates proposals
├─ Agent creates 12 transfer proposals
└─ Task 2 Output: "12 proposals created, $5K cost, $42.5K savings"

00:01:30 - Task 3: Assess Forecasting Risks
├─ Forecasting Analyst reads Tasks 1 & 2 outputs (memory)
├─ Agent processes: "Are we covered for predicted demand?"
│  ├─ Calls run_demand_forecast() for 5 critical medications
│  ├─ Calls get_external_signals() → Flu season detected
│  ├─ Agent reasoning: "40% spike expected, transfers only cover 85%"
│  ├─ Calls detect_demand_anomaly() → 3 facilities with unusual patterns
│  └─ Recommends: "Rush order 500 units of respiratory medications"
├─ Agent completes risk assessment
└─ Task 3 Output: "92% confidence in coverage, recommend rush order"

00:02:15 - Crew Completion
├─ All three agents finish reasoning
├─ CrewAI collects all outputs
└─ Return to Lambda handler

00:02:30 - Results Processing & Persistence
├─ Lambda parses crew output
├─ Extract structured data:
│  ├─ 12 transfer proposals
│  ├─ 3 critical alerts
│  ├─ 5 demand forecasts
│  └─ Risk assessment
├─ Store in DynamoDB (audit trail)
└─ Send SNS notifications

00:02:45 - Notifications
├─ SNS publishes to warehouse managers
├─ Sends to pharmacists
├─ Emails to procurement team
└─ Dashboard updated

Total Execution Time: ~2:45 minutes
Status: COMPLETE
```

---

## 📊 CREWAI ADVANTAGES FOR PHARMA USE CASE

| Feature | Benefit |
|---------|---------|
| **Role-Based Agents** | Expiration Manager, Transfer Coordinator, Forecaster each have clear roles |
| **Task Sequencing** | Task 2 inputs depend on Task 1, Task 3 validates all decisions |
| **Agent Memory** | Agents remember context from previous tasks (no re-explaining) |
| **Type Safety (Pydantic)** | Strict validation of pharmaceutical data types |
| **Simple Syntax** | Less boilerplate than LangChain or raw Claude SDK |
| **Multi-LLM Support** | Can use Claude, GPT, Llama, or other models interchangeably |
| **Built-in Error Handling** | Retries, fallbacks, graceful degradation |
| **Human-in-the-Loop Ready** | Easy to add approval stages later |
| **Audit Trail** | Crew logs all reasoning and decisions |
| **Scaling** | Add more agents/tasks without major refactoring |

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Setup & Agents (Weeks 1-2)
- [ ] Install CrewAI framework
- [ ] Set up Claude API integration
- [ ] Create three specialized agents
- [ ] Define agent roles and backstories
- [ ] Setup memory and logging

### Phase 2: Tools Development (Weeks 3-4)
- [ ] Create inventory tools (type-safe with Pydantic)
- [ ] Create transfer tools
- [ ] Create forecasting tools
- [ ] Unit test each tool
- [ ] Mock database calls

### Phase 3: Task Definition & Testing (Weeks 5-6)
- [ ] Define three core tasks
- [ ] Test task sequencing
- [ ] Validate agent memory between tasks
- [ ] Test with sample data
- [ ] Optimize agent prompts

### Phase 4: AWS Integration (Weeks 7-8)
- [ ] Create Lambda function
- [ ] Package CrewAI dependencies
- [ ] Connect to Redshift/RDS
- [ ] Setup VPC & security groups
- [ ] Configure CloudWatch triggers

### Phase 5: Production & Monitoring (Weeks 9-10)
- [ ] Load testing with full data
- [ ] Performance optimization
- [ ] Cost analysis
- [ ] Implement comprehensive logging
- [ ] Production deployment

---

## 💾 DATA MODELS

### CrewAI Agent Memory

```python
# Memory is automatically managed by CrewAI
# Example of what's stored in agent memory:

Agent Memory (Expiration Manager):
{
    "conversation_history": [
        {
            "role": "user",
            "content": "Analyze expiring inventory..."
        },
        {
            "role": "assistant",
            "content": "I found 500 items expiring...",
            "tool_calls": [
                {
                    "tool": "query_inventory",
                    "result": {...}
                }
            ]
        }
    ],
    "working_memory": {
        "expiring_items": [...],
        "critical_count": 25,
        "estimated_waste": 125000
    }
}
```

### DynamoDB Audit Trail

```json
{
    "execution_id": "uuid",
    "timestamp": "2026-02-04T14:32:00Z",
    "crew_name": "pharma_inventory_crew",
    "agents_executed": ["expiration_manager", "transfer_coordinator", "forecasting_analyst"],
    "tasks_executed": [
        {
            "task_name": "analyze_expiring_inventory",
            "agent": "expiration_manager",
            "status": "COMPLETED",
            "duration_seconds": 45,
            "tools_called": ["query_inventory", "check_facility_capacity", "create_alert"],
            "output": "500 items at risk..."
        },
        {
            "task_name": "find_transfer_opportunities",
            "agent": "transfer_coordinator",
            "status": "COMPLETED",
            "duration_seconds": 45,
            "tools_called": ["find_transfer_matches", "calculate_transfer_cost", "create_transfer_proposal"],
            "output": "12 proposals created..."
        }
    ],
    "final_output": "Crew completed with 12 transfers, 3 alerts",
    "errors": [],
    "cost_estimate": 0.05
}
```

---

## 🔐 SECURITY & COMPLIANCE

### CrewAI-Specific Security
- Agent memory encrypted at rest (DynamoDB encryption)
- Tool execution logged with full audit trail
- Input validation via Pydantic models
- Output sanitization before storage

### AWS Security
- Lambda execution in VPC only
- Secrets Manager for API keys
- IAM roles with least privilege
- VPC endpoints for private access
- CloudTrail logging all API calls

---

## 📞 NEXT STEPS

1. **Review CrewAI approach:** Confirm multi-agent framework meets requirements
2. **Install & test locally:** Set up CrewAI with sample data
3. **Develop agents:** Create three specialized agents with roles
4. **Build tools:** Implement all tools with Pydantic validation
5. **Lambda integration:** Package and deploy to AWS
6. **Monitoring:** Setup CloudWatch and observability

