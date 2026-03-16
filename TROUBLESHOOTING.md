# Quick Troubleshooting Guide

## Common Setup Issues & Solutions

### Issue 1: "ANTHROPIC_API_KEY not found" Error
**Error Message:**
```
❌ Claude API not configured
   → Set ANTHROPIC_API_KEY in .env file
```

**Solution:**
```bash
# 1. Get your API key from https://console.anthropic.com/
# 2. Open .env file
cat .env

# 3. Add your key
echo "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE" >> .env

# 4. Verify it's been saved
grep ANTHROPIC_API_KEY .env
```

---

### Issue 2: "ModuleNotFoundError: No module named 'crewai'"
**Error Message:**
```
ModuleNotFoundError: No module named 'crewai'
```

**Solution:**
```bash
# 1. Check virtual environment is activated
source venv/bin/activate  # On Linux/Mac
.\venv\Scripts\activate   # On Windows

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install requirements
pip install -r requirements.txt

# 4. Verify installation
python -c "import crewai; print('✅ CrewAI installed')"
```

---

### Issue 3: "ModuleNotFoundError: No module named 'langchain_anthropic'"
**Error Message:**
```
ModuleNotFoundError: No module named 'langchain_anthropic'
```

**Solution:**
```bash
# Install the missing LangChain Anthropic integration
pip install langchain-anthropic

# Verify
python -c "from langchain_anthropic import ChatAnthropic; print('✅ OK')"
```

---

### Issue 4: "sqlite3.OperationalError: unable to open database file"
**Error Message:**
```
sqlite3.OperationalError: unable to open database file
```

**Solution:**
```bash
# 1. Check if synthetic data exists
ls data-generation/synthetic_data/

# Should see: consumption.csv, demand_forecast.csv, etc.

# 2. Load the data first
python database/data_loader.py

# 3. Verify database was created
ls -la pharma_dev.db
```

---

### Issue 5: "FileNotFoundError: synthetic data directory not found"
**Error Message:**
```
FileNotFoundError: Synthetic data directory not found
```

**Solution:**
```bash
# 1. Check current directory
pwd

# Should be: pharma-inventory-platform

# 2. Check if data-generation dir exists
ls data-generation/synthetic_data/

# 3. If missing, you're in wrong directory
# Navigate to project root:
cd pharma-inventory-platform

# 4. Try loading data again
python database/data_loader.py
```

---

### Issue 6: "ImportError: cannot import name 'Agent' from 'crewai'"
**Error Message:**
```
ImportError: cannot import name 'Agent' from 'crewai'
```

**Solution:**
```bash
# The installed crewai version is incompatible
# Reinstall with correct version

pip uninstall crewai -y
pip install crewai==0.35.0

# Verify
python -c "from crewai import Agent, Crew, Task; print('✅ OK')"
```

---

### Issue 7: "pandas.errors.ParserError: Error tokenizing data"
**Error Message:**
```
pandas.errors.ParserError: Error tokenizing data with C engine
```

**Solution:**
```bash
# CSV files might be corrupted
# Regenerate synthetic data:

cd data-generation/
python synthetic_data_generator_lite.py

# Then reload
cd ..
python database/data_loader.py
```

---

### Issue 8: Test Fails with "AssertionError: 'success' != 'no_historical_data'"
**Error Message:**
```
AssertionError: 'success' != 'no_historical_data'
```

**Solution:**
```bash
# Data hasn't been loaded into SQLite yet

# 1. Load the data
python database/data_loader.py

# 2. Verify it worked
python -c "from database.data_loader import get_data_loader; l = get_data_loader(); print(f'DB exists: {l.db_path.exists()}')"

# 3. Run tests again
python tests/test_agents_basic.py
```

---

### Issue 9: "TypeError: 'ChatAnthropic' object is not callable"
**Error Message:**
```
TypeError: 'ChatAnthropic' object is not callable
```

**Solution:**
```bash
# The agent LLM assignment is incorrect
# This is already fixed in pharma_agents.py

# Just reinstall:
pip install --upgrade -r requirements.txt

# Then run again:
python main.py
```

---

### Issue 10: "KeyError: 'medication_id' in forecast tool"
**Error Message:**
```
KeyError: 'medication_id' in DataFrame
```

**Solution:**
```bash
# The CSV column names don't match expectations
# Verify synthetic data columns:

python -c "
import pandas as pd
df = pd.read_csv('data-generation/synthetic_data/medications.csv')
print('Columns:', df.columns.tolist())
"

# Should include: medication_id, medication_name, category, etc.

# If not, regenerate data:
cd data-generation/
python synthetic_data_generator.py
```

---

## Installation Verification Checklist

Run this to verify everything is set up correctly:

```bash
#!/bin/bash

echo "🔍 Phase 1 Installation Verification"
echo "===================================="

# 1. Python version
echo -e "\n1️⃣ Checking Python version..."
python --version

# Should be 3.11+

# 2. Virtual environment
echo -e "\n2️⃣ Checking virtual environment..."
which python

# Should show path to venv

# 3. Required packages
echo -e "\n3️⃣ Checking required packages..."
python -c "
import crewai
import langchain
import langchain_anthropic
import pandas
import anthropic
import pydantic
print('✅ All packages installed')
"

# 4. .env file
echo -e "\n4️⃣ Checking .env file..."
if [ -f .env ]; then
    echo "✅ .env file exists"
    if grep -q ANTHROPIC_API_KEY .env; then
        echo "✅ ANTHROPIC_API_KEY is set"
    else
        echo "❌ ANTHROPIC_API_KEY not found in .env"
    fi
else
    echo "❌ .env file not found"
fi

# 5. Synthetic data
echo -e "\n5️⃣ Checking synthetic data..."
if [ -d "data-generation/synthetic_data" ]; then
    count=$(ls data-generation/synthetic_data/*.csv 2>/dev/null | wc -l)
    echo "✅ Found $count CSV files"
else
    echo "❌ Synthetic data directory not found"
fi

# 6. Claude connectivity
echo -e "\n6️⃣ Testing Claude API..."
python agents/config.py

# 7. Data loading
echo -e "\n7️⃣ Testing data loader..."
python -c "from database.data_loader import get_data_loader; l = get_data_loader(); l.load_csv_files(); print('✅ Data loaded successfully')"

# 8. Agents
echo -e "\n8️⃣ Testing agents..."
python -c "from agents.pharma_agents import create_pharma_agents; agents = create_pharma_agents(); print(f'✅ Created {len(agents)} agents')"

echo -e "\n===================================="
echo "✅ Verification complete!"
```

Save as `verify_setup.sh` and run:
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

---

## Quick Fixes for Common Issues

### "Everything broke after an update"
```bash
# Start fresh
deactivate                              # Exit venv
rm -rf venv                             # Remove venv
python -m venv venv                     # Create new venv
source venv/bin/activate                # Activate
pip install -r requirements.txt         # Install fresh
python main.py                          # Test
```

### "Database is corrupted"
```bash
# Delete and recreate
rm pharma_dev.db
python database/data_loader.py
```

### "Agent won't start"
```bash
# Check agent initialization
python -c "
from agents.pharma_agents import create_pharma_agents
try:
    agents = create_pharma_agents()
    for agent in agents:
        print(f'✅ {agent.role}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### "Tools aren't being recognized"
```bash
# Verify tools are properly initialized
python -c "
from tools.inventory_tools import create_inventory_tools
tools = create_inventory_tools()
print('✅ Tools initialized')
print(dir(tools))  # Lists all methods
"
```

---

## Environment Variable Reference

Required variables in `.env`:

```env
# Required - Must get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE

# Optional - Defaults shown
CLAUDE_MODEL=claude-3-5-sonnet-20241022
ENVIRONMENT=development
SQLITE_DB_PATH=pharma_dev.db
SYNTHETIC_DATA_DIR=data-generation/synthetic_data
LOG_LEVEL=INFO
```

---

## Running Individual Components

### Just Load Data
```bash
python database/data_loader.py
```

### Just Test Inventory Tools
```bash
python tools/inventory_tools.py
```

### Just Test Transfer Tools
```bash
python tools/transfer_tools.py
```

### Just Test Forecasting Tools
```bash
python tools/forecasting_tools.py
```

### Just Test Agents
```bash
python -c "
from agents.pharma_agents import create_pharma_agents
agents = create_pharma_agents()
for agent in agents:
    print(f'✅ {agent.role}')
"
```

### Just Run Tests
```bash
python tests/test_agents_basic.py
```

---

## Getting Further Help

1. **Check Documentation**
   - [PHASE_1_SETUP_GUIDE.md](PHASE_1_SETUP_GUIDE.md) - Complete setup
   - [PHASE_1_COMPLETION_SUMMARY.md](PHASE_1_COMPLETION_SUMMARY.md) - What was created
   - Code comments - Implementation details

2. **Check Environment**
   ```bash
   python -c "
   import sys
   print(f'Python: {sys.version}')
   print(f'Executable: {sys.executable}')
   "
   ```

3. **Check Dependencies**
   ```bash
   pip list | grep -E 'crewai|langchain|anthropic|pandas'
   ```

4. **Check Data**
   ```bash
   python -c "
   from database.data_loader import get_data_loader
   l = get_data_loader()
   l.load_csv_files()
   l.get_summary_stats()
   "
   ```

---

## Success Indicators

You'll know everything is working when you see:

✅ `tests/test_agents_basic.py` runs without errors
✅ `python main.py` starts cruise execution
✅ Data loads cleanly: `python database/data_loader.py`
✅ Agents initialize: 3 agents created
✅ Tools work: `python tools/*.py` runs successfully
✅ No Python import errors
✅ No ANTHROPIC_API_KEY errors

If you see all of these, **Phase 1 is ready to use!**

---

**Got stuck?** Start with #1 (API key), then work down the list in order.
