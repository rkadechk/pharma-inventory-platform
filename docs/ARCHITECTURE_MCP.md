# 🏗️ PHARMACEUTICAL INVENTORY PLATFORM - MCP (MODEL CONTEXT PROTOCOL) ARCHITECTURE

**Updated Architecture:** Model Context Protocol (MCP) + AWS Services  
**Date:** February 4, 2026  
**Status:** Architecture Design Phase

---

## 📐 SYSTEM ARCHITECTURE OVERVIEW

### High-Level Architecture (MCP Approach)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHARMACEUTICAL INVENTORY PLATFORM                          │
│              (Model Context Protocol + ETL + ML + Power BI + AWS)           │
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
│    MCP     │ │   ML     │   │   POWER    │    │   ANALYTICS  │
│  SERVERS   │ │  MODELS  │   │     BI     │    │   & INSIGHTS │
│  (Tools)   │ │ (Prophet) │  │ DASHBOARDS │    │              │
└─────┬──────┘ └────┬─────┘   └─────┬──────┘    └──────┬───────┘
      │             │               │                  │
      └─────────────┴───────────────┴──────────────────┘
                   │
        ┌──────────▼──────────────────────────────────────────────┐
        │         DECISION SUPPORT & ACTION LAYER                 │
        │  • Claude/Agent client calls MCP servers                │
        │  • Transfer proposals (multi-facility matching)         │
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
        │  • MCP server health & performance metrics              │
        └──────────────────────────────────────────────────────────┘
```

---

## 🛠️ MODEL CONTEXT PROTOCOL (MCP) LAYER

### What is MCP?

Model Context Protocol (MCP) is an open standard that enables **secure tool sharing** between clients (like Claude, other AI models, or custom applications) and servers (your tools/services).

**Key Benefits:**
- ✅ Standardized tool interface (JSON-RPC 2.0 based)
- ✅ Multiple clients can use the same MCP server
- ✅ Reusable across different AI models & applications
- ✅ Built-in resource discovery & capabilities
- ✅ Secure transport (stdio, HTTP, WebSocket)

### MCP Architecture in Pharma Platform

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │  Claude Agent   │  │  Custom Python   │  │  Dashboard UI    │        │
│  │  (via Lambda)   │  │  Application     │  │  Backend         │        │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘        │
│           │                    │                     │                   │
│           └────────────────────┼─────────────────────┘                   │
│                                │                                         │
│                    ┌───────────▼────────────┐                            │
│                    │   MCP Client Protocol  │                            │
│                    │  (JSON-RPC 2.0 calls) │                            │
│                    └───────────┬────────────┘                            │
│                                │                                         │
└────────────────────────────────┼─────────────────────────────────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  Network Transport Layer  │
                    │  • HTTP/REST              │
                    │  • WebSocket              │
                    │  • stdio (local)          │
                    └────────────┬──────────────┘
                                 │
┌────────────────────────────────┼─────────────────────────────────────────┐
│                     SERVER LAYER (MCP Servers)                           │
├────────────────────────────────┼─────────────────────────────────────────┤
│                                │                                         │
│  ┌──────────────────────────┐  │  ┌──────────────────────────┐           │
│  │  MCP Server 1            │  │  │  MCP Server 2            │           │
│  │  (Inventory Tools)       │  │  │  (Forecasting Tools)     │           │
│  │                          │  │  │                          │           │
│  │  ├─ query_inventory()    │  │  │  ├─ run_forecast()       │           │
│  │  ├─ list_medications()   │  │  │  ├─ get_demand_signals() │           │
│  │  ├─ check_expiry()       │  │  │  └─ predict_shortage()   │           │
│  │  └─ get_facility_stock() │  │  │                          │           │
│  │                          │  │  │                          │           │
│  └──────────┬───────────────┘  │  └──────────┬───────────────┘           │
│             │                  │             │                          │
│  ┌──────────▼──────────────┐   │             │                          │
│  │  MCP Server 3           │   │             │                          │
│  │  (Transfer Tools)       │   │             │                          │
│  │                         │   │             │                          │
│  │  ├─ find_matches()      │   │             │                          │
│  │  ├─ create_proposal()   │   │             │                          │
│  │  ├─ calculate_cost()    │   │             │                          │
│  │  └─ approve_transfer()  │   │             │                          │
│  │                         │   │             │                          │
│  └──────────┬──────────────┘   │             │                          │
│             │                  │             │                          │
│             │ (all behind      │             │                          │
│             │  same protocol)  │             │                          │
└─────────────┼──────────────────┼─────────────┼──────────────────────────┘
              │                  │             │
              └──────────────────┴─────────────┘
                        │
        ┌───────────────▼────────────────┐
        │  AWS Services (Redshift, RDS, │
        │   DynamoDB, S3, SNS, SES)      │
        └────────────────────────────────┘
```

