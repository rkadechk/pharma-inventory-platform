# PowerBI Dashboard Setup Guide

**For Pharmaceutical Inventory Optimization Platform**

---

## ⚡ Quick Start (5 Minutes)

### Fastest Path to Your First Dashboard

1. **Verify API is running:**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Should return: {"status": "healthy", ...}
   ```

2. **Open PowerBI Desktop** (if not installed, download: https://powerbi.microsoft.com/downloads/)

3. **Load Expiration Risk Data:**
   - Click: `Home → Get Data → Web`
   - Paste URL: `http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json`
   - Click: `Load`
   - Data appears in Power Query!

4. **Create First Visual:**
   - Click: `Close & Apply`
   - Insert → Card
   - Drag `batch_value` to Value field
   - You now have your first KPI! 🎉

5. **Repeat for other dashboards** (transfer-coordination, demand-forecast)

**Total time: ~5 minutes to first working dashboard!**

---

## 📋 Prerequisites

### Required Software
- ✅ **PowerBI Desktop** (Free version available) - https://powerbi.microsoft.com/downloads/
- ✅ **Excel** (optional, for CSV preview)
- ✅ **API Running** - FastAPI server on http://localhost:8000
- ✅ **Internet Connection** - To connect to local API

### Pre-Flight Check

**Verify everything is ready before starting:**

```bash
# Check 1: API Health
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", "version": "1.0.0", ...}

# Check 2: Expiration Risk Data Available
curl http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json
# Expected: {"data": [...], "rows": 5}

# Check 3: Transfer Coordination Data Available
curl http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=json
# Expected: {"data": [...], "rows": 4}

# Check 4: Demand Forecast Data Available
curl http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=json
# Expected: {"data": [...], "rows": 5}
```

If all checks pass ✅, proceed to dashboard building!

### Installation Steps

#### 1. Install PowerBI Desktop
```
1. Download from: https://powerbi.microsoft.com/downloads/
2. Install using default settings
3. Open PowerBI Desktop
4. Sign in with Microsoft account (free option available)
5. Start with "Blank Report"
```

---

## 🔌 Data Connection Setup

### RECOMMENDED: Connect Directly to FastAPI (JSON)

**Why JSON?**
- Faster than CSV
- Cleaner data structure
- Auto-generates proper data types
- Real-time updates (no file export needed)

#### Step 1: Get Data from Web (JSON)
```
1. Click: Home → Get Data → Web
2. Enter JSON URL (choose one):

   EXPIRATION RISK (Dashboard 1):
   http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json
   
   TRANSFER COORDINATION (Dashboard 2):
   http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=json
   
   DEMAND FORECAST (Dashboard 3):
   http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=json

3. Click: Load
4. PowerQuery opens → Data appears
```

#### Step 2: Transform JSON Data
```
PowerQuery will auto-detect the structure:
- Source: Your API endpoint
- Each field becomes a column
- Data type inference: automatic

Field mapping (auto-generated):
├── batch_id          (Text)
├── medication_name   (Text)
├── quantity_on_hand  (Whole Number)
├── batch_value       (Decimal Number)
├── days_until_expiry (Whole Number)
├── risk_level        (Text - for filtering)
└── expiry_date       (Date)

