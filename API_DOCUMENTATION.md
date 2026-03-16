# Pharmaceutical Inventory Management API

**Production-ready FastAPI application for pharmaceutical inventory optimization**

---

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install FastAPI and Uvicorn (if not already included):**
```bash
pip install fastapi uvicorn
```

### Running the API

```bash
# From the project root directory
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using the built-in main
cd app && python3 main.py
```

The API will start on: **http://localhost:8000**

---

## 📖 API Documentation

### Interactive Swagger UI
Visit: **http://localhost:8000/docs**

Features:
- Try out endpoints directly in the browser
- See request/response examples
- View all available parameters
- Test with real data

### ReDoc Documentation
Visit: **http://localhost:8000/redoc**

Features:
- Clean, readable API documentation
- Organized by tags and endpoints
- Detailed descriptions and examples

### OpenAPI Specification
Visit: **http://localhost:8000/openapi.json**

- Full OpenAPI 3.0 specification
- Machine-readable API contract
- Can be imported into API clients, gateways, etc.

---

## 🔌 API Endpoints

### Health & Status
```
GET  /api/v1/health              - Service health check
GET  /api/v1/ready               - Readiness probe
GET  /api/v1/version             - API version info
```

### Full Optimization Pipeline (Main Endpoint)
```
POST /api/v1/optimization/run    - Run complete 7-stage optimization
GET  /api/v1/optimization/status/{id} - Check optimization status
```

### Demand Forecasting
```
POST /api/v1/demand/forecast     - Single medication forecast
POST /api/v1/demand/forecast-batch - Multiple medication forecasts
```

### Inventory Analysis
```
POST /api/v1/inventory/analyze   - Inventory risk analysis
GET  /api/v1/inventory/facilities/{id} - Get facility inventory
```

### Supply Chain Optimization
```
POST /api/v1/supply/optimize     - Supply chain decisions
GET  /api/v1/supply/suppliers    - List available suppliers
GET  /api/v1/supply/transfer-costs - Get transfer cost matrix
```

---

## 📊 Example Usage

### 1. Full Optimization (Most Common)

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/run" \
  -H "Content-Type: application/json" \
  -d '{
    "facility_inventory": [
      {
        "facility_id": "FAC001",
        "batch_id": "B001",
        "medication_id": 1,
        "quantity_on_hand": 100,
        "expiry_date": "2026-03-15",
        "unit_cost": 10.50
      }
    ],
    "consumption_history": [
      {
        "date": "2026-02-19",
        "facility_id": "FAC001",
        "medication_id": 1,
        "units_consumed": 45
      }
    ],
    "suppliers": [
      {
        "supplier_id": "SUP001",
        "name": "Global Pharma",
        "lead_time_days": 3,
        "min_order_units": 50,
        "unit_cost": 8.50
      }
    ],
    "forecast_days": 30
  }'
```

### 2. Demand Forecasting

```bash
curl -X POST "http://localhost:8000/api/v1/demand/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "medication_id": 1,
    "consumption_data": [
      {
        "date": "2026-02-19",
        "facility_id": "FAC001",
        "units_consumed": 45
      }
    ],
    "forecast_days": 30
  }'
```

### 3. Health Check

```bash
curl "http://localhost:8000/api/v1/health"
```

---

## 🏗️ API Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│         (app/main.py)                   │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┼─────────┐
     │         │         │
     ▼         ▼         ▼
  Health  Optimization  Agent Routes
  Routes    Routes      (Demand, Inventory, Supply)
     │         │         │
     └─────────┼─────────┘
               │
     ┌─────────┴──────────┐
     │                    │
     ▼                    ▼
  Schemas            Agents
  (Request/Response)  (Core Logic)
```

### Routes Structure
```
app/
├── main.py              # FastAPI application
├── routes/
│   ├── health.py       # Health check endpoints
│   ├── optimization.py  # Full pipeline endpoint
│   ├── demand.py       # Demand forecasting endpoints
│   ├── inventory.py    # Inventory analysis endpoints
│   └── supply_chain.py # Supply optimization endpoints
└── schemas/
    ├── common.py       # Common schemas (Health, Error, Metrics)
    ├── demand.py       # Demand request/response models
    ├── inventory.py    # Inventory request/response models
    ├── supply_chain.py # Supply chain request/response models
    └── optimization.py # Full optimization request/response models
```

---

## 📥 Request Examples

### Full Optimization Request
```json
{
  "facility_inventory": [
    {
      "facility_id": "hospital_1",
      "batch_id": "batch_001",
      "medication_id": 5,
      "quantity_on_hand": 200,
      "expiry_date": "2026-06-30",
      "unit_cost": 15.75
    }
  ],
  "consumption_history": [
    {
      "date": "2026-02-19",
      "facility_id": "hospital_1",
      "medication_id": 5,
      "units_consumed": 45
    },
    {
      "date": "2026-02-18",
      "facility_id": "hospital_1",
      "medication_id": 5,
      "units_consumed": 48
    }
  ],
  "suppliers": [
    {
      "supplier_id": "supplier_a",
      "name": "PharmaCorp Supply",
      "lead_time_days": 2,
      "min_order_units": 100,
      "unit_cost": 12.50
    }
  ],
  "forecast_days": 30,
  "budget_constraint": 50000.00
}
```