---

## 🖥️ MCP SERVER DESIGN

### Server 1: Inventory Management MCP Server

```python
# mcp_servers/inventory_server.py

from mcp.server import Server, Resource, Tool
from mcp.types import TextContent, ToolResult
import json

server = Server("pharma-inventory-server")

# Define tools that clients can call
@server.tool()
def query_inventory(
    facility_id: str = None,
    medication_id: str = None,
    days_to_expiry_threshold: int = 14
) -> dict:
    """
    Query inventory data from Redshift.
    
    Clients (like Claude) can call this to get current inventory status.
    """
    import redshift_connector
    
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
    
    return {
        "status": "success",
        "count": len(results),
        "items": [
            {
                "medication_id": r[0],
                "facility_id": r[1],
                "quantity": r[2],
                "expiry_date": r[3].isoformat(),
                "days_to_expiry": r[4],
                "batch_id": r[5]
            }
            for r in results
        ]
    }

@server.tool()
def check_facility_capacity(facility_id: str) -> dict:
    """
    Check storage capacity and current utilization at a facility.
    """
    query = """
        SELECT 
            f.facility_id,
            f.total_storage_capacity,
            SUM(i.quantity_on_hand) as total_stock,
            ROUND(100.0 * SUM(i.quantity_on_hand) / f.total_storage_capacity, 2) as utilization_percent
        FROM facilities f
        LEFT JOIN inventory i ON f.facility_id = i.facility_id
        WHERE f.facility_id = %s
        GROUP BY f.facility_id, f.total_storage_capacity
    """
    
    cursor.execute(query, [facility_id])
    result = cursor.fetchone()
    
    return {
        "facility_id": result[0],
        "total_capacity": result[1],
        "current_stock": result[2],
        "utilization_percent": result[3]
    }

@server.tool()
def get_expiring_medications() -> dict:
    """
    List all medications expiring within 7 days (critical alert).
    """
    query = """
        SELECT 
            medication_id,
            facility_id,
            quantity_on_hand,
            expiry_date,
            days_to_expiry
        FROM inventory
        WHERE days_to_expiry <= 7
        ORDER BY days_to_expiry ASC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    return {
        "critical_count": len(results),
        "items": [
            {
                "medication_id": r[0],
                "facility_id": r[1],
                "quantity": r[2],
                "expiry_date": r[3].isoformat(),
                "days_to_expiry": r[4]
            }
            for r in results
        ]
    }

# Register resources that describe the server's capabilities
@server.resource()
def inventory_schema() -> Resource:
    """
    Return schema of inventory table for clients to understand structure.
    """
    return Resource(
        uri="pharma://inventory/schema",
        name="inventory_schema",
        mimeType="application/json",
        contents=json.dumps({
            "table": "inventory",
            "columns": [
                {"name": "inventory_id", "type": "UUID"},
                {"name": "facility_id", "type": "VARCHAR"},
                {"name": "medication_id", "type": "VARCHAR"},
                {"name": "quantity_on_hand", "type": "INTEGER"},
                {"name": "expiry_date", "type": "DATE"},
                {"name": "days_to_expiry", "type": "INTEGER"}
            ]
        })
    )
```