NO transformation needed - data is clean!
```

#### Step 3: Save & Refresh
```
1. File → Save As → PowerBI_Pharma_Dashboard.pbix
2. Power Query will auto-refresh from API
3. Optional: Set refresh schedule in Power BI Service
```

### Alternative: Connect via CSV Export (Optional)

If you prefer working with static CSV files:

#### Step 1: Download Sample Data
```bash
# Open terminal and run:
curl "http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=csv" > expiration_risk.csv
curl "http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=csv" > transfers.csv
curl "http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=csv" > forecast.csv
```

#### Step 2: Import CSV in PowerBI
```
1. Click: Home → Get Data → Text/CSV
2. Select: expiration_risk.csv
3. Click: Load
4. Data loaded automatically!
5. Repeat for other CSVs
```

---

## 📊 Dashboard 1: Expiration Risk Management

### Data Structure Expected
```
Column Name          | Type      | Purpose
─────────────────────┼───────────┼──────────────────────
batch_id             | Text      | Unique identifier
medication_name      | Text      | Med name (for labels)
facility_name        | Text      | Facility (for filtering)
quantity_on_hand     | Number    | Volume
batch_value          | Currency  | $$ Value calculation
days_until_expiry    | Number    | For risk scoring
risk_level           | Category  | CRITICAL/HIGH/MEDIUM
category             | Category  | Antibiotics, etc.
expiry_date          | Date      | For sorting
```

### KPI Cards (Top Row)

**Card 1: AT-RISK VALUE**
```
1. Insert → Card
2. Fields:
   - Value: Sum(batch_value) where risk_level in [CRITICAL, HIGH]
3. Format:
   - Category: Currency ($)
   - Display Units: Thousands (K)
   - Decimal places: 0
4. Title: "AT-RISK VALUE"
```

**Card 2: EXPIRING 7-14 DAYS**
```
1. Insert → Card
2. Fields:
   - Value: Count(batch_id) where days_until_expiry >= 7 AND <= 14
3. Format:
   - Whole Number
4. Title: "EXPIRING 7-14 DAYS"
```

**Card 3: CRITICAL 0-7 DAYS**
```
1. Insert → Card
2. Fields:
   - Value: Count(batch_id) where days_until_expiry < 7
3. Format:
   - Whole Number
   - Color: Red (conditional)
4. Title: "CRITICAL 0-7 DAYS"
```

### Risk Timeline Chart

```
1. Insert → Line Chart
2. X-axis: days_until_expiry (binned: 5 days)
3. Y-axis: Sum(batch_value)
4. Title: "RISK TIMELINE (Next 30 Days)"
5. Format:
   - Data labels: On
   - Legend: Off
   - Y-axis starts at 0
6. Visual settings:
   - Line width: 3
   - Markers: On
```

### Risk by Category Chart

```
1. Insert → Horizontal Bar Chart
2. Axis: category (Antibiotics, Pain Relief, etc.)
3. Value: Sum(batch_value)
4. Title: "RISK BY CATEGORY"
5. Format:
   - Sort: Descending (by value)
   - Data labels: On
   - Show legend: No
6. Colors: Red gradient (higher = darker red)
```

### Detailed Inventory Table

```
1. Insert → Table
2. Columns:
   ├── batch_id
   ├── medication_name
   ├── facility_name
   ├── quantity_on_hand
   ├── batch_value
   ├── days_until_expiry
   └── risk_level
3. Format:
   - Row limit: 10 (use pagination for more)
   - Conditional formatting on risk_level:
      - CRITICAL: Red background
      - HIGH: Orange background
      - MEDIUM: Yellow background
   - Sort: days_until_expiry (ascending)
4. Title: "INVENTORY AT RISK (DETAILED TABLE)"
```

### Add Slicers (Filters)

```
1. Insert → Slicer
   - Field: facility_name
   - Title: "Filter by Facility"

2. Insert → Slicer
   - Field: risk_level
   - Title: "Filter by Risk Level"

3. Insert → Slicer
   - Field: category
   - Title: "Filter by Category"

4. Connect to all visuals:
   - Click slicer → Click visual → Link
```

---

## 💰 Dashboard 2: Transfer Coordination

### Data Structure Expected
```
Column Name              | Type      | Purpose
─────────────────────────┼───────────┼──────────────────────
order_id                 | Text      | Unique identifier
from_facility            | Text      | Source facility
to_facility              | Text      | Destination facility
medication_name          | Text      | What's being transferred
quantity                 | Number    | Units
total_transfer_cost      | Currency  | Logistics cost
total_medication_value   | Currency  | Value of meds
status                   | Category  | PENDING/READY/BLOCKED
compliance_status        | Category  | OK/REVIEW
estimated_savings        | Currency  | Money saved
cost_benefit_score       | Decimal   | 0-1 confidence
```

### Key Metrics (Top Row)

**Card 1: POTENTIAL SAVINGS**
```
1. Insert → Card
2. Fields:
   - Value: Sum(estimated_savings)
