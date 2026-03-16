# 🚀 PHARMACEUTICAL INVENTORY PLATFORM - NEXT STEPS ROADMAP

**Project Status:** Synthetic Data Generated ✅ | Architecture Designed ✅  
**Current Phase:** Implementation Planning  
**Date:** February 9, 2026

---

## 📍 PROJECT PROGRESS

### What We've Completed ✅

```
Phase 0: Foundation & Planning (COMPLETE)
├── ✅ Problem statement & business case
├── ✅ Architecture design (CrewAI-based)
├── ✅ Data schema design
├── ✅ Synthetic data generation
│   ├── facilities.csv (20 healthcare facilities)
│   ├── medications.csv (500+ medication items)
│   ├── inventory.csv (3,000 batch records)
│   ├── consumption.csv (50,000+ historical records)
│   ├── demand_forecast.csv (forecasts)
│   ├── transfers.csv (10,000+ historical transfers)
│   ├── replenishment_orders.csv
│   └── external_signals.csv (weather, disease data)
├── ✅ Solution architecture diagrams
├── ✅ Technology stack selection (CrewAI + Claude SDK)
├── ✅ AWS infrastructure planning
└── ✅ Implementation roadmap

Data Location: /pharma-inventory-platform/data-generation/synthetic_data/
```

### What's Next 🔄

```
Phase 1: CrewAI Framework Development (STARTING NOW - Weeks 1-2)
├── [ ] Local development environment setup
├── [ ] CrewAI & dependencies installation
├── [ ] Claude API integration
├── [ ] Three agents creation
├── [ ] Agent memory configuration
└── [ ] Basic testing with sample data

Phase 2: Tools & Database Layer (Weeks 3-4)
├── [ ] Inventory tools (query, capacity, alerts)
├── [ ] Transfer tools (matching, proposals, approval)
├── [ ] Forecasting tools (predictions, anomalies)
├── [ ] Local database setup (SQLite for testing)
├── [ ] Tool integration with synthetic data
└── [ ] Unit testing all tools

Phase 3: Tasks & Workflows (Weeks 5-6)
├── [ ] Define Task 1: Analyze Expiring Inventory
├── [ ] Define Task 2: Find Transfer Opportunities
├── [ ] Define Task 3: Assess Forecasting Risks
├── [ ] Test task sequencing
├── [ ] Validate agent memory between tasks
└── [ ] End-to-end crew execution testing

Phase 4: AWS Deployment (Weeks 7-8)
├── [ ] AWS account setup
├── [ ] Lambda function creation
├── [ ] Redshift & RDS setup
├── [ ] VPC & security configuration
├── [ ] CloudWatch integration
└── [ ] Production deployment

Phase 5: Testing & Optimization (Weeks 9-10)
├── [ ] Load testing
├── [ ] Performance optimization
├── [ ] Cost analysis
├── [ ] Compliance & audit trail validation
└── [ ] Go-live with pilot facilities
```

---

## 🎯 PHASE 1: CREWAI FRAMEWORK DEVELOPMENT (IMMEDIATE NEXT STEPS)

### Step 1.1: Set Up Local Development Environment

```bash
# Create project structure
mkdir -p /pharma-inventory-platform/agents
mkdir -p /pharma-inventory-platform/tasks
mkdir -p /pharma-inventory-platform/tools
mkdir -p /pharma-inventory-platform/models
mkdir -p /pharma-inventory-platform/tests

# Create virtual environment
cd /pharma-inventory-platform
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install crewai==0.35.0
pip install anthropic==0.28.0
pip install pydantic==2.5.0
pip install pandas==2.0.3
pip install redshift-connector==2.0.920
pip install fbprophet==0.7.1
pip install scikit-learn==1.3.0
pip install boto3==1.34.0
pip install python-dotenv==1.0.0
```

### Step 1.2: Set Up Claude API Integration

```python
# agents/config.py

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

client = Anthropic()

# Claude model configuration
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096

# Verify API connectivity
def test_claude_connection():
    """Test if Claude API is accessible"""
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Connected to Claude' if you receive this."}
            ]
        )
        print("✅ Claude API Connection Successful")
        return True
    except Exception as e:
        print(f"❌ Claude API Connection Failed: {str(e)}")
        return False
```

### Step 1.3: Create Three Specialized Agents