### Server 2: Forecasting MCP Server

```python
# mcp_servers/forecasting_server.py

from mcp.server import Server, Tool
import joblib
import pandas as pd

server = Server("pharma-forecasting-server")

@server.tool()
def run_demand_forecast(
    medication_id: str,
    facility_id: str,
    days_ahead: int = 30
) -> dict:
    """
    Run Prophet demand forecasting for a medication at a facility.
    """
    # Load pre-trained Prophet model from S3
    model = joblib.load(
        f"s3://pharma-models/prophet_{medication_id}.pkl"
    )
    
    # Generate forecast
    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)
    
    # Get last N rows (future predictions)
    future_forecast = forecast.tail(days_ahead)
    
    return {
        "medication_id": medication_id,
        "facility_id": facility_id,
        "forecast_horizon_days": days_ahead,
        "predictions": [
            {
                "date": row['ds'].isoformat(),
                "predicted_demand": round(row['yhat'], 2),
                "lower_bound": round(row['yhat_lower'], 2),
                "upper_bound": round(row['yhat_upper'], 2),
                "confidence_level": 0.95
            }
            for _, row in future_forecast.iterrows()
        ]
    }

@server.tool()
def get_external_signals(
    signal_type: str = "all"  # "weather", "disease", "events", "all"
) -> dict:
    """
    Fetch external signals that impact demand (weather, disease outbreaks, etc).
    """
    from boto3 import client
    
    s3 = client('s3')
    
    response = s3.get_object(
        Bucket='pharma-data',
        Key='external_signals/latest.json'
    )
    
    signals = json.loads(response['Body'].read())
    
    if signal_type != "all":
        signals = {k: v for k, v in signals.items() 
                  if signal_type in k}
    
    return {
        "timestamp": signals.get("timestamp"),
        "signals": signals
    }

@server.tool()
def detect_demand_anomaly(
    medication_id: str,
    facility_id: str,
    lookback_days: int = 30
) -> dict:
    """
    Detect unusual demand patterns that might indicate shortage risk.
    """
    query = """
        SELECT 
            DATE(consumption_date) as date,
            SUM(quantity_consumed) as daily_consumption
        FROM consumption
        WHERE medication_id = %s 
            AND facility_id = %s
            AND consumption_date >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(consumption_date)
        ORDER BY date DESC
    """
    
    cursor.execute(query, [medication_id, facility_id, lookback_days])
    data = pd.DataFrame(cursor.fetchall(), columns=['date', 'consumption'])
    
    # Simple anomaly detection: consumption > mean + 2*std
    mean = data['consumption'].mean()
    std = data['consumption'].std()
    threshold = mean + (2 * std)
    
    anomalies = data[data['consumption'] > threshold]
    
    return {
        "medication_id": medication_id,
        "facility_id": facility_id,
        "avg_consumption": round(mean, 2),
        "anomaly_threshold": round(threshold, 2),
        "anomalies_detected": len(anomalies),
        "anomaly_dates": [
            {"date": row['date'].isoformat(), "consumption": row['consumption']}
            for _, row in anomalies.iterrows()
        ]
    }
```

### Server 3: Transfer Coordination MCP Server

