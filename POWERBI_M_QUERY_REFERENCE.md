# PowerBI M Query Reference - All Three Endpoints

## 📋 Quick Reference

Copy these M queries directly into PowerBI's Advanced Editor for each endpoint.

---

## 1️⃣ EXPIRATION RISK MANAGEMENT (3,000 records)

### Main Query: `expiration-risk?format=json`

```m
let
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json")),
    #"Converted to Table" = Table.FromRecords({Source}),
    #"Expanded data" = Table.ExpandListColumn(#"Converted to Table", "data"),
    #"Expanded data1" = Table.ExpandRecordColumn(#"Expanded data", "data", {
        "batch_id", 
        "medication_id", 
        "medication_name", 
        "facility_id", 
        "facility_name", 
        "quantity_on_hand", 
        "unit_cost", 
        "batch_value", 
        "expiry_date", 
        "days_until_expiry", 
        "risk_level", 
        "category", 
        "recommendation"
    }, {
        "data.batch_id", 
        "data.medication_id", 
        "data.medication_name", 
        "data.facility_id", 
        "data.facility_name", 
        "data.quantity_on_hand", 
        "data.unit_cost", 
        "data.batch_value", 
        "data.expiry_date", 
        "data.days_until_expiry", 
        "data.risk_level", 
        "data.category", 
        "data.recommendation"
    }),
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded data1",{
        {"data.batch_id", type text}, 
        {"data.medication_id", Int64.Type}, 
        {"data.medication_name", type text}, 
        {"data.facility_id", type text}, 
        {"data.facility_name", type text}, 
        {"data.quantity_on_hand", Int64.Type}, 
        {"data.unit_cost", type number}, 
        {"data.batch_value", type number}, 
        {"data.expiry_date", type date}, 
        {"data.days_until_expiry", Int64.Type}, 
        {"data.risk_level", type text}, 
        {"data.category", type text}, 
        {"data.recommendation", type text}
    }),
    #"Removed Other Columns" = Table.SelectColumns(#"Changed Type", {
        "data.batch_id", 
        "data.medication_id", 
        "data.medication_name", 
        "data.facility_id", 
        "data.facility_name", 
        "data.quantity_on_hand", 
        "data.unit_cost", 
        "data.batch_value", 
        "data.expiry_date", 
        "data.days_until_expiry", 
        "data.risk_level", 
        "data.category", 
        "data.recommendation"
    })
in
    #"Removed Other Columns"
```

### Column Mapping:
- `data.batch_id` → batch_id (text)
- `data.medication_id` → medication_id (number)
- `data.medication_name` → medication_name (text)
- `data.facility_id` → facility_id (text)
- `data.facility_name` → facility_name (text)
- `data.quantity_on_hand` → quantity_on_hand (number)
- `data.unit_cost` → unit_cost (decimal)
- `data.batch_value` → batch_value (decimal)
- `data.expiry_date` → expiry_date (date)
- `data.days_until_expiry` → days_until_expiry (number)
- `data.risk_level` → risk_level (text) [Values: CRITICAL, HIGH, MEDIUM, LOW]
- `data.category` → category (text)
- `data.recommendation` → recommendation (text) [Values: TRANSFER, MONITOR]

---

## 2️⃣ TRANSFER COORDINATION (500 records)

### Main Query: `transfer-coordination?format=json`

```m
let
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=json")),
    #"Converted to Table" = Table.FromRecords({Source}),
    #"Expanded data" = Table.ExpandListColumn(#"Converted to Table", "data"),
    #"Expanded data1" = Table.ExpandRecordColumn(#"Expanded data", "data", {
        "order_id",
        "from_facility",
        "from_facility_id",
        "to_facility",
        "to_facility_id",
        "medication_id",
        "medication_name",
        "quantity",
        "unit_cost",
        "transfer_cost_per_unit",
        "total_transfer_cost",
        "total_medication_value",
        "decision_type",
        "status",
        "compliance_status",
        "expected_delivery_date",
        "created_date",
        "rationale",
        "estimated_savings",
        "cost_benefit_score"
    }, {
        "data.order_id",
        "data.from_facility",
        "data.from_facility_id",
        "data.to_facility",
        "data.to_facility_id",
        "data.medication_id",
        "data.medication_name",
        "data.quantity",
        "data.unit_cost",
        "data.transfer_cost_per_unit",
        "data.total_transfer_cost",
        "data.total_medication_value",
        "data.decision_type",
        "data.status",
        "data.compliance_status",
        "data.expected_delivery_date",
        "data.created_date",
        "data.rationale",
        "data.estimated_savings",
        "data.cost_benefit_score"
    }),
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded data1",{
        {"data.order_id", type text},
        {"data.from_facility", type text},
        {"data.from_facility_id", type text},
        {"data.to_facility", type text},
        {"data.to_facility_id", type text},
        {"data.medication_id", Int64.Type},
        {"data.medication_name", type text},
        {"data.quantity", Int64.Type},
        {"data.unit_cost", type number},
        {"data.transfer_cost_per_unit", type number},
        {"data.total_transfer_cost", type number},
        {"data.total_medication_value", type number},
        {"data.decision_type", type text},
        {"data.status", type text},
        {"data.compliance_status", type text},
        {"data.expected_delivery_date", type date},
        {"data.created_date", type date},
        {"data.rationale", type text},
        {"data.estimated_savings", type number},
        {"data.cost_benefit_score", type number}
    }),
    #"Removed Other Columns" = Table.SelectColumns(#"Changed Type", {
        "data.order_id",
        "data.from_facility",
        "data.from_facility_id",
        "data.to_facility",
        "data.to_facility_id",
        "data.medication_id",
        "data.medication_name",
        "data.quantity",
        "data.unit_cost",
        "data.transfer_cost_per_unit",
        "data.total_transfer_cost",
        "data.total_medication_value",
        "data.decision_type",
        "data.status",
        "data.compliance_status",
        "data.expected_delivery_date",
        "data.created_date",
        "data.rationale",
        "data.estimated_savings",
        "data.cost_benefit_score"
    })
in
    #"Removed Other Columns"
```