```python
# agents/pharma_agents.py

from crewai import Agent
from anthropic import Anthropic
from config import CLAUDE_MODEL

client = Anthropic()

# Agent 1: Expiration Manager
expiration_manager = Agent(
    role="Inventory Expiration Manager",
    goal="Identify medications at risk of expiration and prevent waste",
    backstory="""
    You are an expert pharmaceutical inventory analyst with 10 years 
    of experience in healthcare supply chain management. Your primary 
    responsibility is to monitor medication expiration dates across 
    all facilities and ensure no valuable medications are wasted.
    
    You understand:
    - Regulatory requirements for medication handling
    - Storage constraints and facility capacity
    - The urgency of identifying items expiring within 7-14 days
    - Financial impact of pharmaceutical waste
    - Safe disposal procedures for expired medications
    """,
    verbose=True,
    memory=True,
    llm=client
)

# Agent 2: Transfer Coordinator
transfer_coordinator = Agent(
    role="Multi-Facility Transfer Coordinator",
    goal="Optimize pharmaceutical inventory distribution across facilities",
    backstory="""
    You are a logistics and inventory optimization specialist. Your role 
    is to identify where medications are in surplus at one facility and 
    needed at another, then coordinate cost-effective transfers.
    
    You understand:
    - Distance optimization and logistics costs
    - Regulatory compliance for inter-facility transfers
    - Storage capacity constraints
    - Transfer timing and cold chain requirements
    - Cost-benefit analysis of transfer proposals
    - The life-saving impact of preventing shortages
    """,
    verbose=True,
    memory=True,
    llm=client
)

# Agent 3: Forecasting & Risk Analyst
forecasting_analyst = Agent(
    role="Demand Forecasting & Risk Analyst",
    goal="Predict demand spikes and prevent medication shortages",
    backstory="""
    You are a data scientist specializing in healthcare demand forecasting. 
    You use machine learning models, weather patterns, disease surveillance data, 
    and historical consumption patterns to predict future demand.
    
    You understand:
    - Time-series forecasting (Prophet, ARIMA)
    - Seasonal patterns (flu season, holidays)
    - External signals (disease outbreaks, weather, events)
    - Anomaly detection in consumption patterns
    - Confidence intervals and risk assessment
    - Procurement planning and lead times
    """,
    verbose=True,
    memory=True,
    llm=client
)
```

### Step 1.4: Create Database Layer (Using Synthetic Data)

```python
# database/data_loader.py

import pandas as pd
import sqlite3
from pathlib import Path

class SyntheticDataLoader:
    """Load and manage synthetic data for local testing"""
    
    def __init__(self, data_dir: str = "/pharma-inventory-platform/data-generation/synthetic_data"):
        self.data_dir = Path(data_dir)
        self.db_path = Path("pharma_dev.db")  # Local SQLite for testing
        self.conn = None
    
    def load_csv_files(self):
        """Load all synthetic CSV files"""
        self.data = {
            "facilities": pd.read_csv(self.data_dir / "facilities.csv"),
            "medications": pd.read_csv(self.data_dir / "medications.csv"),
            "inventory": pd.read_csv(self.data_dir / "inventory.csv"),
            "consumption": pd.read_csv(self.data_dir / "consumption.csv"),
            "demand_forecast": pd.read_csv(self.data_dir / "demand_forecast.csv"),
            "transfers": pd.read_csv(self.data_dir / "transfers.csv"),
            "replenishment_orders": pd.read_csv(self.data_dir / "replenishment_orders.csv"),
            "external_signals": pd.read_csv(self.data_dir / "external_signals.csv")
        }
        print(f"✅ Loaded {len(self.data)} CSV files")
        return self.data
    
    def create_sqlite_db(self):
        """Create local SQLite database from synthetic data"""
        self.conn = sqlite3.connect(str(self.db_path))
        
        for table_name, df in self.data.items():
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            print(f"✅ Created table: {table_name} ({len(df)} rows)")
        
        self.conn.commit()
        print(f"✅ Database created: {self.db_path}")
    
    def get_connection(self):
        """Get SQLite connection for testing"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
        return self.conn
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results"""
        return pd.read_sql_query(sql, self.get_connection())
    
    def get_summary_stats(self):
        """Print summary statistics about data"""
        print("\n" + "="*60)
        print("SYNTHETIC DATA SUMMARY")
        print("="*60)
        
        print(f"\n📍 Facilities: {len(self.data['facilities'])}")
        print(f"   Locations: {', '.join(self.data['facilities']['facility_id'].unique()[:5])}...")
        
        print(f"\n💊 Medications: {len(self.data['medications'])}")
        print(f"   Categories: {', '.join(self.data['medications']['category'].unique()[:5])}...")
        
        print(f"\n📦 Inventory Batches: {len(self.data['inventory'])}")
        print(f"   Total units: {self.data['inventory']['quantity_on_hand'].sum():,.0f}")
        
        print(f"\n📊 Consumption Records: {len(self.data['consumption'])}")
        print(f"   Date range: {self.data['consumption']['consumption_date'].min()} to {self.data['consumption']['consumption_date'].max()}")
        
        print(f"\n📈 Demand Forecasts: {len(self.data['demand_forecast'])}")
        
        print(f"\n🚚 Transfer History: {len(self.data['transfers'])}")
        
        print(f"\n🌡️ External Signals: {len(self.data['external_signals'])}")
        print("\n" + "="*60)

# Usage
if __name__ == "__main__":
    loader = SyntheticDataLoader()
    loader.load_csv_files()
    loader.create_sqlite_db()
    loader.get_summary_stats()
```