```python
# mcp_servers/transfer_server.py

from mcp.server import Server, Tool
import json

server = Server("pharma-transfer-server")

@server.tool()
def find_transfer_matches(
    medication_id: str,
    surplus_quantity: int,
    source_facility: str
) -> dict:
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
            ) as distance_km
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
    
    matches = cursor.fetchall()
    
    return {
        "medication_id": medication_id,
        "source_facility": source_facility,
        "available_quantity": surplus_quantity,
        "potential_matches": [
            {
                "facility_id": m[0],
                "facility_name": m[1],
                "shortage_quantity": m[2],
                "available_capacity": m[3],
                "distance_km": round(m[4], 2),
                "recommended_transfer_qty": min(surplus_quantity, m[2])
            }
            for m in matches
        ]
    }

@server.tool()
def create_transfer_proposal(
    source_facility: str,
    destination_facility: str,
    medication_id: str,
    quantity: int,
    reasoning: str
) -> dict:
    """
    Create a transfer proposal with audit trail.
    """
    import uuid
    
    proposal_id = str(uuid.uuid4())
    
    proposal = {
        "id": proposal_id,
        "source_facility": source_facility,
        "destination_facility": destination_facility,
        "medication_id": medication_id,
        "quantity": quantity,
        "status": "PENDING_APPROVAL",
        "reasoning": reasoning,
        "created_by": "mcp-agent",
        "created_at": datetime.now().isoformat(),
        "approval_chain": []
    }
    
    # Store in RDS
    insert_proposal_to_db(proposal)
    
    # Store in DynamoDB for audit trail
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('pharma-proposals')
    table.put_item(Item=proposal)
    
    # Send notification
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

@server.tool()
def calculate_transfer_cost(
    source_facility: str,
    destination_facility: str,
    quantity: int
) -> dict:
    """
    Calculate logistics cost for a transfer.
    """
    # Get facility coordinates
    query = """
        SELECT latitude, longitude FROM facilities 
        WHERE facility_id IN (%s, %s)
    """
    
    cursor.execute(query, [source_facility, destination_facility])
    coords = cursor.fetchall()
    
    # Calculate distance
    import math
    lat1, lon1 = coords[0]
    lat2, lon2 = coords[1]
    
    distance = math.sqrt(
        (lat2 - lat1)**2 + (lon2 - lon1)**2
    ) * 111  # km
    
    # Calculate costs
    transport_cost = distance * 2.5  # $2.5 per km
    handling_cost = quantity * 0.5   # $0.50 per unit
    insurance_cost = distance * 0.3  # $0.30 per km
    
    total_cost = transport_cost + handling_cost + insurance_cost
    
    return {
        "distance_km": round(distance, 2),
        "transport_cost": round(transport_cost, 2),
        "handling_cost": round(handling_cost, 2),
        "insurance_cost": round(insurance_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_unit": round(total_cost / quantity, 4)
    }

@server.tool()
def approve_transfer(
    proposal_id: str,
    approver_id: str,
    approval_notes: str = ""
) -> dict:
    """
    Approve a transfer proposal (with audit trail).
    """
    # Update proposal status
    update_query = """
        UPDATE transfer_proposals
        SET status = 'APPROVED',
            approval_chain = approval_chain || %s,
            approved_at = NOW()
        WHERE id = %s
    """
    
    approval_entry = {
        "approver_id": approver_id,
        "timestamp": datetime.now().isoformat(),
        "notes": approval_notes
    }
    
    cursor.execute(update_query, [json.dumps(approval_entry), proposal_id])
    
    # Log to audit trail
    log_to_audit(proposal_id, "APPROVED", approver_id)
    
    # Trigger transfer execution
    trigger_transfer_execution(proposal_id)
    
    return {
        "proposal_id": proposal_id,
        "status": "APPROVED",
        "message": "Transfer approved and queued for execution"
    }
```

---

## 🔌 HOW CLIENTS USE MCP SERVERS

### Client Example: Claude Agent Using MCP