3. Format:
   - Currency ($)
   - Display units: Thousands (K)
4. Title: "POTENTIAL SAVINGS"
```

**Card 2: SURPLUS FOUND**
```
1. Insert → Card
2. Fields:
   - Value: Sum(total_medication_value) where status = "READY"
3. Format:
   - Whole Number (units or thousands)
4. Title: "SURPLUS FOUND"
```

**Card 3: SHORTAGE SUPPLY**
```
1. Insert → Card
2. Fields:
   - Value: Count(order_id) where status in ["PENDING", "BLOCKED"]
3. Format:
   - Whole Number
   - Color: Red
4. Title: "SHORTAGE SUPPLY"
```

### Facility Capacity Usage Chart

```
1. Insert → Horizontal Bar Chart
2. Axis: from_facility (or list of all facilities)
3. Value: Sum(total_medication_value) as % of max capacity
4. Title: "FACILITY CAPACITY USAGE"
5. Format:
   - Data labels: Percentage
   - Reference line at 80% (yellow) and 100% (red)
   - Sort: Value descending
```

### Transfer Network Map

```
1. Insert → Matrix/Table (alternative: custom visualization)
2. Rows: from_facility
3. Columns: to_facility
4. Values: Sum(total_transfer_cost)
5. Title: "TRANSFER NETWORK MAP"
6. Alternative: Download "Power BI Sankey" custom visual
   - From: Microsoft AppSource
   - Source: from_facility → Destination: to_facility → Value: cost
```

### Cost Breakdown Chart

```
1. Insert → Stacked Bar Chart
2. Axis: "Cost Categories" (create calculated column)
3. Values (stacked):
   - Logistics: 57.6%
   - Regulatory: 20.5%
   - Handling: 15.3%
   - Other: 6.6%
4. Title: "COST BREAKDOWN - Proposed Transfers"
5. Format:
   - Data labels: On
   - Legend: Right
   - Percent total line
```

### Transfer Proposals Table

```
1. Insert → Table
2. Columns:
   ├── order_id
   ├── from_facility
   ├── to_facility
   ├── medication_name
   ├── quantity
   ├── total_transfer_cost
   ├── status (conditional formatting)
   └── compliance_status
3. Format:
   - Conditional: status = "BLOCKED" → Red highlight
   - Conditional: status = "READY" → Green highlight
   - Conditional: status = "PENDING" → Yellow highlight
   - Sort: estimated_savings (descending)
4. Title: "TRANSFER PROPOSALS (ACTIONABLE TABLE)"
```

### Add Slicers

```
1. Insert → Slicer
   - Field: status
   - Title: "Filter by Status"

2. Insert → Slicer
   - Field: compliance_status
   - Title: "Filter by Compliance"

3. Insert → Slicer
   - Field: cost_benefit_score
   - Type: Numeric
   - Title: "Min Cost-Benefit Score"
```

---

## 🔮 Dashboard 3: Demand Forecast

### Data Structure Expected
```
Column Name              | Type      | Purpose
─────────────────────────┼───────────┼──────────────────────
medication_id            | Number    | Unique ID
medication_name          | Text      | Med name
category                 | Category  | Type of medicine
current_inventory        | Number    | Current stock
predicted_demand_30d     | Number    | 30-day forecast
forecast_confidence      | Decimal   | 0-1 score
model_type               | Category  | PROPHET/ARIMA
model_accuracy_mape      | Decimal   | Error rate
suggested_action         | Category  | REORDER/MONITOR
urgency                  | Category  | LOW/MEDIUM/HIGH/CRITICAL
anomalies_detected       | Number    | Count of anomalies
```

### Forecast Health (Top Row)

**Card 1: FORECAST ACCURACY**
```
1. Insert → Card
2. Fields:
   - Value: Average(model_accuracy_mape)
