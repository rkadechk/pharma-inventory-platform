# CrewAI Quick Start - 5 Minutes to Your First AI Analysis

## 🚀 Get Running in 5 Steps

### Step 1: Get OpenAI API Key (2 min)
1. Go to https://platform.openai.com/api/keys
2. Create a new API key
3. Copy it (you'll only see it once)

### Step 2: Set Environment Variable (1 min)
```bash
export OPENAI_API_KEY="sk-proj-..."
```

### Step 3: Install Dependencies (2 min)
```bash
pip install crewai langchain-openai
```

Or update from requirements:
```bash
pip install -r requirements.txt --upgrade
```

### Step 4: Start API Server
```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

### Step 5: Make Your First Request!
```bash
# Risk Assessment Analysis
curl -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk

# Transfer Optimization
curl -X POST http://localhost:8000/api/v1/crew/analyze/transfer-optimization

# Demand Forecast Analysis
curl -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast

# Full Assessment (all agents)
curl -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment
```

**That's it!** ✅ Your CrewAI agents are now analyzing your pharmaceutical data.

---

## 📊 What You Get

Each call returns:

```json
{
  "status": "success",
  "analysis_type": "expiration_risk|transfer_optimization|demand_forecast",
  "data": {
    "analysis": {
      // Data metrics and summaries
    },
    "recommendations": "AI-generated insights and recommendations..."
  }
}
```

---

## 🎯 Try These Examples

### Example 1: Daily Risk Check
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk | jq '.data.recommendations'
```

**Output:** AI recommendations for managing expiring inventory

### Example 2: Transfer Decisions
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/transfer-optimization | jq '.data.analysis.potential_savings'
```

**Output:** Potential savings from transfers (e.g., `$45000.00`)

### Example 3: Forecast Risks
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast | jq '.data.analysis.critical_urgency'
```

**Output:** Number of critical medications (e.g., `12`)

### Example 4: Executive Report
```bash
curl -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment | jq '.data.executive_report'
```

**Output:** Full executive report with top 10 recommendations (takes 1-2 min)

---

## 📱 In Python

```python
import requests
import json

# Call CrewAI risk assessment
response = requests.post("http://localhost:8000/api/v1/crew/analyze/expiration-risk")
result = response.json()

# Extract recommendations
recommendations = result['data']['recommendations']
print(recommendations)
# Output: "Based on analysis of 3000 inventory batches, 
#          recommend immediate transfers of 23 batches..."

# Extract metrics
at_risk_value = result['data']['analysis']['at_risk_value']
print(f"At-Risk Value: ${at_risk_value:,.2f}")
# Output: "At-Risk Value: $245,000.00"
```

---

## 🔗 API Endpoints Reference

| Endpoint | Purpose | Time | Best For |
|----------|---------|------|----------|
| `/api/v1/crew/analyze/expiration-risk` | Expiration risk analysis | 30-60s | Daily risk check |
| `/api/v1/crew/analyze/transfer-optimization` | Transfer recommendations | 30-60s | Before approval |
| `/api/v1/crew/analyze/demand-forecast` | Demand risk assessment | 30-60s | Replenishment |
| `/api/v1/crew/analyze/full-assessment` | Comprehensive report | 1-2m | Weekly review |
| `/api/v1/crew/status` | Agent status check | <1s | Health check |
| `/api/v1/crew/docs/agents` | Agent documentation | <1s | Reference |

---

## 💡 Common Workflows

### Morning Risk Brief (3 min)
```bash
#!/bin/bash
echo "=== Morning Pharmacy Brief ==="
curl -s -X POST http://localhost:8000/api/v1/crew/analyze/expiration-risk | jq '.data.analysis.critical_count'
echo "critical batches expiring in 7 days"
curl -s -X POST http://localhost:8000/api/v1/crew/analyze/demand-forecast | jq '.data.analysis.critical_urgency'
echo "medications at critical urgency"
```

### Weekly Operations Review (10 min)
```bash
#!/bin/bash
echo "=== Weekly Operations Review ==="
curl -s -X POST http://localhost:8000/api/v1/crew/analyze/full-assessment | \
  jq '.data.executive_report' > weekly_report.txt
echo "Report saved to weekly_report.txt"
```

### Before Transfer Approval
```python
# Check AI recommendation before approving transfer
response = requests.post("http://localhost:8000/api/v1/crew/analyze/transfer-optimization")
recommendations = response.json()['data']['recommendations']

if 'recommend' in recommendations.lower():
    print("✅ AI recommends this transfer")
else:
    print("⚠️ AI has concerns - review details")
```

---

## ⚠️ Important Notes

### API Key Security
```bash
# ✅ Good
export OPENAI_API_KEY="sk-..."

# ❌ Bad - never commit to git!
OPENAI_API_KEY = "sk-..."  # in source code
```

### Response Times
- First request: **45-60 seconds** (LLM reasoning)
- Subsequent requests: **30-45 seconds** (LLM might be faster)
- Full assessment: **1-2 minutes** (multi-agent coordination)

**This is normal** - the agents are doing complex reasoning on your data!

### Cost
- Each request to GPT-4: ~$0.20-2.00 depending on analysis
- Daily risk check (10x): ~$2/day
- Weekly full assessment (2x): ~$4/week
- Monthly budget: ~$40-50

---

## 🛠️ Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="sk-..."
# Then restart: pkill -f uvicorn
```

### "Module not found: crewai"
```bash
pip install crewai langchain-openai
```

### "Request timed out"
- APIs are sometimes slow - retry after 30 seconds
- Full assessment takes 1-2 minutes - be patient
- Check status: `curl http://localhost:8000/api/v1/crew/status`

### "Invalid API key"
- Verify key is correct: `echo $OPENAI_API_KEY`
- Check at https://platform.openai.com/account/api-keys
- Create a new one if needed

---

## 📚 Next Steps

1. ✅ Test all 4 agents with sample requests
2. ✅ Review sample outputs in the integration guide
3. ✅ Integrate into your workflow/dashboards
4. ✅ Schedule daily/weekly analyses
5. ✅ Build custom agents for specific needs

---

## 🎓 Learn More

- **Full Documentation:** See `CREWAI_INTEGRATION_GUIDE.md`
- **Framework Docs:** https://docs.crewai.com/
- **API Reference:** Check `/api/v1/crew/docs/agents` endpoint
- **Examples:** See Python examples in this guide

---

**Status:** ✅ Ready to Deploy
**Framework:** CrewAI + GPT-4-Turbo
**Support:** Check endpoints at http://localhost:8000/docs

You're all set! Start analyzing. 🚀