```python
# client/claude_agent.py

from anthropic import Anthropic
import json
import subprocess

# Start MCP servers as separate processes
mcp_processes = {
    "inventory": subprocess.Popen(["python", "mcp_servers/inventory_server.py"]),
    "forecasting": subprocess.Popen(["python", "mcp_servers/forecasting_server.py"]),
    "transfer": subprocess.Popen(["python", "mcp_servers/transfer_server.py"])
}

# Initialize Claude client
client = Anthropic()

# Define how Claude can access MCP servers
mcp_tools = [
    {
        "type": "tool",
        "name": "call_mcp_server",
        "description": "Call a tool from an MCP server",
        "input_schema": {
            "type": "object",
            "properties": {
                "server": {
                    "type": "string",
                    "enum": ["inventory", "forecasting", "transfer"],
                    "description": "Which MCP server to call"
                },
                "tool": {
                    "type": "string",
                    "description": "Tool name in the MCP server"
                },
                "arguments": {
                    "type": "object",
                    "description": "Tool arguments"
                }
            },
            "required": ["server", "tool", "arguments"]
        }
    }
]

def call_mcp_tool(server: str, tool: str, arguments: dict) -> dict:
    """
    Execute an MCP server tool via JSON-RPC protocol.
    """
    import socket
    import json
    
    # Connect to MCP server's stdio or HTTP endpoint
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": arguments
        }
    }
    
    # Send request and receive response
    # (implementation depends on transport: stdio, HTTP, WebSocket)
    
    response = send_mcp_request(server, request)
    return response["result"]

def run_expiration_agent():
    """
    Run the expiration management agent.
    """
    messages = [
        {
            "role": "user",
            "content": """
            You are an expert pharmaceutical inventory management agent.
            
            Task: Identify medications at risk of expiration and recommend actions.
            
            Steps:
            1. Query all medications expiring within 14 days using the inventory server
            2. For each critical medication, find facilities that need it
            3. Create transfer proposals to move stock before expiry
            4. For items that can't be transferred, flag for safe disposal
            
            Use the MCP tools to gather data and make recommendations.
            Explain your reasoning for each decision.
            """
        }
    ]
    
    while True:
        # Get Claude's response
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=mcp_tools,
            messages=messages
        )
        
        # Check if Claude wants to call an MCP tool
        if response.stop_reason == "tool_use":
            for content in response.content:
                if content.type == "tool_use" and content.name == "call_mcp_server":
                    # Execute MCP tool call
                    server = content.input["server"]
                    tool = content.input["tool"]
                    arguments = content.input["arguments"]
                    
                    result = call_mcp_tool(server, tool, arguments)
                    
                    # Add result back to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": json.dumps(result)
                        }]
                    })
        else:
            # Claude has finished, extract recommendations
            return extract_recommendations(response)

# Run the agent
if __name__ == "__main__":
    recommendations = run_expiration_agent()
    print(json.dumps(recommendations, indent=2))
```

---

## 📋 DEPLOYMENT ARCHITECTURE

