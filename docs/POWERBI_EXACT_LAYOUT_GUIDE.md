# PowerBI Exact Dashboard Layout Guide
**Replicate UI/UX Design Exactly in PowerBI Desktop**

---

## 📐 Layout Overview

Each dashboard uses a **4-section layout**:

```
┌─────────────────────────────────────────────────────┐
│  [FILTERS: Date Range, Facility, etc.]              │
├─────────────────────────────────────────────────────┤
│  [KPI CARD 1]  [KPI CARD 2]  [KPI CARD 3]          │  ← Row 1: 3 cards
├─────────────────────────────────────────────────────┤
│  [CHART/VISUAL 1]        [CHART/VISUAL 2]          │  ← Row 2: 2 columns
├─────────────────────────────────────────────────────┤
│  [LARGE TABLE / VISUALIZATIONS]                     │  ← Row 3: Full width
├─────────────────────────────────────────────────────┤
│  [INFO BOX - Agent Recommendations]                 │  ← Row 4: Text/Info
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Dashboard 1: Expiration Risk Management - EXACT LAYOUT

### Step 1: Set Up Canvas & Filters

1. **Create 3 Slicers at top (filter row):**
   - Slicer 1: **Date Range** (for filtering by expiry date window)
     - Insert → Slicer
     - Field: `expiry_date`
     - Position: Top-left corner
   
   - Slicer 2: **Facility** (dropdown to filter by facility)
     - Insert → Slicer
     - Field: `facility_name`
     - Position: Top-center
   
   - Slicer 3: **Category** (optional, for filtering medication type)
     - Insert → Slicer
     - Field: `category`
     - Position: Top-right

2. **Format slicers:**
   - Style: Vertical or Dropdown
   - Background: Light gray (#F5F5F5)
   - Border: 1px gray

---

### Step 2: Row 1 - Three KPI Cards (Critical Metrics)

**Layout: Place 3 cards side-by-side across the page**

#### Card 1: AT-RISK VALUE
```
Position: Left side, below filters
Size: 1/3 width

Data:
- Value: Sum(batch_value) where risk_level in ["CRITICAL", "HIGH"]
- Title: "AT-RISK VALUE"
- Subtitle: Show trend (e.g., "↑ +$120K vs week")

Formatting:
1. Click card → Format panel
2. Card settings:
   - Title text: 14pt, Bold, Dark blue
   - Value text: 32pt, Bold, Black
   - Category label: Show (for trend direction)