---

## 📤 Response Example

### Full Optimization Response
```json
{
  "status": "completed",
  "execution_time_seconds": 2.45,
  "timestamp": "2026-02-19T21:35:00",
  "demand_forecasts": [
    {
      "medication_id": 5,
      "medication_name": "Med_5",
      "forecast_date": "2026-02-19T21:35:00",
      "predicted_demand_units": 1350,
      "confidence_level": 0.89,
      "model_type": "PROPHET",
      "model_accuracy_mape": 0.14,
      "forecast_points": [...],
      "anomalies_detected": []
    }
  ],
  "inventory_recommendations": [...],
  "supply_decisions": [...],
  "action_plan": {...},
  "system_metrics": {
    "total_medications": 205,
    "total_facilities": 8,
    "total_inventory_value": 2500000.50,
    "medications_at_risk": 12,
    "estimated_savings": 180000.00,
    "forecast_accuracy_mape": 0.145
  },
  "quality_report": {
    "overall_quality_score": 0.87,
    "data_completeness": {...},
    "validation_summary": {...},
    "system_health": {...},
    "recommendations": []
  },
  "validation_results": {...},
  "warnings": [],
  "errors": []
}
```

---

## 🔒 Security Considerations

### For Production Deployment:
1. **API Key Authentication** - Add token-based authentication
2. **Rate Limiting** - Implement rate limits per client
3. **Input Sanitization** - Validate all inputs (already done via Pydantic)
4. **HTTPS Only** - Force SSL/TLS in production
5. **CORS Configuration** - Restrict to specific origins
6. **Logging & Monitoring** - Set up comprehensive monitoring

---

## 📊 Performance Metrics

| Operation | Typical Time | Notes |
|-----------|-------------|-------|
| Health Check | < 100ms | Lightweight |
| Demand Forecast | 1-3 sec | Prophet model training |
| Inventory Analysis | 1-2 sec | Batch processing |
| Supply Optimization | 1-2 sec | Decision algorithm |
| Full Pipeline | 2-5 sec | All 7 stages |

---

## 🐛 Error Handling

### Standard Error Response
```json
{
  "error_code": "INVALID_INPUT",
  "message": "Invalid medication_id provided",
  "details": {
    "field": "medication_id",
    "value": -1
  },
  "timestamp": "2026-02-19T21:35:00"
}
```

### Common Error Codes
- `INVALID_INPUT` (400) - Bad request data
- `VALIDATION_ERROR` (422) - Schema validation failure
- `NOT_FOUND` (404) - Resource not found
- `INTERNAL_SERVER_ERROR` (500) - Server error

---

## 🧪 Testing the API

### Using Swagger UI (Recommended)
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in the parameters
4. Click "Execute"

### Using cURL
```bash
curl -X POST "http://localhost:8000/api/v1/optimization/run" \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Using Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/optimization/run',
    json={...}
)

print(response.json())
```

### Using Postman
1. Import the OpenAPI spec: http://localhost:8000/openapi.json
2. Create a new request
3. Select endpoint and fill in body
4. Send request

---

## 📈 Monitoring & Logging

The API includes comprehensive logging:

```
app.main - INFO - Pharmaceutical Inventory Management API Starting
app.routes.optimization - INFO - Starting optimization pipeline with 45 batches
app.agents.orchestrator - INFO - ✓ All input data validation passed
app.routes.optimization - INFO - Optimization completed successfully in 2.45s
```

View logs in the terminal where you started the API server.

---

## ⚙️ Configuration

### Environment Variables
```bash
# Optional configuration
PHARMA_LOG_LEVEL=INFO
PHARMA_API_HOST=0.0.0.0
PHARMA_API_PORT=8000
PHARMA_CORS_ORIGINS=*
```

### Uvicorn Settings
```bash
# Development (with reload)
uvicorn app.main:app --reload --log-level=info

# Production (no reload)
uvicorn app.main:app --workers=4 --log-level=warning
```

---

## 🤝 Integration Examples

### Frontend Integration (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/api/v1/optimization/run', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    facility_inventory: [...],
    consumption_history: [...],
    suppliers: [...]
  })
});

const result = await response.json();
console.log(result.action_plan);
```

### Python Client
```python
from app.schemas.optimization import FullOptimizationRequest, FullOptimizationResponse
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/api/v1/optimization/run',
        json=request.model_dump()
    )
    optimization_result = FullOptimizationResponse(**response.json())
```

---

## 📚 Useful Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **OpenAPI Specification**: https://spec.openapis.org/
- **Pydantic**: https://docs.pydantic.dev/
- **Uvicorn**: https://www.uvicorn.org/

---

## 📞 Support

For issues or questions:
1. Check the Swagger documentation at `/docs`
2. Review error messages and logs
3. Consult the main README.md for project context

---

**API Version:** 1.0.0  
**Last Updated:** February 19, 2026  
**Status:** Production-Ready ✅