### MCP Servers on AWS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AWS DEPLOYMENT                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │ ECS Fargate Cluster (MCP Server Containers)                      │ │
│  │                                                                  │ │
│  │  Container 1: Inventory Server                                  │ │
│  │  • Port 3001                                                    │ │
│  │  • Health check: /health                                        │ │
│  │  • Replicas: 2 (auto-scaling 1-5)                              │ │
│  │                                                                  │ │
│  │  Container 2: Forecasting Server                               │ │
│  │  • Port 3002                                                    │ │
│  │  • Health check: /health                                        │ │
│  │  • Replicas: 2 (auto-scaling 1-5)                              │ │
│  │                                                                  │ │
│  │  Container 3: Transfer Server                                  │ │
│  │  • Port 3003                                                    │ │
│  │  • Health check: /health                                        │ │
│  │  • Replicas: 2 (auto-scaling 1-5)                              │ │
│  │                                                                  │ │
│  │  Container 4: API Gateway (MCP HTTP Router)                    │ │
│  │  • Port 443 (HTTPS)                                            │ │
│  │  • Routes requests to backend servers                          │ │
│  │  • Authentication: API keys, IAM                               │ │
│  │                                                                  │ │
│  └────────────────┬─────────────────────────────────────────────────┘ │
│                   │                                                    │
│  ┌────────────────▼──────────────────────────────────────────────┐   │
│  │ Lambda Functions (Agent Orchestrators)                        │   │
│  │                                                               │   │
│  │ • Expiration Manager Lambda                                  │   │
│  │   └─ Calls MCP servers via HTTP                              │   │
│  │ • Transfer Coordinator Lambda                                │   │
│  │   └─ Calls MCP servers via HTTP                              │   │
│  │ • Forecasting Alert Lambda                                   │   │
│  │   └─ Calls MCP servers via HTTP                              │   │
│  │                                                               │   │
│  └────────────────┬──────────────────────────────────────────────┘   │
│                   │                                                    │
│  ┌────────────────▼──────────────────────────────────────────────┐   │
│  │ CloudWatch Events (Triggers)                                  │   │
│  │                                                               │   │
│  │ • Hourly: Run expiration check agent                         │   │
│  │ • Every 6 hours: Run forecasting agent                       │   │
│  │ • Real-time (SNS): Run transfer coordinator                  │   │
│  │                                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPC (Private Network)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ Public Subnet (API Gateway / Load Balancer)             │  │
│ │                                                          │  │
│ │  ┌─────────────────────────────────────────────────┐   │  │
│ │  │ Application Load Balancer (HTTPS)               │   │  │
│ │  │ • Listens on 443                                │   │  │
│ │  │ • Routes to ECS containers                      │   │  │
│ │  └────────────┬────────────────────────────────────┘   │  │
│ │              │                                          │  │
│ └──────────────┼──────────────────────────────────────────┘  │
│                │                                              │
│ ┌──────────────▼──────────────────────────────────────────┐  │
│ │ Private Subnet (ECS Containers & Databases)            │  │
│ │                                                          │  │
│ │ ┌────────────────────────────────────────────────────┐ │  │
│ │ │ ECS Cluster (MCP Servers + Lambda Orchestrators)  │ │  │
│ │ │ • Security Group: Allow ALB → Containers         │ │  │
│ │ │ • Security Group: Allow Containers → DB          │ │  │
│ │ └────────────────────────────────────────────────────┘ │  │
│ │                                                          │  │
│ │ ┌────────────────────────────────────────────────────┐ │  │
│ │ │ Redshift (Data Warehouse)                         │ │  │
│ │ │ • VPC Endpoint (private access)                   │ │  │
│ │ │ • Security Group: Allow ECS containers           │ │  │
│ │ └────────────────────────────────────────────────────┘ │  │
│ │                                                          │  │
│ │ ┌────────────────────────────────────────────────────┐ │  │
│ │ │ RDS PostgreSQL (Proposals, Audit)                 │ │  │
│ │ │ • VPC Endpoint (private access)                   │ │  │
│ │ │ • Security Group: Allow ECS containers           │ │  │
│ │ └────────────────────────────────────────────────────┘ │  │
│ │                                                          │  │
│ │ ┌────────────────────────────────────────────────────┐ │  │
│ │ │ DynamoDB (Audit Trails & Logging)                 │ │  │
│ │ │ • VPC Endpoint (private access)                   │ │  │
│ │ └────────────────────────────────────────────────────┘ │  │
│ │                                                          │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│ ┌──────────────────────────────────────────────────────────┐  │
│ │ S3 Gateway Endpoint (Private S3 Access)                 │  │
│ │ • Models bucket                                         │  │
│ │ • Data bucket                                           │  │
│ │ • Logs bucket                                           │  │
│ └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 AGENT EXECUTION FLOW (WITH MCP)

### Example: Expiration Management Workflow

