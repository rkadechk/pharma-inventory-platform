# CrewAI Integration Guide

## 🤖 What is CrewAI?

CrewAI is a framework for orchestrating **collaborative AI agents** to work together on complex tasks. In your pharmaceutical platform, agents analyze real data and generate intelligent recommendations.

---

## 📋 Your CrewAI Setup

Your system now has **4 specialized agents**:

### 1. Risk Assessment Specialist
- **Role:** Analyzes expiration risks in inventory
- **Input:** 3,000+ inventory batches with expiration dates
- **Output:** Risk-prioritized recommendations (transfers, disposals, donations)
- **Endpoint:** `POST /api/v1/crew/analyze/expiration-risk`
- **Response Time:** 30-60 seconds

### 2. Supply Chain Optimizer
- **Role:** Recommends optimal transfer decisions
- **Input:** 500+ transfer proposals with costs and benefits
- **Output:** Priority transfer list with cost-benefit analysis
- **Endpoint:** `POST /api/v1/crew/analyze/transfer-optimization`
- **Response Time:** 30-60 seconds

### 3. Demand Forecast Analyst
- **Role:** Interprets demand forecasts and identifies risks
- **Input:** 4,500+ demand forecasts with confidence scores
- **Output:** Stockout risks, reorder recommendations, anomaly analysis
- **Endpoint:** `POST /api/v1/crew/analyze/demand-forecast`
- **Response Time:** 30-60 seconds

### 4. Executive Report Generator
- **Role:** Synthesizes all analyses into actionable reports
- **Input:** Risk, optimization, and demand analyses
- **Output:** Executive summary with top 10 recommendations
- **Endpoint:** `POST /api/v1/crew/analyze/full-assessment`
- **Response Time:** 1-2 minutes

---

## 🚀 Getting Started

### Prerequisites

You need OpenAI API access:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."
```

### Install Dependencies

```bash
pip install crewai langchain-openai
```

**Or update from requirements.txt:**
```bash
pip install -r requirements.txt
```

---

## 📡 API Endpoints

### 1. Risk Assessment Analysis
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk
```

**Response:**
```json
{
  "status": "success",
  "analysis_type": "expiration_risk",
  "data": {
    "analysis": {
      "analysis_type": "expiration_risk",
      "summary": "...",
      "critical_count": 34,
      "at_risk_value": 245000.00
    },
    "recommendations": "Based on analysis, recommend immediate transfers of..."
  }
}
```

### 2. Transfer Optimization Analysis
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/transfer-optimization
```

**Response:**
```json
{
  "status": "success",
  "analysis_type": "transfer_optimization",
  "data": {
    "analysis": {
      "analysis_type": "transfer_optimization",
      "summary": "...",
      "pending_count": 123,
      "potential_savings": 45000.00
    },
    "recommendations": "Top 3 transfers: 1) Hospital A→B (savings $12K)..."
  }
}
```

### 3. Demand Forecast Analysis
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast
```

**Response:**
```json
{
  "status": "success",
  "analysis_type": "demand_forecast",
  "data": {
    "analysis": {
      "analysis_type": "demand_forecast",
      "summary": "...",
      "critical_urgency": 12,
      "anomalies_detected": 47
    },
    "recommendations": "Critical medications needing immediate reorder..."
  }
}
```

### 4. Full Assessment (All Agents)
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment
```

**Response:**
```json
{
  "status": "success",
  "analysis_type": "full_assessment",
  "data": {
    "risk_analysis": {...},
    "optimization_analysis": {...},
    "demand_analysis": {...},
    "executive_report": "## Pharmaceutical Operations Executive Summary\n\n..."
  }
}
```

### 5. Agent Status
```bash
curl http://localhost:8000/api/v1/crew/status
```

### 6. Agent Documentation
```bash
curl http://localhost:8000/api/v1/crew/docs/agents
```

---

## 🔧 How It Works

### Data Flow

```
User Request
    ↓