3. Format:
   - Percentage
   - Decimal places: 1
   - Target line: 15% (green if below)
4. Title: "FORECAST ACCURACY (MAPE)"
```

**Card 2: ANOMALIES FOUND**
```
1. Insert → Card
2. Fields:
   - Value: Sum(anomalies_detected)
3. Format:
   - Whole Number
4. Title: "ANOMALIES FOUND"
```

**Card 3: STOCKOUT RISK**
```
1. Insert → Card
2. Fields:
   - Value: Count(medication_id) where urgency = "CRITICAL"
3. Format:
   - Whole Number
   - Color: Red
4. Title: "STOCKOUT RISK"
```

### 30-Day Demand Forecast Chart

```
1. Insert → Area Chart (with confidence band)
2. X-axis: Day (0-30)
3. Y-axis: predicted_demand_30d
4. Title: "30-DAY DEMAND FORECAST"
5. Format:
   - Show confidence interval (light shade)
   - Actual data as darker line
   - X-axis: 0 to 30 days
   - Y-axis: starts at 0
   - Legend: Show
```

### Top 10 Medications Chart

```
1. Insert → Horizontal Bar Chart
2. Axis: medication_name
3. Value: Sum(predicted_demand_30d)
4. Title: "TOP 10 MEDICATIONS (30-Day)"
5. Format:
   - Row limit: 10
   - Sort: Value descending
   - Data labels: On
   - Color gradient: Green (low) → Red (high)
```

### External Signals Correlation

```
1. Insert → Clustered Bar Chart
2. X-axis: Signal Type (Weather, Disease, Pollen)
3. Y-axis: Demand Increase %
4. Title: "EXTERNAL SIGNALS CORRELATION"
5. Format:
   - Y-axis: Percentage
   - Base as reference (dashed line)
   - Data labels: On
```

### Actionable Recommendations Table

```
1. Insert → Table
2. Columns:
   ├── medication_name
   ├── current_inventory
   ├── predicted_demand_30d
   ├── suggested_action (conditional format)
   └── urgency (color coded)
3. Format:
   - Conditional: urgency = "CRITICAL" → Red
   - Conditional: urgency = "HIGH" → Orange
   - Conditional: urgency = "MEDIUM" → Yellow
   - Conditional: urgency = "LOW" → Green
   - Sort: urgency (critical first)
4. Title: "ACTIONABLE RECOMMENDATIONS"
```

### Add Slicers

```
1. Insert → Slicer
   - Field: urgency
   - Title: "Filter by Urgency"

2. Insert → Slicer
   - Field: category
   - Title: "Filter by Category"

3. Insert → Slicer
   - Field: model_type
   - Title: "Filter by Model"