```
TIME: 00:00 (Hourly Trigger)
═══════════════════════════════════════════════════════════════════

1. TRIGGER
   └─ CloudWatch Events → Lambda: ExpirationManagerAgent

2. AGENT INITIALIZATION
   ├─ Load Claude client
   ├─ Register MCP servers (inventory, forecasting, transfer)
   ├─ Load agent instructions
   └─ Begin logging

3. CLAUDE AGENT REASONING (Loop 1)
   ├─ Claude receives: "Analyze expiring inventory"
   ├─ Claude thinks: "I need to query expiring medications"
   ├─ Claude calls: MCP inventory server
   │  └─ call_mcp_server(
   │       server="inventory",
   │       tool="get_expiring_medications"
   │     )
   │
   └─ MCP Server responds: 500 items expiring within 7 days

4. CLAUDE AGENT REASONING (Loop 2)
   ├─ Claude receives: List of expiring items
   ├─ Claude thinks: "For critical items, find transfer candidates"
   ├─ Claude loops over medications:
   │  └─ call_mcp_server(
   │       server="transfer",
   │       tool="find_transfer_matches",
   │       arguments={
   │         "medication_id": "MED-001",
   │         "surplus_quantity": 150,
   │         "source_facility": "HOSPITAL-A"
   │       }
   │     )
   │
   └─ MCP Server responds: 3 matching facilities

5. CLAUDE AGENT REASONING (Loop 3)
   ├─ Claude receives: Matching facilities list
   ├─ Claude thinks: "Calculate costs for each transfer option"
   ├─ Claude calls: MCP transfer server
   │  └─ call_mcp_server(
   │       server="transfer",
   │       tool="calculate_transfer_cost",
   │       arguments={
   │         "source_facility": "HOSPITAL-A",
   │         "destination_facility": "HOSPITAL-B",
   │         "quantity": 150
   │       }
   │     )
   │
   └─ MCP Server responds: Cost = $412.50

6. CLAUDE DECISION PHASE
   ├─ Claude evaluates all options
   ├─ Claude creates transfer proposal:
   │  └─ call_mcp_server(
   │       server="transfer",
   │       tool="create_transfer_proposal",
   │       arguments={
   │         "source_facility": "HOSPITAL-A",
   │         "destination_facility": "HOSPITAL-B",
   │         "medication_id": "MED-001",
   │         "quantity": 150,
   │         "reasoning": "Transfers before 3-day expiry..."
   │       }
   │     )
   │
   └─ MCP Server creates proposal and sends SNS notification

7. COMPLETION
   ├─ All proposals created and logged
   ├─ Audit trail recorded in DynamoDB
   ├─ Notifications sent to warehouse managers
   └─ Return success status

RESULT:
├─ Transfer proposals created: 12
├─ Items flagged for review: 15
├─ Cost analysis completed: $5,250
├─ Audit trail: Full reasoning preserved
└─ Status: COMPLETE
```

---

## 🎯 MCP VS CLAUDE AGENTIC SDK

| Aspect | Claude Agentic SDK | MCP |
|--------|-------------------|-----|
| **Architecture** | Direct tool use | Server-based tool exposure |
| **Clients** | Claude only | Any client (Claude, custom apps, etc) |
| **Scalability** | Per-client tool setup | Shared MCP servers |
| **Reusability** | Tools built into agent | Tools are independent services |
| **Complexity** | Simpler | More structured |
| **Multi-tenancy** | Not built-in | Native support |
| **Tool Versioning** | Managed per agent | Centralized versioning |
| **Use Case** | Single smart agent | Multiple clients needing same tools |

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: MCP Server Foundation (Weeks 1-2)
- [ ] Set up MCP SDK in Python
- [ ] Create Inventory MCP Server
- [ ] Create Transfer MCP Server
- [ ] Create Forecasting MCP Server
- [ ] Define tool schemas and documentation
- [ ] Unit test individual tools

### Phase 2: MCP Deployment (Weeks 3-4)
- [ ] Containerize MCP servers (Docker)
- [ ] Deploy to ECS Fargate
- [ ] Set up Application Load Balancer
- [ ] Configure VPC endpoints & security groups
- [ ] Set up health checks & monitoring
- [ ] Test end-to-end tool calls

### Phase 3: Agent Integration (Weeks 5-6)
- [ ] Build Claude client for MCP servers
- [ ] Implement expiration management agent
- [ ] Implement transfer coordinator agent
- [ ] Implement forecasting agent
- [ ] Create agent orchestration logic
- [ ] Test agent-MCP interactions