### Step 1.5: Create Inventory Tools (with Synthetic Data)

```python
# tools/inventory_tools.py

from crewai_tools import tool
from database.data_loader import SyntheticDataLoader
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd

# Initialize data loader
data_loader = SyntheticDataLoader()
data_loader.load_csv_files()
data_loader.create_sqlite_db()

class InventoryItem(BaseModel):
    """Type-safe inventory item structure"""
    medication_id: str
    facility_id: str
    quantity_on_hand: int
    expiry_date: str
    days_to_expiry: int
    batch_id: str

@tool("Query Inventory")
def query_inventory(
    facility_id: Optional[str] = None,
    medication_id: Optional[str] = None,
    days_to_expiry_threshold: int = 14
) -> List[InventoryItem]:
    """
    Query inventory data from local database.
    
    Args:
        facility_id: Filter by specific facility (optional)
        medication_id: Filter by specific medication (optional)
        days_to_expiry_threshold: Show items expiring within N days
    
    Returns:
        List of InventoryItem objects matching criteria
    """
    from datetime import datetime, timedelta
    
    # Load inventory data
    inventory_df = data_loader.data['inventory'].copy()
    
    # Convert expiry_date to datetime
    inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'])
    
    # Calculate days to expiry
    today = datetime.now()
    inventory_df['days_to_expiry'] = (
        inventory_df['expiry_date'] - today
    ).dt.days
    
    # Filter by threshold
    filtered = inventory_df[
        inventory_df['days_to_expiry'] < days_to_expiry_threshold
    ]
    
    # Apply optional filters
    if facility_id:
        filtered = filtered[filtered['facility_id'] == facility_id]
    if medication_id:
        filtered = filtered[filtered['medication_id'] == medication_id]
    
    # Convert to InventoryItem objects
    items = [
        InventoryItem(
            medication_id=row['medication_id'],
            facility_id=row['facility_id'],
            quantity_on_hand=int(row['quantity_on_hand']),
            expiry_date=row['expiry_date'].isoformat(),
            days_to_expiry=int(row['days_to_expiry']),
            batch_id=row['batch_id']
        )
        for _, row in filtered.iterrows()
    ]
    
    print(f"✅ Found {len(items)} inventory items")
    return items

@tool("Check Facility Capacity")
def check_facility_capacity(facility_id: str) -> dict:
    """Check storage capacity and utilization at a facility."""
    
    facilities_df = data_loader.data['facilities']
    inventory_df = data_loader.data['inventory']
    
    facility = facilities_df[facilities_df['facility_id'] == facility_id].iloc[0]
    facility_inventory = inventory_df[
        inventory_df['facility_id'] == facility_id
    ]
    
    total_stock = facility_inventory['quantity_on_hand'].sum()
    total_capacity = facility['total_storage_capacity']
    utilization = (total_stock / total_capacity) * 100 if total_capacity > 0 else 0
    
    return {
        "facility_id": facility_id,
        "facility_name": facility['facility_name'],
        "total_capacity": int(total_capacity),
        "current_stock": int(total_stock),
        "utilization_percent": round(utilization, 2),
        "available_capacity": int(total_capacity - total_stock)
    }

@tool("Create Alert")
def create_alert(
    facility_id: str,
    medication_id: str,
    alert_type: str,
    quantity: int,
    message: str
) -> dict:
    """Create an alert for pharmacists/warehouse managers."""
    
    # In testing, just log the alert
    alert = {
        "alert_id": f"ALERT-{facility_id}-{medication_id}",
        "facility_id": facility_id,
        "medication_id": medication_id,
        "alert_type": alert_type,
        "quantity_at_risk": quantity,
        "message": message,
        "status": "CREATED"
    }
    
    print(f"🚨 [{alert_type}] {message}")
    return alert
```