FastAPI Route (/api/v1/crew/*)
    ↓
PharmacyCrew (Agent Orchestrator)
    ↓
Individual Agent (Risk/Opt/Demand/Report)
    ↓
LLM (GPT-4-Turbo)
    ↓
AI-Generated Recommendations
    ↓
JSON Response to User
```

### Example: Risk Assessment Flow

```python
1. User calls: POST /api/v1/crew/analyze/expiration-risk
2. PharmacyCrew loads 3,000 inventory records from CSV
3. ExpirationRiskAnalyst calculates metrics:
   - 34 critical batches
   - $245K at-risk value
   - Top expiring items
4. Risk Assessment Agent (GPT-4) receives this data
5. Agent analyzes and generates recommendations:
   - "Transfer 23 batches to Hospital B immediately"
   - "Donate remaining 11 batches to clinics"
   - "Est. $42K waste reduction"
6. Response returned in 45 seconds
```

---

## 💡 Use Cases

### 1. Morning Briefing
Get daily risk assessment:
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk \
  | jq '.data.recommendations'
```

Use for: Daily standups, risk reviews

### 2. Weekly Operations Review
Get comprehensive assessment:
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment \
  | jq '.data.executive_report'
```

Use for: Weekly planning, stakeholder meetings

### 3. Transfer Decision Support
Before approving any transfer:
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/transfer-optimization \
  | jq '.data.recommendations'
```

Use for: Transfer approval process, cost validation

### 4. Inventory Replenishment
Determine reorder quantities:
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast \
  | jq '.data.recommendations'
```

Use for: Procurement orders, supplier communication

---

## 🔌 Integration with PowerBI

Combine CrewAI recommendations with PowerBI dashboards:

1. **PowerBI Dashboard:** Visual data at `localhost:8000/docs`
2. **CrewAI Endpoint:** Call agent for recommendations
3. **Executive Report:** Display in Excel/PowerPoint

Example Workflow:
```
1. View PowerBI Expiration Risk dashboard
2. See 34 critical batches, $245K risk
3. Click "Get AI Recommendations" → CrewAI endpoint
4. Agent returns priority transfer list
5. Use that list to execute transfers
6. Monitor impact in PowerBI
```

---

## 📊 Response Format Guide

All CrewAI endpoints return:

```json
{
  "status": "success|error",
  "analysis_type": "expiration_risk|transfer_optimization|demand_forecast|full_assessment",
  "data": {
    "analysis": {
      // Raw data metrics and summaries
    },
    "recommendations": "AI-generated recommendations text"
  },
  "timestamp": "2025-02-19T22:45:00.000000"
}
```

Parse recommendations:
```python
import requests
import json

response = requests.post("http://localhost:8000/api/v1/crew/analyze/expiration-risk")
data = response.json()

# Get AI recommendations
recommendations = data['data']['recommendations']
print(recommendations)
# Output: "Based on analysis of 3000 inventory batches..."
```

---

## ⚡ Performance Tips

### Tip 1: Cache Results
Save recommendations for 1-2 hours:
```python
import time
from functools import lru_cache

@lru_cache(maxsize=4)
def get_crew_analysis():
    return requests.post(
        "http://localhost:8000/api/v1/crew/analyze/expiration-risk"
    ).json()
```

### Tip 2: Batch Requests
Call multiple agents in sequence (not parallel - CrewAI needs sequential reasoning):
```python
# Sequential approach
risk = requests.post("http://localhost:8000/api/v1/crew/analyze/expiration-risk")
transfer = requests.post("http://localhost:8000/api/v1/crew/analyze/transfer-optimization")
demand = requests.post("http://localhost:8000/api/v1/crew/analyze/demand-forecast")
```

### Tip 3: Schedule Analysis
Run daily/weekly analyses in background:
```python
# In your scheduler (APScheduler, Celery, etc.)
@scheduler.scheduled_job('cron', hour=9)  # 9 AM daily
def daily_risk_assessment():
    requests.post("http://localhost:8000/api/v1/crew/analyze/expiration-risk")
    # Save results to database or log
```

### Tip 4: Monitor API Logs
Check what agents are doing:
```bash
curl http://localhost:8000/api/v1/crew/status | jq '.available_agents'
```

---

## 🛠️ Customization

### Add New Agent

1. **Create analyzer class** in `agents/crewai_pharmacy.py`:
```python
class MyAnalyzer:
    def analyze(self) -> dict:
        # Your analysis logic
        return {"key": "value"}
```

2. **Create agent** in `PharmacyCrewAgents`:
```python
@staticmethod
def create_my_agent():
    return Agent(
        role="Your Role",
        goal="Your goal",
        backstory="Your backstory",
        llm=llm,
        verbose=True,
    )
```

3. **Add task method** in `PharmacyCrew`:
```python
def run_my_analysis(self) -> dict:
    agent = PharmacyCrewAgents.create_my_agent()
    task = Task(description="...", agent=agent)
    crew = Crew(agents=[agent], tasks=[task])
    return {"result": crew.kickoff()}
```

4. **Add FastAPI route** in `app/routes/crew.py`:
```python
@router.post("/analyze/my-analysis")
async def analyze_my_analysis():
    crew = PharmacyCrew()
    result = await loop.run_in_executor(executor, crew.run_my_analysis)
    return {"data": result}
```

---

## 🔐 Important Notes

### API Key Management
```bash
# NEVER commit your API key
export OPENAI_API_KEY="sk-..."

# For production, use environment variables or secrets manager
```

### Cost Considerations
Each analysis call uses GPT-4-Turbo:
- Risk/Opt/Demand agents: ~$0.20-0.50 per call (30-60 sec)
- Full assessment: ~$1.00-2.00 per call (1-2 min)

**Estimate:** 
- 10 daily risk assessments = $2/day
- 5 weekly full assessments = $5/week
- Total = ~$30/month

### Response Times
- Single agent: 30-60 seconds (LLM reasoning)
- Multi-agent: 1-2 minutes (sequential coordination)
- Don't expect instant responses - this is complex reasoning!

---

## ❓ Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-..."  # Set key
pkill -f uvicorn  # Restart API
```

### "Agent timed out"
- API is busy - wait and retry
- Full assessment takes longer - be patient
- Consider scheduling off-peak hours

### "LLM returned invalid output"
- Happens occasionally
- Endpoint will retry automatically
- Check logs for details

### "Too many requests"
- OpenAI rate limit hit
- Space out calls by ~30 seconds
- Batch requests during off-peak

---

## 📈 What's Next?

1. **Test agents** with sample data
2. **Integrate with PowerBI** for visual + AI insights
3. **Schedule daily/weekly analyses** for management
4. **Build custom agents** for your specific needs
5. **Create dashboards** that show AI recommendations

---

## 🎯 Summary

Your CrewAI setup gives you:
- ✅ 4 specialized AI agents
- ✅ Real-time analysis of 8,000+ pharmaceutical records
- ✅ Intelligent recommendations (cost, compliance, risk)
- ✅ Executive-level reporting
- ✅ Easy API integration with FastAPI
- ✅ Compatible with existing PowerBI dashboards

**Ready to build smarter pharmacy operations!**

---

**Documentation created:** February 19, 2025
**Framework:** CrewAI + GPT-4-Turbo
**Status:** Ready to deploy