### Phase 4: Operational Setup (Weeks 7-8)
- [ ] Set up CloudWatch triggers
- [ ] Configure Lambda orchestrators
- [ ] Implement error handling & retries
- [ ] Set up comprehensive logging
- [ ] Create audit trail system
- [ ] Load testing with production data

### Phase 5: Production & Monitoring (Weeks 9-10)
- [ ] Performance optimization
- [ ] Cost analysis & tuning
- [ ] Security audit & hardening
- [ ] Production deployment
- [ ] Stakeholder training
- [ ] Post-launch monitoring

---

## 📊 DATA MODELS

### MCP Server Definition (OpenAPI/JSON Schema)

```json
{
  "mcp_version": "1.0",
  "name": "pharma-inventory-server",
  "version": "1.0.0",
  "description": "MCP server for pharmaceutical inventory operations",
  "tools": [
    {
      "name": "query_inventory",
      "description": "Query inventory data with filters",
      "inputSchema": {
        "type": "object",
        "properties": {
          "facility_id": {
            "type": "string",
            "description": "Filter by facility ID (optional)"
          },
          "medication_id": {
            "type": "string",
            "description": "Filter by medication ID (optional)"
          },
          "days_to_expiry_threshold": {
            "type": "integer",
            "description": "Show items expiring within N days",
            "default": 14
          }
        },
        "required": []
      },
      "resultSchema": {
        "type": "object",
        "properties": {
          "status": {"type": "string"},
          "count": {"type": "integer"},
          "items": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "medication_id": {"type": "string"},
                "facility_id": {"type": "string"},
                "quantity": {"type": "integer"},
                "expiry_date": {"type": "string", "format": "date"},
                "days_to_expiry": {"type": "integer"}
              }
            }
          }
        }
      }
    }
  ]
}
```

### Audit Trail (DynamoDB)

```json
{
  "audit_id": "uuid",
  "timestamp": "2026-02-04T14:32:00Z",
  "event_type": "AGENT_EXECUTION",
  "agent_type": "expiration_management",
  "mcp_calls": [
    {
      "sequence": 1,
      "mcp_server": "inventory",
      "tool": "get_expiring_medications",
      "status": "SUCCESS",
      "duration_ms": 245,
      "result_summary": "500 items found"
    },
    {
      "sequence": 2,
      "mcp_server": "transfer",
      "tool": "find_transfer_matches",
      "status": "SUCCESS",
      "duration_ms": 512,
      "result_summary": "12 transfer opportunities identified"
    }
  ],
  "agent_decisions": [
    {
      "decision_id": "uuid",
      "type": "create_proposal",
      "reasoning": "Transfer before 3-day expiry window",
      "created_at": "2026-02-04T14:32:15Z",
      "status": "PENDING_APPROVAL"
    }
  ]
}
```

---

## 🔐 SECURITY CONSIDERATIONS

### MCP Server Authentication
- API keys for server-to-server communication
- IAM roles for Lambda → MCP server calls
- TLS/HTTPS for all external communication
- Rate limiting per API key/client

### Data Access Control
- MCP tools check caller permissions
- Row-level security on database queries
- Redshift/RDS access via VPC endpoints only
- Secrets Manager for database credentials

### Audit & Compliance
- All MCP calls logged with timestamp
- Tool input/output stored in DynamoDB (with redaction for sensitive data)
- CloudTrail logging for AWS service calls
- Reasoning chains preserved for regulatory review

---

## 📞 NEXT STEPS

1. **Evaluate MCP vs Claude SDK:** Confirm MCP approach meets requirements
2. **Design MCP Servers:** Finalize tool schemas and API contracts
3. **Prototype:** Build first MCP server (inventory) with Docker
4. **Integration Test:** Test Claude agent calling MCP servers
5. **Scale:** Add remaining servers and deploy to production
6. **Monitor:** Implement comprehensive observability