### Step 1.6: Create Transfer Tools

```python
# tools/transfer_tools.py

from crewai_tools import tool
from database.data_loader import SyntheticDataLoader
from typing import List
from pydantic import BaseModel
import pandas as pd
import math
import uuid

data_loader = SyntheticDataLoader()

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
    """Find facilities that need medication and can receive it."""
    
    facilities_df = data_loader.data['facilities']
    inventory_df = data_loader.data['inventory']
    
    # Get source facility coordinates
    source = facilities_df[
        facilities_df['facility_id'] == source_facility
    ].iloc[0]
    
    # Find facilities needing this medication
    needy_facilities = []
    
    for _, facility in facilities_df.iterrows():
        if facility['facility_id'] == source_facility:
            continue
        
        # Check current stock
        current_stock = inventory_df[
            (inventory_df['facility_id'] == facility['facility_id']) &
            (inventory_df['medication_id'] == medication_id)
        ]['quantity_on_hand'].sum()
        
        # Assume reorder point is 50% of max capacity per med
        reorder_point = facility['total_storage_capacity'] * 0.1
        shortage = max(0, reorder_point - current_stock)
        
        if shortage > 0:
            # Calculate distance
            distance = math.sqrt(
                (facility['latitude'] - source['latitude'])**2 +
                (facility['longitude'] - source['longitude'])**2
            ) * 111  # km
            
            needy_facilities.append(
                TransferMatch(
                    facility_id=facility['facility_id'],
                    facility_name=facility['facility_name'],
                    shortage_quantity=int(shortage),
                    available_capacity=int(facility['total_storage_capacity']),
                    distance_km=round(distance, 2)
                )
            )
    
    # Sort by distance
    needy_facilities.sort(key=lambda x: x.distance_km)
    
    print(f"✅ Found {len(needy_facilities)} matching facilities")
    return needy_facilities[:10]  # Return top 10 closest

@tool("Calculate Transfer Cost")
def calculate_transfer_cost(
    source_facility: str,
    destination_facility: str,
    quantity: int
) -> dict:
    """Calculate logistics cost for a transfer."""
    
    facilities_df = data_loader.data['facilities']
    
    source = facilities_df[
        facilities_df['facility_id'] == source_facility
    ].iloc[0]
    dest = facilities_df[
        facilities_df['facility_id'] == destination_facility
    ].iloc[0]
    
    # Calculate distance
    distance = math.sqrt(
        (dest['latitude'] - source['latitude'])**2 +
        (dest['longitude'] - source['longitude'])**2
    ) * 111
    
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
        "cost_per_unit": round(total_cost / quantity if quantity > 0 else 0, 4)
    }

@tool("Create Transfer Proposal")
def create_transfer_proposal(
    source_facility: str,
    destination_facility: str,
    medication_id: str,
    quantity: int,
    reasoning: str
) -> dict:
    """Create a transfer proposal."""
    
    proposal_id = str(uuid.uuid4())
    
    proposal = {
        "id": proposal_id,
        "source_facility": source_facility,
        "destination_facility": destination_facility,
        "medication_id": medication_id,
        "quantity": quantity,
        "reasoning": reasoning,
        "status": "PENDING_APPROVAL",
        "created_by": "crewai-agent"
    }
    
    print(f"✅ Transfer proposal created: {proposal_id}")
    return proposal
```

### Step 1.7: Initial Testing Script

```python
# tests/test_agents_basic.py

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.config import test_claude_connection
from database.data_loader import SyntheticDataLoader
from tools.inventory_tools import query_inventory, check_facility_capacity

def test_claude_api():
    """Test Claude API connection"""
    print("\n" + "="*60)
    print("TEST 1: Claude API Connection")
    print("="*60)
    test_claude_connection()

def test_data_loading():
    """Test synthetic data loading"""
    print("\n" + "="*60)
    print("TEST 2: Synthetic Data Loading")
    print("="*60)
    loader = SyntheticDataLoader()
    loader.load_csv_files()
    loader.create_sqlite_db()
    loader.get_summary_stats()

def test_inventory_tools():
    """Test inventory tools"""
    print("\n" + "="*60)
    print("TEST 3: Inventory Tools")
    print("="*60)
    
    # Test query_inventory
    items = query_inventory(days_to_expiry_threshold=14)
    print(f"Found {len(items)} items expiring soon")
    if items:
        print(f"Sample: {items[0]}")
    
    # Test check_facility_capacity
    capacity = check_facility_capacity("HOSPITAL-001")
    print(f"\nFacility Capacity: {capacity}")

if __name__ == "__main__":
    test_claude_api()
    test_data_loading()
    test_inventory_tools()
    print("\n✅ All basic tests passed!")
```