### Column Mapping:
- `data.order_id` → order_id (text)
- `data.from_facility` → from_facility (text)
- `data.from_facility_id` → from_facility_id (text)
- `data.to_facility` → to_facility (text)
- `data.to_facility_id` → to_facility_id (text)
- `data.medication_id` → medication_id (number)
- `data.medication_name` → medication_name (text)
- `data.quantity` → quantity (number)
- `data.unit_cost` → unit_cost (decimal)
- `data.transfer_cost_per_unit` → transfer_cost_per_unit (decimal)
- `data.total_transfer_cost` → total_transfer_cost (decimal)
- `data.total_medication_value` → total_medication_value (decimal)
- `data.decision_type` → decision_type (text) [Always: TRANSFER]
- `data.status` → status (text) [Values: PENDING, READY, BLOCKED, COMPLETED]
- `data.compliance_status` → compliance_status (text) [Values: OK, WARNING, RISK]
- `data.expected_delivery_date` → expected_delivery_date (date)
- `data.created_date` → created_date (date)
- `data.rationale` → rationale (text)
- `data.estimated_savings` → estimated_savings (decimal)
- `data.cost_benefit_score` → cost_benefit_score (decimal) [0.0 - 1.0]

---

## 3️⃣ DEMAND FORECAST (4,500 records)

### Main Query: `demand-forecast?format=json`

```m
let
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=json")),
    #"Converted to Table" = Table.FromRecords({Source}),
    #"Expanded data" = Table.ExpandListColumn(#"Converted to Table", "data"),
    #"Expanded data1" = Table.ExpandRecordColumn(#"Expanded data", "data", {
        "medication_id",
        "medication_name",
        "category",
        "forecast_date",
        "current_inventory",
        "predicted_demand_7d",
        "predicted_demand_14d",
        "predicted_demand_30d",
        "forecast_confidence",
        "model_type",
        "model_accuracy_mape",
        "min_safe_stock",
        "max_stock",
        "suggested_action",
        "urgency",
        "risk_level",
        "anomalies_detected",
        "external_signals"
    }, {
        "data.medication_id",
        "data.medication_name",
        "data.category",
        "data.forecast_date",
        "data.current_inventory",
        "data.predicted_demand_7d",
        "data.predicted_demand_14d",
        "data.predicted_demand_30d",
        "data.forecast_confidence",
        "data.model_type",
        "data.model_accuracy_mape",
        "data.min_safe_stock",
        "data.max_stock",
        "data.suggested_action",
        "data.urgency",
        "data.risk_level",
        "data.anomalies_detected",
        "data.external_signals"
    }),
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded data1",{
        {"data.medication_id", Int64.Type},
        {"data.medication_name", type text},
        {"data.category", type text},
        {"data.forecast_date", type datetime},
        {"data.current_inventory", Int64.Type},
        {"data.predicted_demand_7d", Int64.Type},
        {"data.predicted_demand_14d", Int64.Type},
        {"data.predicted_demand_30d", Int64.Type},
        {"data.forecast_confidence", type number},
        {"data.model_type", type text},
        {"data.model_accuracy_mape", type number},
        {"data.min_safe_stock", Int64.Type},
        {"data.max_stock", Int64.Type},
        {"data.suggested_action", type text},
        {"data.urgency", type text},
        {"data.risk_level", type text},
        {"data.anomalies_detected", Int64.Type},
        {"data.external_signals", type text}
    }),
    #"Removed Other Columns" = Table.SelectColumns(#"Changed Type", {
        "data.medication_id",
        "data.medication_name",
        "data.category",
        "data.forecast_date",
        "data.current_inventory",
        "data.predicted_demand_7d",
        "data.predicted_demand_14d",
        "data.predicted_demand_30d",
        "data.forecast_confidence",
        "data.model_type",
        "data.model_accuracy_mape",
        "data.min_safe_stock",
        "data.max_stock",
        "data.suggested_action",
        "data.urgency",
        "data.risk_level",
        "data.anomalies_detected",
        "data.external_signals"
    })
in
    #"Removed Other Columns"
```