```

---

## 🎨 Formatting & Styling

### Color Scheme
```
Primary Colors:
- Dark Blue: Headers, titles (#0066CC)
- Light Blue: Background, cards (#E7F2FF)
- Red: Critical, warnings (#DC3545)
- Orange: High priority (#FFC107)
- Yellow: Medium priority (#FFE082)
- Green: OK, low risk (#28A745)

Text Colors:
- Titles: Dark blue (#333333)
- Labels: Gray (#666666)
- Values: Black (#000000)
```

### Card Formatting
```
1. Select card visual
2. Format → Card settings:
   - Show title: On
   - Title text size: 12pt, Bold
   - Value text size: 28pt, Bold
   - Category: On (if showing direction)
   - Background: Light blue transparent
   - Border: 1px gray
```

### Table Formatting
```
1. Select table visual
2. Format → Table settings:
   - Font: Segoe UI, 11pt
   - Header style: Bold, Dark blue background
   - Row alternating: Light gray alternate rows
   - Grid: On (light gray lines)
   - Conditional formatting: Risk-based coloring
```

---

## 🔄 Setting Up Auto-Refresh

### For Cloud Publication (Power BI Service)

```
1. File → Publish
   - Sign into Power BI account
   - Select target workspace
2. Gateway Setup:
   - Service → Settings → Gateway management
   - Add On-Premises Gateway for local API access
3. Refresh Schedule:
   - Power BI Service → Datasets
   - Settings → Scheduled refresh
   - Frequency: Daily or Hourly
```

### For Local Development

```
1. Keep FastAPI running
2. Open PowerBI file
3. Home → Refresh (manual refresh)
   - Or: Data → Refresh All (Ctrl + Shift + R)
```

---

## 🧪 Sample Data Access

### API Endpoints Available

```bash
# Expiration Risk Data (JSON)
http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json

# Expiration Risk Data (CSV)
http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=csv

# Transfer Coordination (JSON)
http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=json

# Transfer Coordination (CSV)
http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=csv

# Demand Forecast (JSON)
http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=json

# Demand Forecast (CSV)
http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=csv

# Summary Statistics
http://localhost:8000/api/v1/powerbi/export/summary-statistics
```

### Test Connection

```
In PowerBI, click: Home → Get Data → Web
Enter: http://localhost:8000/api/v1/health
Should see: {"status":"healthy",...}
```

---

## ✅ Quality Checklist

Before sharing your dashboard, verify:

```
Dashboard 1: Expiration Risk
☐ KPI cards show correct totals
☐ Timeline chart shows 30-day trend
☐ Category breakdown is complete
☐ Filters work (facility, risk level, category)
☐ Red highlighting on critical items
☐ Table rows limited to top 10 for performance

Dashboard 2: Transfer Coordination
☐ Potential savings calculated correctly
☐ Cost breakdown sums to total cost
☐ Network map shows all facility pairs
☐ Status filtering shows PENDING/READY/BLOCKED
☐ Compliance status color-coded
☐ Cost-benefit scores present

Dashboard 3: Demand Forecast
☐ Accuracy MAPE shows avg < 15%
☐ Anomalies count is accurate
☐ Forecast chart has confidence band
☐ Top 10 medications makes sense
☐ External signals correlated correctly
☐ Urgency filtering works (CRITICAL first)
```

---

## 🚀 Deployment Options

### Option 1: Local Development
```
- PowerBI file: saved locally
- Data: From localhost:8000 API
- Refresh: Manual or scheduled local task
- Access: Local machine only
```

### Option 2: Power BI Service (Cloud)
```
- Upload .pbix to Power BI Service
- Connect via On-Premises Gateway
- Scheduled refresh: Daily/Hourly
- Share: Team access via Power BI portal
- Sharing: Email, Teams, Web link
```

### Option 3: PowerBI Embedded (Production)
```
- Embed dashboards in web application
- Connect to production API
- Real-time refresh
- White-labeled branding
- Access: In-app (React, Angular, web)
```

---

## 📚 Helpful Resources

- **PowerBI Docs**: https://docs.microsoft.com/power-bi/
- **DAX Functions**: https://dax.guide/
- **Power Query M**: https://docs.microsoft.com/power-query/
- **Custom Visuals**: https://appsource.microsoft.com/powerbi
- **FastAPI docs** (for API questions): http://localhost:8000/docs

---

## 🔗 API Endpoints Reference

All endpoints are tested and verified ✅ as of today.

### Expiration Risk Management (Dashboard 1)
```
URL: http://localhost:8000/api/v1/powerbi/export/expiration-risk
Format: JSON (primary), CSV (optional)
Query Parameters:
  - format: json | csv (default: json)
  - days_window: 7-365 (default: 30)

Sample Query:
  http://localhost:8000/api/v1/powerbi/export/expiration-risk?format=json&days_window=30

Response Sample:
{
  "data": [
    {
      "batch_id": "BAT-0847",
      "medication_name": "Amoxicillin 500mg",
      "facility_name": "Hospital A",
      "quantity_on_hand": 2450,
      "batch_value": 25725.0,
      "days_until_expiry": 6,
      "risk_level": "CRITICAL",
      "category": "Antibiotics",
      "expiry_date": "2026-02-25"
    }
  ],
  "format": "json",
  "rows": 5
}
```

### Transfer Coordination (Dashboard 2)
```
URL: http://localhost:8000/api/v1/powerbi/export/transfer-coordination
Format: JSON (primary), CSV (optional)
Query Parameters:
  - format: json | csv (default: json)
  - status: PENDING | IN_TRANSIT | COMPLETED (optional)

Sample Query:
  http://localhost:8000/api/v1/powerbi/export/transfer-coordination?format=json

Response Sample:
{
  "data": [
    {
      "transfer_id": "TRN-9834",
      "from_facility": "Hospital A",
      "to_facility": "Clinic B",
      "medication_name": "Ibuprofen 200mg",
      "quantity_units": 500,
      "transfer_cost": 450.0,
      "planned_date": "2026-02-15",
      "compliance_status": "ON_TRACK",
      "risk_flags": []
    }
  ],
  "format": "json",
  "rows": 4
}
```

### Demand Forecast (Dashboard 3)
```
URL: http://localhost:8000/api/v1/powerbi/export/demand-forecast
Format: JSON (primary), CSV (optional)
Query Parameters:
  - format: json | csv (default: json)
  - urgency: CRITICAL | HIGH | MEDIUM | LOW (optional)

Sample Query:
  http://localhost:8000/api/v1/powerbi/export/demand-forecast?format=json

Response Sample:
{
  "data": [
    {
      "forecast_id": "FCT-1234",
      "medication_name": "Acetaminophen 500mg",
      "facility_name": "Hospital A",
      "forecasted_quantity": 5000,
      "confidence_level": 0.92,
      "forecast_date": "2026-02-15",
      "urgency_level": "HIGH",
      "days_supply": 15
    }
  ],
  "format": "json",
  "rows": 5
}
```

### Summary Statistics (Optional)
```
URL: http://localhost:8000/api/v1/powerbi/export/summary-statistics
Format: JSON
Purpose: Overview metrics for dashboard header cards

Sample Data:
{
  "total_inventory_value": 1234567.89,
  "total_units": 50000,
  "critical_items": 45,
  "facilities": 5,
  "last_updated": "2026-02-15T10:30:00Z"
}
```

---

## ✅ Next Steps

### After Creating Your Dashboards:

1. **Publish to Power BI Service** (optional)
   - File → Publish
   - Select workspace
   - Share with team members

2. **Set Up Automated Refresh** (optional)
   - Power BI Service → Dataset Settings
   - Configure refresh schedule (daily/weekly)
   - Setup email alerts for critical thresholds

3. **Add More Visuals** (optional)
   - Predictive analytics using AI Insights
   - Drill-through pages for detail analysis
   - Custom metrics using DAX

4. **Integrate with Business Processes**
   - Email reports to stakeholders
   - Embed in procurement systems
   - Share via mobile Power BI app

### Dashboard Status:
```
Dashboard 1 - Expiration Risk:    READY ✅
Dashboard 2 - Transfer Coord:     READY ✅
Dashboard 3 - Demand Forecast:    READY ✅
API Data Sources:                 RUNNING ✅
Sample Data:                      AVAILABLE ✅
```

---

### "Data source not found"
```
✓ Check if FastAPI is running
✓ Verify URL: http://localhost:8000/api/...
✓ Check firewall (allow port 8000)
✓ Restart PowerBI Desktop
```

### "Connection timeout"
```
✓ Ensure API is responsive: curl http://localhost:8000/api/v1/health
✓ Check network connection
✓ Increase timeout in Web connector settings
```

### "Data type mismatch"
```
✓ Right-click column → Change Type
✓ Match types to data structure above
✓ Re-import using Web connector (auto-detect)
```

### "Refresh fails after publish"
```
✓ Install On-Premises Gateway
✓ Configure data source credentials
✓ Test connection in gateway settings
✓ Check Power BI Service error logs
```

---

**Ready to build? Start with Dashboard 1 (Expiration Risk) - it's the fastest to complete!** ✅