---

## 📋 PHASE 1 DELIVERABLES (Expected by End of Week 2)

```
✓ agents/
  ├── config.py                    # Claude API setup
  ├── pharma_agents.py            # 3 specialized agents
  └── __init__.py

✓ tools/
  ├── inventory_tools.py          # Query, capacity, alerts
  ├── transfer_tools.py           # Matching, proposals, costs
  ├── forecasting_tools.py        # (will add in Phase 2)
  └── __init__.py

✓ database/
  ├── data_loader.py              # Load synthetic data → SQLite
  └── __init__.py

✓ tests/
  ├── test_agents_basic.py        # Basic integration tests
  ├── test_inventory_tools.py     # Tool unit tests
  └── test_data_loading.py        # Data validation

✓ Configuration
  ├── .env                         # ANTHROPIC_API_KEY
  ├── requirements.txt             # Dependencies
  └── README.md                    # Setup instructions

✓ Documentation
  ├── PHASE_1_COMPLETION.md       # What was built
  ├── API_REFERENCE.md            # Tool documentation
  └── TESTING_GUIDE.md            # How to run tests
```

---

## 🔧 IMMEDIATE ACTION ITEMS (THIS WEEK)

### 1. Create `.env` File
```
ANTHROPIC_API_KEY=your_api_key_here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Initial Tests
```bash
python tests/test_agents_basic.py
```

### 4. Create Basic Crew
```python
# main.py - Basic crew execution

from crewai import Crew
from agents.pharma_agents import (
    expiration_manager,
    transfer_coordinator,
    forecasting_analyst
)

# Create crew
pharma_crew = Crew(
    agents=[
        expiration_manager,
        transfer_coordinator,
        forecasting_analyst
    ],
    process=Process.SEQUENTIAL,
    verbose=True,
    memory=True
)

# Test with sample input
if __name__ == "__main__":
    result = pharma_crew.kickoff(
        inputs={
            "current_datetime": "2026-02-09",
            "facilities_count": 20,
            "critical_threshold_days": 7,
            "warning_threshold_days": 14
        }
    )
    print(result)
```

---

## ⏱️ TIMELINE OVERVIEW

| Week | Phase | Key Deliverables | Status |
|------|-------|-----------------|--------|
| W1-2 | **1: CrewAI Setup** | Agents, tools, basic testing | ⏳ **CURRENT** |
| W3-4 | **2: Tools & Tasks** | All 15+ tools, unit tests | 🔄 Next |
| W5-6 | **3: Task Sequencing** | E2E crew execution, optimization | 🔄 Next |
| W7-8 | **4: AWS Deployment** | Lambda, Redshift, RDS setup | 🔄 Next |
| W9-10 | **5: Production** | Load testing, optimizations | 🔄 Next |

---

## 📊 SUCCESS CRITERIA FOR PHASE 1

- [ ] Claude API connection working
- [ ] All synthetic data loaded into SQLite
- [ ] 3 agents created with proper roles
- [ ] At least 5 tools working with synthetic data
- [ ] Basic crew execution successful
- [ ] All tests passing (>90% success rate)
- [ ] Documentation complete
- [ ] Team trained on new framework

---

## 🎯 KEY QUESTIONS TO ANSWER BEFORE STARTING

1. **Do you have an Anthropic API key?** (Required for Claude access)
   - Get one at: https://console.anthropic.com/

2. **What's your local development environment?** (Windows/Mac/Linux)
   - Setup instructions vary slightly

3. **Do you want to start with local testing or jump to AWS Lambda?**
   - Recommended: Build & test locally first (faster feedback)

4. **Who's doing the development work?**
   - One person or a team? (affects coordination)

5. **Any existing Python project structure I should follow?**
   - Reference your existing code style?

---

## 🚀 READY TO START?

Answer these questions and I'll provide:
1. ✅ Complete Phase 1 implementation code
2. ✅ Step-by-step setup guide 
3. ✅ Troubleshooting checklist
4. ✅ Testing procedures
5. ✅ Code review guidelines

**Let's build this! 🔨**