3. Background: Light red tint (#FFE6E6)
4. Border: 2px red (#DC3545)
```

#### Card 2: EXPIRING 7-14 DAYS
```
Position: Center, below filters (middle 1/3)
Size: 1/3 width

Data:
- Value: Count of batch_id where days_until_expiry between 7 and 14
- Title: "EXPIRING 7-14 DAYS"
- Subtitle: Show trend

Formatting:
1. Similar to Card 1
2. Background: Light orange tint (#FFF3E0)
3. Border: 2px orange (#FFC107)
```

#### Card 3: CRITICAL 0-7 DAYS
```
Position: Right side, below filters
Size: 1/3 width

Data:
- Value: Count of batch_id where days_until_expiry < 7
- Title: "CRITICAL 0-7 DAYS"
- Subtitle: Show trend

Formatting:
1. Similar cards above
2. Background: Bright red (#FFE6E6)
3. Border: 2px red (#DC3545)
4. Value text color: RED (#DC3545)
```

---

### Step 3: Row 2 - Two Visualizations (Middle Row)

#### Left Visual: Risk Timeline Chart
```
Position: Left side, below KPI cards
Size: 50% width (half the dashboard)

Chart Type: Line Chart (with trend)

Setup:
1. Insert → Line Chart
2. Legend (X axis): days_until_expiry (group by 5-day bins)
   - Right-click axis → Bin → Set bin size to 5
3. Value (Y axis): Sum(batch_value)
4. Format:
   - Title: "RISK TIMELINE (Next 30 Days)"
   - Title text: 14pt, Bold
   - Line width: 3px
   - Line color: Red (#DC3545)
   - Show markers: ON
   - Data labels: ON (show values)
   - Y-axis starts at $0
   - Legend: OFF
   - Grid: Light gray

Visual appearance:
Should show a descending trend line from left to right
(as batches expire, value decreases)
```

#### Right Visual: Risk by Category Chart
```
Position: Right side, below KPI cards
Size: 50% width

Chart Type: Horizontal Bar Chart

Setup:
1. Insert → Horizontal Bar Chart
2. Axis: category (Antibiotics, Pain Relief, etc.)
3. Value: Sum(batch_value)
4. Format:
   - Title: "RISK BY CATEGORY"
   - Title text: 14pt, Bold
   - Sort: Value descending (highest risk first)
   - Data labels: ON (show values in bar)
   - Legend: OFF
   - Colors: Red gradient (darker = higher value)
      - Use Format → Data colors
      - Gradient: Light red → Dark red

Visual appearance:
Horizontal bars, longest on top, decreasing downward
Each bar labeled with category name
```

---

### Step 4: Row 3 - Detailed Inventory Table (Full Width)

```
Position: Below both charts, full width
Size: 100% width

Chart Type: Table

Setup:
1. Insert → Table

2. Select columns (in order):
   ├── batch_id
   ├── medication_name
   ├── facility_name
   ├── quantity_on_hand
   ├── batch_value
   ├── days_until_expiry
   └── risk_level

3. Format:
   - Title: "INVENTORY AT RISK (DETAILED TABLE)"
   - Title text: 14pt, Bold
   - Font: Segoe UI, 11pt
   - Row limit: Show 10 rows (enable pagination)
   - Column headers: Bold, Dark blue background (#0066CC), White text

4. Conditional Formatting (on risk_level column):
   - CRITICAL:   Red background (#FFE6E6)
   - HIGH:       Orange background (#FFF3E0)
   - MEDIUM:     Yellow background (#FFFDE7)

5. Sorting:
   - Primary sort: days_until_expiry (Ascending)
   - This puts CRITICAL items at top

Visual appearance:
Clean table with 5-7 rows visible
Red rows at top (critical items)
Orange/yellow rows below
Pagination controls at bottom
```

---

### Step 5: Row 4 - Agent Recommendations (Optional Info Box)

```
Position: Bottom of dashboard, full width
Size: 100% width

Method: Add a Text Box

1. Insert → Text Box
2. Content (example):
   "ℹ️ AGENT INSIGHT: Expiration Manager Agent recommends 
    transferring Amoxicillin batch BAT-0847 to Clinic X 
    (high demand) or marking for disposal to prevent waste."
3. Format:
   - Background: Light blue (#E7F2FF)
   - Border: 1px gray
   - Text color: Dark blue (#0066CC)
   - Padding: 10px
```

---

## 💰 Dashboard 2: Transfer Coordination - EXACT LAYOUT

### Step 1: Filters (Top Row)

Same as Dashboard 1:
- Date Range Slicer
- Facility Slicer  
- Status Slicer (PENDING, IN_TRANSIT, COMPLETED)

---

### Step 2: Row 1 - Three KPI Cards

#### Card 1: POTENTIAL SAVINGS
```
Data: Sum(estimated_savings)
Title: "POTENTIAL SAVINGS"
Background: Light green (#E8F5E9)
Border: 2px green (#28A745)
Value text: 32pt, Bold, Green (#28A745)
```

#### Card 2: SURPLUS FOUND
```
Data: Sum(total_medication_value) where status = "READY"
Title: "SURPLUS FOUND"
Background: Light cyan (#E0F2F1)
Border: 2px teal (#17A2B8)
Value text: 32pt, Bold
```

#### Card 3: SHORTAGE SUPPLY
```
Data: Count(order_id) where status in ["PENDING", "BLOCKED"]
Title: "SHORTAGE SUPPLY"
Background: Light red (#FFE6E6)
Border: 2px red (#DC3545)
Value text: 32pt, Bold, Red
```

---

### Step 3: Row 2 - Two Visualizations

#### Left Visual: Facility Capacity Usage
```
Chart Type: Horizontal Bar Chart

Data:
- Axis: from_facility (list of facilities)
- Value: Sum(total_medication_value) as % of capacity

Format:
- Title: "FACILITY CAPACITY USAGE"
- Add reference lines:
  * 80% = Yellow dashed line (warning)
  * 100% = Red dashed line (full)
- Data labels: Show percentage
- Colors: Green (<60%) → Yellow (60-80%) → Red (>80%)
- Sort: Descending (full facilities at top)

Visual notes:
- Hospital G should be at ~91% (near limit) - show in RED
- Others below 87%
```

#### Right Visual: Transfer Network Map
```
Chart Type: Sankey Diagram (or matrix table as alternative)

For SANKEY (recommended):
1. Install "Power BI Sankey" from Microsoft AppSource:
   - File → Options → Marketplace → Search "Sankey"
   - Download & Install

2. Setup Sankey:
   - Source: from_facility
   - Destination: to_facility
   - Weight: Sum(transfer_cost)
   - Title: "TRANSFER NETWORK MAP"

Visual appearance:
- Left column: Source facilities (Hospital A, B, etc.)
- Right column: Destination facilities
- Flowing lines between facilities
- Line thickness = transfer cost
- Shows network of transfers

Alternative (if Sankey unavailable):
Use Matrix table:
- Rows: from_facility
- Columns: to_facility
- Values: Sum(transfer_cost)
- Format with conditional coloring
```

---

### Step 4: Row 3 - Cost Breakdown (Full Width)

```
Chart Type: Stacked Horizontal Bar Chart

Data:
- Create calculated column "Cost Category" with values:
  * Logistics (57.6% of total)
  * Regulatory/Compliance (20.5%)
  * Handling (15.3%)
  * Other (6.6%)

Setup:
1. Insert → Stacked Horizontal Bar Chart
2. Axis: "Cost Breakdown"
3. Value (stacked): Base/sum for each category
4. Format:
   - Title: "COST BREAKDOWN - Proposed Transfers"
   - Colors: 
     * Logistics: Blue
     * Regulatory: Orange
     * Handling: Yellow
     * Other: Green
   - Data labels: Show values AND percentages
   - Legend: Right side

Visual appearance:
One horizontal bar, segmented by cost type
Shows total $425,000 at end
Label: "Total Estimated Cost: $425,000 (Savings vs. waste)"
```

---

### Step 5: Row 4 - Transfer Proposals Table (Full Width)

```
Chart Type: Table

Columns (in order):
├── order_id (or transfer_id)
├── from_facility
├── to_facility
├── medication_name
├── quantity_units
├── total_transfer_cost
├── status
└── compliance_status

Format:
- Title: "TRANSFER PROPOSALS (ACTIONABLE TABLE)"
- Row limit: 10 rows
- Enable pagination
- Conditional formatting on status:
  * 🔴 BLOCKED: Dark red background
  * 🟡 PENDING: Yellow background
  * 🟢 READY: Light green background
- Conditional formatting on compliance_status:
  * ✅ OK: Green text
  * ⚠️ REVIEW: Orange/yellow highlight
- Sort: status (BLOCKED first), then by estimated_savings (desc)
```

---

### Step 6: Row 5 - Agent Insight Box (Optional)

```
Text box at bottom:
"ℹ️ AGENT INSIGHT: Transfer Coordinator Agent found 23 
 optimization opportunities worth $425K in savings. 
 Click "View Details" for compliance requirements."
```

---

## 🔮 Dashboard 3: Demand Forecast - EXACT LAYOUT

### Step 1: Filters (Top Row)

- Date Range Slicer
- Facility Slicer
- Urgency Slicer (CRITICAL, HIGH, MEDIUM, LOW)
- Optional: Model Type (PROPHET, ARIMA)

---

### Step 2: Row 1 - Three KPI Cards

#### Card 1: FORECAST ACCURACY
```
Data: Average(model_accuracy_mape)
Title: "FORECAST ACCURACY"
Subtitle: "(MAPE)"
Format as: Percentage (1 decimal place)

Conditional coloring:
- < 10%: Green (#28A745) - "Excellent"
- 10-15%: Blue (#0066CC) - "Good"
- 15-20%: Orange (#FFC107) - "Acceptable"
- > 20%: Red (#DC3545) - "Needs Improvement"

Background: Light blue (#E7F2FF)
Border: 2px blue (#0066CC)
Show status label: "✅ Excellent" or "⚠️ Needs Review"
```

#### Card 2: ANOMALIES FOUND
```
Data: Sum(anomalies_detected)
Title: "ANOMALIES FOUND"
Subtitle: Show trend (e.g., "↑ +8 vs week")

Background: Light orange (#FFF3E0)
Border: 2px orange (#FFC107)
Value text: 32pt, Bold
Add warning indicator if > 50
```

#### Card 3: STOCKOUT RISK
```
Data: Count(medication_id) where urgency = "CRITICAL"
Title: "STOCKOUT RISK"
Subtitle: "Immediate action needed"

Background: Light red (#FFE6E6)
Border: 2px red (#DC3545)
Value text: 32pt, Bold, Red
Add urgency icon: 🛑
```

---

### Step 3: Row 2 - Large Forecast Chart (Full Width)

```
Chart Type: Combo Chart (Line + Area with confidence band)

Data:
- X-axis: forecast_date (or day number, 0-30)
- Primary Y-axis: forecasted_quantity (actual demand as line)
- Secondary Y-axis: confidence_level (optional, as area)

Setup:
1. Insert → Combo Chart
2. Legend (X axis): forecast_date or Day (0, 1, 2...30)
3. Line values: Sum(forecasted_quantity) - Dark blue line
4. Area values: confidence_level - Light blue shaded area
5. Format:
   - Title: "30-DAY DEMAND FORECAST"
   - Title text: 14pt, Bold
   - X-axis label: "Days from Today"
   - Y-axis label: "Units"
   - Line width: 3px (dark blue)
   - Area opacity: 30% (light blue confidence band)
   - Data labels: ON (show values at key points)
   - Legend: Show (inline or right)
   - Grid: Light gray
   - Y-axis starts at 0

Visual appearance:
- Confidence band shown as light blue shaded area
- Actual/forecast line as darker blue on top
- Line shows peaks/valleys of demand patterns
- Should occupy ~40-50% of dashboard height
```

---

### Step 4: Row 3 - Two Visualizations (Side by Side)

#### Left Visual: Top 10 Medications
```
Chart Type: Horizontal Bar Chart

Data:
- Axis: medication_name (top 10 by demand)
- Value: Sum(predicted_demand_30d) or Sum(forecasted_quantity)

Format:
- Title: "TOP 10 MEDICATIONS (30-Day)"
- Title text: 12pt, Bold
- Row limit: 10 (do not show more)
- Sort: Value descending (highest demand first)
- Data labels: ON (show values)
- Colors: Gradient from Green (low) to Red (high)
  * Green (#28A745) for low demand
  * Yellow for medium
  * Red (#DC3545) for high demand
- Legend: OFF

Visual notes:
- Ibuprofen 200mg should be longest bar at top
- Shows medication priority for procurement
```

#### Right Visual: External Signals Correlation
```
Chart Type: Clustered Bar Chart

Data:
- Axis: Signal Type (Weather, Disease, Pollen)
- Value: Demand Increase % (e.g., +15%, +25%, +10%)

Setup:
1. Insert → Clustered Bar Chart
2. Axis: Signal type
3. Value: Correlation % (as numerical)
4. Format:
   - Title: "EXTERNAL SIGNALS CORRELATION"
   - Title text: 12pt, Bold
   - Data labels: ON (show percentages)
   - Add reference line at 0% (baseline)
   - Colors: Light blue bars
   - Y-axis: Shows percentage scale

Visual appearance:
- 3 bars (Weather, Disease, Pollen)
- Each shows how much they increase demand
- Reference line at 0 (baseline)
- Helps explain forecast drivers
```

---

### Step 5: Row 4 - Actionable Recommendations Table (Full Width)

```
Chart Type: Table

Columns (in order):
├── medication_name
├── category
├── current_inventory
├── predicted_demand_30d
├── days_supply
├── urgency_level
└── suggested_action

Format:
- Title: "ACTIONABLE RECOMMENDATIONS"
- Title text: 14pt, Bold
- Row limit: 10-15 rows
- Enable pagination
- Conditional formatting on urgency:
  * CRITICAL: Red background (#FFE6E6)
  * HIGH: Orange background (#FFF3E0)
  * MEDIUM: Yellow background (#FFFDE7)
  * LOW: Green background (#E8F5E9)
- Sort: urgency (CRITICAL first), then by days_supply (ascending)
- Font: Segoe UI, 11pt
- Header: Bold, dark blue background

Visual notes:
- CRITICAL and HIGH urgency items visible at top
- Red rows immediately catch attention
- Helps prioritize reordering
```

---

### Step 6: Row 5 - Agent Insight (Optional Info Box)

```
Text box at bottom:
"ℹ️ AGENT INSIGHT: Demand Forecast Agent predicts 847 units 
 of top 10 medications needed in next 30 days. Weather impact 
 detected (+25% increase during recent temp drop). 
 Start reorders immediately for CRITICAL items."
```

---

## 🎨 Global Formatting (All Dashboards)

### Color Palette
```
Primary:     Dark Blue (#0066CC)    - Headers, titles
Secondary:   Light Blue (#E7F2FF)   - Backgrounds, cards
Danger:      Red (#DC3545)          - Critical alerts
Warning:     Orange (#FFC107)       - High priority
Success:     Green (#28A745)        - OK, good status
Text Dark:   Dark Gray (#333333)    - Titles
Text Light:  Medium Gray (#666666)  - Labels
```

### Typography
```
Titles:      14pt, Bold, Dark Blue (#0066CC)
Subtitles:   12pt, Regular, Gray (#666666)
Values:      32pt, Bold, Black (#000000)
Labels:      11pt, Regular, Gray (#666666)
Data:        11pt, Regular, Dark Gray (#333333)
```

### Spacing
```
Top margin (filters to cards):     15px
Between sections:                   10px
Card padding:                        15px
Table row height:                    35px
Visual margins:                      5px
```

---

## 📋 Checklist: Dashboard Complete

### Dashboard 1: Expiration Risk
- [ ] 3 KPI cards (At-Risk Value, Expiring 7-14D, Critical 0-7D)
- [ ] Risk Timeline line chart (shows trend over 30 days)
- [ ] Risk by Category horizontal bar chart
- [ ] Detailed Inventory table (10 rows, conditional formatting)
- [ ] Date/Facility/Category slicers working
- [ ] Color scheme applied (red/orange/yellow)
- [ ] Agent insight box at bottom

### Dashboard 2: Transfer Coordination
- [ ] 3 KPI cards (Potential Savings, Surplus, Shortage)
- [ ] Facility Capacity Usage horizontal bar chart
- [ ] Transfer Network Map (Sankey or matrix)
- [ ] Cost Breakdown stacked bar chart
- [ ] Transfer Proposals table (status color-coded)
- [ ] Status/Facility slicers working
- [ ] Green/teal color scheme for savings dashboard
- [ ] Agent insight box at bottom

### Dashboard 3: Demand Forecast
- [ ] 3 KPI cards (Accuracy, Anomalies, Stockout Risk)
- [ ] 30-Day Forecast large combo chart (line + confidence band)
- [ ] Top 10 Medications horizontal bar (green-to-red gradient)
- [ ] External Signals correlation bar chart
- [ ] Actionable Recommendations table (urgency-colored)
- [ ] Urgency/Facility slicers working
- [ ] Blue color scheme for forecast dashboard
- [ ] Agent insight box at bottom

---

## 💡 Pro Tips

1. **Alignment:** Use "Align" tools to line up cards and charts perfectly
2. **Grouping:** Group related elements (e.g., 3 cards together) for easy resizing
3. **Mobile Layout:** Test mobile layout - use Portrait for dashboards
4. **Conditional Formatting:** Use data-driven coloring for immediate visual impact
5. **Refresh:** Remember to refresh data when API values change
6. **Export:** Save as PowerBI_Pharma_Dashboard_Complete.pbix

---

## ✅ Next: Share & Publish

Once all 3 dashboards are complete:
1. File → Save As → PowerBI_Pharma_Dashboard_Complete.pbix
2. (Optional) File → Publish to Power BI Service
3. Share with stakeholders
4. Setup auto-refresh schedule

**Congratulations! You've replicated the complete UI/UX design in PowerBI!** 🎉
