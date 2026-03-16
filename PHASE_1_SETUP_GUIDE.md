# Phase 1: Foundation Setup - Quick Start Guide

Welcome to the **Pharmaceutical Inventory Optimization Platform**! This guide will help you get the system running on your local machine.

## Overview

This platform uses **CrewAI** to orchestrate three specialized agents that work together to optimize pharmaceutical inventory:

1. **Expiration Manager** - Identifies medications at risk of expiration
2. **Transfer Coordinator** - Optimizes cross-facility transfers  
3. **Forecasting Analyst** - Predicts demand and prevents shortages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CREWAI ORCHESTRATOR                      │
│  (Manages agent communication and task sequencing)          │
└─────────────────────────────────────────────────────────────┘
          │                          │                          │
          ▼                          ▼                          ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │ EXPIRATION   │        │   TRANSFER   │        │ FORECASTING  │
    │   MANAGER    │        │ COORDINATOR  │        │   ANALYST    │
    └──────────────┘        └──────────────┘        └──────────────┘
          │                          │                          │
          ▼                          ▼                          ▼
    ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
    │ Inventory    │        │   Transfer   │        │ Forecasting  │
    │    Tools     │        │    Tools     │        │    Tools     │
    └──────────────┘        └──────────────┘        └──────────────┘
          │                          │                          │
          └──────────────────────────┴──────────────────────────┘
                                    │
                                    ▼
                        ┌─────────────────────┐
                        │   SQLite Database   │
                        │  (Synthetic Data)   │
                        └─────────────────────┘
```

## Prerequisites

### 1. Python Environment
- Python 3.11 or higher
- Virtual environment (venv or conda)
- Linux environment (WSL on Windows is fine)

### 2. Anthropic API Key
- Get your API key from [console.anthropic.com](https://console.anthropic.com/)
- You need an account with Claude API access
- Free credits available for new accounts

### 3. Dependencies
- All Python packages listed in `requirements.txt`

## Installation

### Step 1: Clone/Navigate to Project
```bash
cd pharma-inventory-platform
```

### Step 2: Create Virtual Environment
```bash
# Using venv
python3.11 -m venv venv              # On Linux/Mac
python -m venv venv                  # On Windows

# Activate it
source venv/bin/activate             # On Linux/Mac
.\venv\Scripts\activate              # On Windows
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy template to actual .env file
cp .env.template .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### Step 5: Verify Installation
```bash
# Test Python imports
python -c "import crewai; import langchain_anthropic; print('✅ Imports OK')"

# Test Claude connectivity
python -m agents.config
```

## Project Structure

```
pharma-inventory-platform/
├── agents/                 # Agent definitions and config
│   ├── config.py          # Claude API setup
│   ├── pharma_agents.py   # Three agent definitions
│   └── __init__.py        # Module exports
│
├── tools/                 # Tool implementations
│   ├── inventory_tools.py # Expiration & capacity tools
│   ├── transfer_tools.py  # Transfer coordination tools
│   ├── forecasting_tools.py # Demand prediction tools
│   └── __init__.py        # Module exports
│
├── database/              # Data management
│   ├── data_loader.py     # CSV → SQLite loader
│   └── __init__.py        # Module exports
│
├── data-generation/       # Synthetic data (pre-generated)
│   └── synthetic_data/    # CSV files with sample data
│
├── tests/                 # Test suite
│   ├── test_agents_basic.py # Integration tests
│   └── __init__.py        # Module exports
│
├── main.py               # Main execution script
├── requirements.txt      # Python dependencies
├── .env.template         # Environment template
└── README.md             # This file
```

## Quick Start

### Run Tests (Verify Everything Works)
```bash
# Run all integration tests
python tests/test_agents_basic.py

# Output should show:
# ✅ Data loader initialized
# ✅ Loaded 8 data tables
# ✅ SQLite database created
# ... etc
```

### Run Platform (Single Cycle)
```bash
# Execute one complete analysis cycle
python main.py

# This will:
# 1. Validate prerequisites (API key, data, agents)
# 2. Load synthetic data into SQLite
# 3. Create three agents and assign tools
# 4. Define three sequential tasks
# 5. Execute crew and output results
```

### Load Data Manually
```bash
python database/data_loader.py

# Output shows:
# 📂 Loading CSV Files
# ✅ facilities | 10 rows | 5 columns
# ✅ medications | 3000 rows | 8 columns
# ... etc
```

### Test Individual Agents
```bash
# Test inventory tools
python tools/inventory_tools.py

# Test transfer tools
python tools/transfer_tools.py

# Test forecasting tools
python tools/forecasting_tools.py
```

## Data Files

The system uses pre-generated synthetic data:

- **facilities.csv** - 10 hospital/clinic locations
- **medications.csv** - 3,000 unique medications
- **inventory.csv** - 50,000 inventory batches
- **consumption.csv** - 90 days of consumption history
- **demand_forecast.csv** - 30-day demand forecasts
- **transfers.csv** - Historical transfer records
- **replenishment_orders.csv** - Past replenishment orders
- **external_signals.csv** - Weather, disease, event signals

**Total Data Points:** 500,000+

## Core Components

### Agents (agents/pharma_agents.py)
Three specialized agents working together:

```python
from agents.pharma_agents import create_pharma_agents

agents = create_pharma_agents()
# Returns: (expiration_manager, transfer_coordinator, forecasting_analyst)
```

### Tools (tools/*.py)
15+ tools across three domains:

**Inventory Tools:**
- `query_inventory()` - Get inventory details
- `get_expiring_medications()` - Find items expiring soon
- `check_facility_capacity()` - Check storage utilization
- `create_alert()` - Create pharmacist alerts

**Transfer Tools:**
- `find_transfer_matches()` - Find surplus/shortage pairs
- `calculate_transfer_cost()` - Compute logistics costs
- `create_transfer_proposal()` - Generate proposals
- `check_regulatory_constraints()` - Verify compliance
- `approve_transfer()` - Approve transfers

**Forecasting Tools:**
- `run_demand_forecast()` - 30-day predictions
- `detect_demand_anomaly()` - Find unusual patterns
- `get_external_signals()` - Get weather/disease data
- `assess_stockout_risk()` - 7-day risk assessment
- `recommend_replenishment()` - Suggest orders

### Tasks

The system executes three sequential tasks:

**Task 1: Expiration Analysis** (Expiration Manager)
- Identifies medications expiring within 14 days
- Checks facility capacity utilization
- Creates priority alerts
- Output: Expiration report with actions

**Task 2: Transfer Coordination** (Transfer Coordinator)
- Finds surplus/shortage matches
- Calculates transfer costs
- Checks regulatory constraints
- Output: Transfer proposals with analysis

**Task 3: Demand Forecasting** (Forecasting Analyst)
- Runs 30-day demand forecasts
- Detects consumption anomalies
- Gets external signals
- Output: Replenishment strategy

## Common Issues & Solutions

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Solution: Set the API key in .env
echo "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE" >> .env
```

### Issue: "ModuleNotFoundError: No module named 'crewai'"
```bash
# Solution: Reinstall requirements
pip install --upgrade -r requirements.txt
```

### Issue: "Database file not found"
```bash
# Solution: Load data first
python database/data_loader.py
```

### Issue: CrewAI version conflicts
```bash
# Solution: Create fresh virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Edit `.env` file to customize:

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-...        # Your API key
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Environment
ENVIRONMENT=development              # or production

# Paths
SQLITE_DB_PATH=pharma_dev.db        # Database location
SYNTHETIC_DATA_DIR=data-generation/synthetic_data

# Logging
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
```

## API Usage Examples

### Query Inventory
```python
from tools.inventory_tools import create_inventory_tools

tools = create_inventory_tools()

# Get all inventory
result = tools.query_inventory()
print(f"Total units: {result['total_units']}")

# Get expiring medications
expiring = tools.get_expiring_medications(days_threshold=14)
print(f"Expiring soon: {expiring['expiring_count']}")

# Check facility capacity
capacity = tools.check_facility_capacity("FAC001")
print(f"Utilization: {capacity['utilization_percent']}%")
```

### Find Transfer Opportunities
```python
from tools.transfer_tools import create_transfer_tools

tools = create_transfer_tools()

# Find surplus/shortage matches
matches = tools.find_transfer_matches()
print(f"Found {matches['total_matches']} opportunities")

# Calculate cost for a transfer
cost = tools.calculate_transfer_cost("FAC001", "FAC002", 500)
print(f"Cost: ${cost['total_cost']}")
```

### Run Demand Forecast
```python
from tools.forecasting_tools import create_forecasting_tools

tools = create_forecasting_tools()

# Forecast demand
forecast = tools.run_demand_forecast("MED001", "FAC001", days=30)
print(f"30-day forecast: {forecast['forecast']}")

# Assess stockout risk
risk = tools.assess_stockout_risk("MED001", "FAC001")
print(f"Risk level: {risk['risk_level']}")

# Get replenishment recommendation
replenish = tools.recommend_replenishment("MED001", "FAC001")
print(f"Order {replenish['recommended_order_quantity']} units")
```

## Next Steps

After Phase 1 is complete:

1. **Phase 2:** Expand tools, add external APIs (weather, disease data)
2. **Phase 3:** Implement task sequencing with crew execution
3. **Phase 4:** Deploy to AWS (Lambda, RDS, Step Functions)
4. **Phase 5:** Scale to production (multi-region, monitoring)

## Support

### Common Commands
```bash
# Check system status
python main.py

# Run tests
python tests/test_agents_basic.py

# Load fresh data
python database/data_loader.py

# Test individual tools
python tools/inventory_tools.py
python tools/transfer_tools.py
python tools/forecasting_tools.py
```

### Environment Details
- **Python:** 3.11+
- **CrewAI:** 0.35.0 with LangChain
- **Claude:** 3.5 Sonnet via Anthropic API
- **Database:** SQLite (development)
- **Data:** 500K+ synthetic records

## License & Attribution

This project is built using:
- **CrewAI Framework** - Agent orchestration
- **Claude API** - LLM backbone
- **LangChain** - LLM integrations
- **Pandas/NumPy** - Data processing
- **Prophet** - Time-series forecasting

---

**Ready to get started?** Run `python main.py` and watch the agents work!

For detailed technical documentation, see [ARCHITECTURE_CREWAI.md](../docs/ARCHITECTURE_CREWAI.md)