### Column Mapping:
- `data.medication_id` → medication_id (number)
- `data.medication_name` → medication_name (text)
- `data.category` → category (text)
- `data.forecast_date` → forecast_date (datetime)
- `data.current_inventory` → current_inventory (number)
- `data.predicted_demand_7d` → predicted_demand_7d (number)
- `data.predicted_demand_14d` → predicted_demand_14d (number)
- `data.predicted_demand_30d` → predicted_demand_30d (number)
- `data.forecast_confidence` → forecast_confidence (decimal) [0.0 - 1.0]
- `data.model_type` → model_type (text) [Values: PROPHET, ARIMA, EXPONENTIAL]
- `data.model_accuracy_mape` → model_accuracy_mape (decimal) [Mean Absolute Percentage Error]
- `data.min_safe_stock` → min_safe_stock (number)
- `data.max_stock` → max_stock (number)
- `data.suggested_action` → suggested_action (text) [Values: MONITOR, ORDER, TRANSFER, REDUCE]
- `data.urgency` → urgency (text) [Values: LOW, MEDIUM, HIGH, CRITICAL]
- `data.risk_level` → risk_level (text) [Values: LOW, MEDIUM, HIGH]
- `data.anomalies_detected` → anomalies_detected (number)
- `data.external_signals` → external_signals (text)

---

## 🔗 Creating Relationships

Once you've loaded all three tables, create these relationships:

### Primary Keys Setup:
| Table | Primary Key |
|-------|------------|
| Expiration Risk | data.batch_id |
| Transfer Coordination | data.order_id |
| Demand Forecast | data.medication_id |

### Create Relationships:
1. **Expiration Risk → Demand Forecast**
   - From: data.medication_id (Expiration Risk)
   - To: data.medication_id (Demand Forecast)
   - Cardinality: Many-to-One (M:1)

2. **Transfer Coordination → Expiration Risk**
   - From: data.medication_id (Transfer Coordination)
   - To: data.medication_id (Expiration Risk)
   - Cardinality: Many-to-One (M:1)

3. **Transfer Coordination → Facilities** (if creating separate Facilities table)
   - From: data.from_facility_id (Transfer Coordination)
   - To: facility_id (Facilities)
   - Cardinality: Many-to-One (M:1)

---

## 💡 Tips for Success

### Tip 1: Rename Columns (Optional but Cleaner)
After transforming, you can rename the `data.` prefixed columns:
- Right-click column → Rename
- Change `data.batch_id` → `batch_id`
- Change `data.medication_name` → `medication_name`
- etc.

### Tip 2: Add a Refresh Date Column
```m
#"Added Refresh Date" = Table.AddColumn(#"Removed Other Columns", "Refresh Date", each DateTime.LocalNow()),
```

### Tip 3: Cache Data Locally
For better performance, export the queries to JSON files and load locally instead of hitting the API every refresh:
```m
Source = Json.Document(File.Contents("C:\PowerBI\expiration_risk.json")),
```

### Tip 4: Add Error Handling
```m
#"Added Error Handling" = Table.AddColumn(#"Removed Other Columns", "Data Quality", 
    each if [data.batch_id] = null then "Missing Batch ID" else "OK")
```

---

## 📊 Quick Transformation Path

For each endpoint:
1. **Get Data** → **Web** → Paste URL
2. **Advanced Editor** → Paste M query from above
3. **Load** → Confirm data appears
4. **Rename columns** (optional, for cleaner names)
5. **Create Relationships** (after all 3 loaded)
6. **Build visuals**

---

## ✅ Validation Checklist

After loading all three tables:

- [ ] Expiration Risk: 3,000+ rows
- [ ] Transfer Coordination: 500+ rows
- [ ] Demand Forecast: 4,500+ rows
- [ ] No error rows in any table
- [ ] All columns have correct data types
- [ ] Relationships created (3 total)
- [ ] Date columns show as dates (not text)
- [ ] Number columns show as numbers (not text)

---

## 🚀 You're Ready!

Once all three queries are loaded and relationships are created, you have the complete data model ready for dashboard building!

**Next Step:** Follow [POWERBI_EXACT_LAYOUT_GUIDE.md](POWERBI_EXACT_LAYOUT_GUIDE.md) to build your three dashboards.
