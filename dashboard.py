import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import numpy as np
import logging

# Import agent recommendation functions
from dashboard_agent_integration import (
    get_expiration_agent_recommendations,
    get_transfer_agent_recommendations,
    get_demand_agent_insights,
    get_cost_benefit_analysis,
    get_risk_assessment,
    get_predictive_alerts,
    get_master_strategy,
    display_agent_header,
    display_agent_recommendations_table,
    display_agent_metrics,
    render_ai_badge,
    render_ai_status_banner,
)

# ============================================================================
# CONFIG & SETUP
# ============================================================================

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Pharma Inventory Optimization Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .metric-card-critical {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card-warning {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 12px;
        opacity: 0.9;
        margin-top: 8px;
    }
    .metric-trend {
        font-size: 11px;
        margin-top: 5px;
        opacity: 0.85;
    }
    .dashboard-title {
        color: #2c3e50;
        text-align: center;
        padding: 20px 0;
        border-bottom: 3px solid #667eea;
        margin-bottom: 20px;
    }
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
    }
    .critical-box {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 4px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# API CONNECTION
# ============================================================================

API_BASE = "http://127.0.0.1:8000"

def get_api_data(endpoint):
    """Fetch data from FastAPI backend with caching and filtering by facility AND date range"""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Extract the 'data' key if it exists
        data_list = data.get('data', []) if isinstance(data, dict) else data
        
        if not data_list:
            return []
        
        # Convert to DataFrame for easier filtering
        df = pd.DataFrame(data_list)
        
        # Filter by facility if not "All"
        if hasattr(st.session_state, 'facility') and st.session_state.facility != 'All':
            facility_name = st.session_state.facility
            if 'facility_name' in df.columns:
                df = df[df['facility_name'] == facility_name]
            elif 'facility_id' in df.columns:
                df = df[df['facility_id'] == facility_name]
            elif 'from_facility' in df.columns:  # For transfer data
                df = df[df['from_facility'] == facility_name]

        return df.to_dict('records')
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_health_check():
    """Check API connectivity"""
    try:
        resp = requests.get(f"{API_BASE}/api/v1/health/health", timeout=5)
        return resp.status_code == 200
    except:
        return False

@st.cache_data(ttl=300)
def get_available_date_range():
    """Fetch the available date range from the API"""
    try:
        resp = requests.get(f"{API_BASE}/api/v1/powerbi/date-range", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract overall range
        if 'overall_range' in data:
            overall = data['overall_range']
            min_date = datetime.strptime(overall['min_date'], '%Y-%m-%d').date() if overall.get('min_date') else datetime.now().date() - timedelta(days=30)
            max_date = datetime.strptime(overall['max_date'], '%Y-%m-%d').date() if overall.get('max_date') else datetime.now().date()
            return min_date, max_date
        
        return None, None
    except Exception as e:
        logger.warning(f"Could not fetch date range from API: {e}")
        return None, None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def render_metric_card(col, value, label, trend=None, is_critical=False, is_warning=False):
    """Render a KPI metric card"""
    style_class = "metric-card"
    if is_critical:
        style_class += " metric-card-critical"
    elif is_warning:
        style_class += " metric-card-warning"
    
    trend_html = f"<div class='metric-trend'>↑ {trend}</div>" if trend else ""

    # data-render forces Streamlit 1.24 to re-render the node when label or value changes
    col.markdown(f"""
        <div class='{style_class}' data-render='{label}|{value}'>
            <div class='metric-label'>{label}</div>
            <div class='metric-value'>{value}</div>
            {trend_html}
        </div>
    """, unsafe_allow_html=True)

def create_timeline_chart(df, value_col="days_until_expiry", title=None, horizon_val=30):
    """
    Expiration countdown Gantt chart (sparse) or facility×bucket heatmap (dense).

    SPARSE (≤80 items): Each batch = one horizontal bar stretching from today (0)
    to its expiry day, grouped by "Medication — Facility", colored by risk level.
    Urgency zone bands in the background provide instant urgency context.

    DENSE (>80 items): Facility × time-bucket heatmap. Cell color = dominant risk,
    cell text = item count — shows which facilities need attention and when.
    """
    RISK_COLORS = {
        "EXPIRED":  "#6a1b9a",
        "CRITICAL": "#c62828",
        "HIGH":     "#ef6c00",
        "MEDIUM":   "#f9a825",
        "LOW":      "#64b5f6",
    }
    RISK_ORDER  = ["EXPIRED", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
    RISK_WEIGHT = {"EXPIRED": 5, "CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text="No expiration data for selected filters",
        xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=14, color="#888"),
    )
    empty_fig.update_layout(height=440, template="plotly_white")

    if df.empty or value_col not in df.columns:
        return empty_fig

    df = df.copy()
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    if df.empty:
        return empty_fig

    risk_col = "risk_level"       if "risk_level"       in df.columns else None
    val_col  = "batch_value"      if "batch_value"       in df.columns else None
    fac_col  = "facility_name"    if "facility_name"     in df.columns else None
    med_col  = "medication_name"  if "medication_name"   in df.columns else None
    qty_col  = "quantity_on_hand" if "quantity_on_hand"  in df.columns else None
    bid_col  = "batch_id"         if "batch_id"          in df.columns else None

    chart_title = title or "Expiration Risk Timeline"
    n_items = len(df)
    x_min = int(df[value_col].min())
    x_max = int(df[value_col].max())

    # ── Urgency zone bands (shared) ───────────────────────────────────────────
    ZONE_DEFS = [
        (None,  -1,  "rgba(130,0,0,0.06)",      "Expired"),
        (0,      7,  "rgba(198,40,40,0.10)",     "Critical  0–7d"),
        (8,     30,  "rgba(239,108,0,0.08)",     "High  8–30d"),
        (31,    90,  "rgba(249,168,37,0.06)",    "Medium  31–90d"),
        (91,  9999,  "rgba(100,181,246,0.05)",   "Low  91d+"),
    ]

    def add_urgency_zones(fig, x_lo, x_hi):
        for z_lo, z_hi, color, label in ZONE_DEFS:
            lo = x_lo if z_lo is None else z_lo
            hi = z_hi
            if lo > x_hi or hi < x_lo:
                continue
            fig.add_vrect(
                x0=max(lo, x_lo), x1=min(hi, x_hi),
                fillcolor=color, line_width=0, layer="below",
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # DENSE MODE  (>80 items) — Heatmap: facility × time bucket
    # Short horizons (≤30d) use the Gantt chart only when the dataset is small enough to be readable.
    # If there are >50 items even in a short window, fall back to the heatmap so nothing is cut off.
    # ═══════════════════════════════════════════════════════════════════════════
    force_gantt = isinstance(horizon_val, int) and horizon_val <= 30 and n_items <= 50
    if n_items > 80 and not force_gantt:
        if horizon_val == "past":
            buckets = [(-999999, -91, ">90d Ago"), (-90, -31, "31-90d Ago"),
                       (-30, -8, "8-30d Ago"), (-7, -1, "≤7d Ago")]
        elif isinstance(horizon_val, int) and horizon_val <= 30:
            buckets = [(-999999,-1,"Expired"),(0,7,"0-7d"),(8,14,"8-14d"),(15,30,"15-30d")]
        elif isinstance(horizon_val, int) and horizon_val <= 90:
            buckets = [(-999999,-1,"Expired"),(0,7,"0-7d"),(8,30,"8-30d"),
                       (31,60,"31-60d"),(61,90,"61-90d")]
        else:
            buckets = [(-999999,-1,"Expired"),(0,7,"0-7d"),(8,30,"8-30d"),
                       (31,90,"31-90d"),(91,180,"91-180d"),(181,9999,"181d+")]

        facilities = sorted(df[fac_col].dropna().unique()) if fac_col else ["All"]
        bkt_labels = [b[2] for b in buckets]

        # Build z (dominant risk weight), text (count), and color
        z_matrix, text_matrix, color_matrix = [], [], []
        # Map each bucket to a sensible fallback risk based on its day range
        def bucket_risk(lo, hi):
            """Risk inferred purely from time window (used when stored risk_level is unreliable)."""
            if hi < 0:   return "EXPIRED"
            if hi <= 7:  return "CRITICAL"
            if hi <= 30: return "HIGH"
            if hi <= 90: return "MEDIUM"
            return "LOW"

        for fac in facilities:
            fac_df = df[df[fac_col] == fac] if fac_col else df
            z_row, t_row, c_row = [], [], []
            for lo, hi, _ in buckets:
                mask = (fac_df[value_col] >= lo) & (fac_df[value_col] <= hi)
                subset = fac_df[mask]
                count = len(subset)
                if count == 0:
                    z_row.append(0)
                    t_row.append("")
                    c_row.append("rgba(240,240,240,0.3)")
                    continue
                # For future buckets (lo >= 0), derive risk from time window so that
                # stale "EXPIRED" labels in the DB don't corrupt the colour.
                if lo >= 0:
                    dom_risk = bucket_risk(lo, hi)
                else:
                    dom_risk = "EXPIRED"
                z_row.append(RISK_WEIGHT[dom_risk])
                t_row.append(f"{count}")
                c_row.append(RISK_COLORS[dom_risk])
            z_matrix.append(z_row)
            text_matrix.append(t_row)

        colorscale = [
            [0.00, "#f5f5f5"],
            [0.20, RISK_COLORS["LOW"]],
            [0.40, RISK_COLORS["MEDIUM"]],
            [0.60, RISK_COLORS["HIGH"]],
            [0.80, RISK_COLORS["CRITICAL"]],
            [1.00, RISK_COLORS["EXPIRED"]],
        ]

        fig = go.Figure(go.Heatmap(
            z=z_matrix,
            x=bkt_labels,
            y=facilities,
            text=text_matrix,
            texttemplate="%{text}",
            textfont=dict(size=13, color="white"),
            colorscale=colorscale,
            zmin=0, zmax=5,
            showscale=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Window: %{x}<br>"
                "Items: %{text}<extra></extra>"
            ),
            xgap=3, ygap=3,
        ))

        # Risk legend as annotations
        for i, (risk, color) in enumerate(RISK_COLORS.items()):
            fig.add_annotation(
                xref="paper", yref="paper",
                x=0.01 + i * 0.14, y=-0.12,
                text=f"<span style='color:{color}'>■</span> {risk}",
                showarrow=False, font=dict(size=11),
            )

        fig.update_layout(
            title=dict(text=chart_title, font=dict(size=15, color="#2c3e50"), x=0),
            xaxis=dict(title="Expiry Window", side="top", tickfont=dict(size=12)),
            yaxis=dict(title="Facility", tickfont=dict(size=11), autorange="reversed"),
            template="plotly_white",
            height=max(320, 60 + len(facilities) * 42),
            plot_bgcolor="#fafafa",
            margin=dict(l=20, r=20, t=80, b=60),
        )
        return fig

    # ═══════════════════════════════════════════════════════════════════════════
    # SPARSE MODE  (≤80 items) — Gantt countdown chart
    # ═══════════════════════════════════════════════════════════════════════════
    # Build row label: "Medication — Facility (BatchID)"
    rows_data = []
    for _, row in df.iterrows():
        days = int(row[value_col])
        med  = str(row[med_col])  if med_col  else "Batch"
        fac  = str(row[fac_col])  if fac_col  else ""
        bid  = str(row[bid_col])  if bid_col  else ""
        risk = str(row[risk_col]) if risk_col else "LOW"
        val  = float(row[val_col])  if val_col  and pd.notna(row[val_col])  else 0
        qty  = int(row[qty_col])    if qty_col  and pd.notna(row[qty_col])   else 0

        # If a future item has a stale "EXPIRED" label in the DB, remap it
        # to the appropriate risk level based on actual days remaining.
        if days >= 0 and risk == "EXPIRED":
            if days <= 7:   risk = "CRITICAL"
            elif days <= 30: risk = "HIGH"
            elif days <= 90: risk = "MEDIUM"
            else:            risk = "LOW"

        # Row label: medication + facility (truncated for readability)
        med_short = med[:28] + "…" if len(med) > 28 else med
        fac_short = fac.replace(" Medical Center","").replace(" Hospital","") \
                       .replace(" Health Clinic","").replace(" Regional","")
        label = f"{med_short}  ·  {fac_short}" if fac_short else med_short
        if bid:
            label += f"  [{bid[-6:]}]"

        rows_data.append({
            "label": label, "days": days, "risk": risk,
            "val": val, "qty": qty, "med": med, "fac": fac, "bid": bid,
        })

    # Sort: most urgent (smallest days) first, expired last
    rows_data.sort(key=lambda r: (r["days"] >= 0, r["days"]))

    # Capture full-dataset stats BEFORE capping (so badge reflects all batches, not just displayed ones)
    total_critical_high_all = sum(1 for r in rows_data if r["risk"] in ("CRITICAL", "HIGH"))
    total_value_all = sum(r["val"] for r in rows_data)

    # Cap rows for short horizons to keep chart readable
    max_rows = 30 if (isinstance(horizon_val, int) and horizon_val <= 7) else \
               50 if (isinstance(horizon_val, int) and horizon_val <= 30) else len(rows_data)
    if len(rows_data) > max_rows:
        rows_data = rows_data[:max_rows]

    labels = [r["label"] for r in rows_data]
    # De-duplicate labels
    seen: dict = {}
    clean_labels = []
    for lbl in labels:
        seen[lbl] = seen.get(lbl, 0) + 1
        clean_labels.append(lbl if seen[lbl] == 1 else f"{lbl} ({seen[lbl]})")
    for i, r in enumerate(rows_data):
        r["label"] = clean_labels[i]

    fig = go.Figure()

    # Urgency zone shading
    add_urgency_zones(fig, x_min - 2, x_max + 2)

    # One bar trace per risk level for legend grouping
    for risk in RISK_ORDER:
        subset = [r for r in rows_data if r["risk"] == risk]
        if not subset:
            continue
        fig.add_trace(go.Bar(
            name=risk,
            orientation="h",
            y=[r["label"] for r in subset],
            # bar spans from 0 → days (or days → 0 for expired)
            x=[r["days"] if r["days"] >= 0 else abs(r["days"]) for r in subset],
            base=[0 if r["days"] >= 0 else r["days"] for r in subset],
            marker=dict(
                color=RISK_COLORS[risk],
                opacity=0.85,
                line=dict(color="white", width=1),
            ),
            customdata=[[r["val"], r["qty"], r["days"], r["fac"], r["bid"]]
                        for r in subset],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "⏱ Expires in: <b>%{customdata[2]}d</b><br>"
                "💰 Value: $%{customdata[0]:,.0f}<br>"
                "📦 Qty: %{customdata[1]:,} units<br>"
                "🏥 %{customdata[3]}<br>"
                "Batch: %{customdata[4]}"
                "<extra></extra>"
            ),
            width=0.55,
        ))

    # "Today" vertical line
    fig.add_vline(
        x=0, line_dash="solid", line_color="#546e7a", line_width=2,
        annotation_text="<b>Today</b>",
        annotation_position="top right",
        annotation_font=dict(size=11, color="#546e7a"),
    )

    total_critical_high = total_critical_high_all
    total_value = total_value_all

    row_height = 36
    chart_h = min(700, max(300, 90 + len(rows_data) * row_height))

    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=15, color="#2c3e50"), x=0),
        xaxis=dict(
            title="Days Until Expiry  (← expired | upcoming →)",
            gridcolor="#eeeeee",
            zeroline=False,
            ticksuffix="d",
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            autorange="reversed",     # most urgent at top
            showgrid=False,
        ),
        barmode="overlay",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="right", x=1, font=dict(size=11),
        ),
        hovermode="closest",
        template="plotly_white",
        height=chart_h,
        plot_bgcolor="#fafafa",
        margin=dict(l=10, r=20, t=60, b=50),
        annotations=[
            dict(
                xref="paper", yref="paper", x=0.01, y=1.0,
                text=(
                    f"<b>🚨 {total_critical_high} CRITICAL/HIGH batches</b>"
                    f"  ·  Total value at risk: <b>${total_value:,.0f}</b>"
                ),
                showarrow=False,
                font=dict(size=12, color="#c62828"),
                bgcolor="rgba(255,235,235,0.92)",
                bordercolor="#c62828", borderwidth=1, borderpad=5,
                yanchor="bottom",
            )
        ] if total_critical_high > 0 else [],
    )
    return fig


def create_top_at_risk_medications(df, n=10):
    """Horizontal bar — top N medications by batch value at risk, colored by risk level."""
    RISK_COLORS = {"EXPIRED": "#6a1b9a", "CRITICAL": "#c62828",
                   "HIGH": "#ef6c00", "MEDIUM": "#f9a825", "LOW": "#1565c0"}

    empty_fig = go.Figure()
    empty_fig.add_annotation(text="No medication data available",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font=dict(size=13, color="#888"))
    empty_fig.update_layout(height=380, template="plotly_white")

    if df.empty or "medication_name" not in df.columns:
        return empty_fig

    risk_col = "risk_level" if "risk_level" in df.columns else None
    val_col  = "batch_value" if "batch_value" in df.columns else None
    days_col = "days_until_expiry" if "days_until_expiry" in df.columns else None

    agg: dict = {}
    for _, row in df.iterrows():
        med = row["medication_name"]
        val = float(row[val_col]) if val_col else 1
        risk = row[risk_col] if risk_col else "LOW"
        days = int(row[days_col]) if days_col and pd.notna(row[days_col]) else 9999
        if med not in agg:
            agg[med] = {"value": 0, "count": 0, "risk": risk, "min_days": days}
        agg[med]["value"] += val
        agg[med]["count"] += 1
        # Escalate risk level if this batch is more critical
        order = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "EXPIRED"]
        r_idx   = order.index(risk)              if risk              in order else 0
        cur_idx = order.index(agg[med]["risk"])  if agg[med]["risk"]  in order else 0
        if r_idx > cur_idx:
            agg[med]["risk"] = risk
        agg[med]["min_days"] = min(agg[med]["min_days"], days)

    df_agg = pd.DataFrame([
        {"Medication": k, "Value": v["value"], "Batches": v["count"],
         "Risk": v["risk"], "Min Days": v["min_days"]}
        for k, v in agg.items()
    ]).sort_values("Value", ascending=False).head(n)

    if df_agg.empty:
        return empty_fig

    # Ensure Value is numeric
    df_agg["Value"] = pd.to_numeric(df_agg["Value"], errors="coerce").fillna(0)

    # Sort so highest value is at top of horizontal bar
    df_agg = df_agg.sort_values("Value", ascending=True)

    RISK_ORDER = ["EXPIRED", "CRITICAL", "HIGH", "MEDIUM", "LOW"]

    fig = go.Figure()
    for risk in RISK_ORDER:
        subset = df_agg[df_agg["Risk"] == risk]
        if subset.empty:
            continue
        color = RISK_COLORS.get(risk, "#888")
        fig.add_trace(go.Bar(
            x=subset["Value"].tolist(),
            y=subset["Medication"].tolist(),
            name=risk,
            orientation="h",
            marker=dict(color=color, line=dict(color="white", width=0.5)),
            customdata=list(zip(subset["Risk"], subset["Batches"], subset["Min Days"])),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Value at Risk: $%{x:,.0f}<br>"
                "Risk Level: %{customdata[0]}<br>"
                "Batches: %{customdata[1]}<br>"
                "Soonest Expiry: %{customdata[2]}d"
                "<extra></extra>"
            ),
            text=[f"${v:,.0f}" for v in subset["Value"].tolist()],
            textposition="auto",
            textfont=dict(size=10),
        ))

    fig.update_layout(
        title=dict(text=f"Top {n} Medications by Value at Risk",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(
            title="Total Batch Value ($)",
            tickformat="$,.0f",
            autorange=True,
        ),
        yaxis=dict(tickfont=dict(size=11)),
        template="plotly_white",
        height=420,
        plot_bgcolor="#fafafa",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=11),
            traceorder="normal",
        ),
        margin=dict(l=10, r=20, t=70, b=40),
        uniformtext=dict(minsize=8, mode="hide"),
    )
    return fig

def create_category_pie_chart(df, title="Risk by Category"):
    """Pie chart showing % of at-risk inventory value by drug category."""
    if df.empty or 'category' not in df.columns:
        return go.Figure().add_annotation(text="No category data", xref="paper", yref="paper",
                                          x=0.5, y=0.5, showarrow=False)

    if 'batch_value' in df.columns:
        grouped = df.groupby('category')['batch_value'].sum().sort_values(ascending=False)
        hover_label = "Value at Risk ($)"
    else:
        grouped = df['category'].value_counts()
        hover_label = "Item Count"

    fig = go.Figure(go.Pie(
        labels=grouped.index.tolist(),
        values=grouped.values.tolist(),
        marker=dict(
            colors=px.colors.qualitative.Set2,
            line=dict(color="white", width=2)
        ),
        texttemplate="%{percent:.1%}",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>" + hover_label + ": $%{value:,.0f}<br>Share: %{percent:.1%}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#2c3e50"), x=0),
        height=380,
        template="plotly_white",
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=11)),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig

def create_facility_flow_chart(df):
    """Diverging horizontal bar: net units flowing OUT (surplus donor) vs IN (shortage receiver) per facility."""
    empty = go.Figure()
    empty.add_annotation(text="No transfer data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=350, template="plotly_white")
    if df.empty or "from_facility" not in df.columns:
        return empty

    qty_col = "quantity" if "quantity" in df.columns else None
    if not qty_col:
        return empty

    out_by = df.groupby("from_facility")[qty_col].sum().rename("units_out")
    in_by  = df.groupby("to_facility")[qty_col].sum().rename("units_in")
    fac_df = pd.DataFrame({"units_out": out_by, "units_in": in_by}).fillna(0)
    fac_df["net_flow"] = fac_df["units_out"] - fac_df["units_in"]
    fac_df = fac_df.sort_values("net_flow")

    # Savings per facility (how much value is each facility generating by donating)
    sav_col = "estimated_savings" if "estimated_savings" in df.columns else None
    if sav_col:
        sav_out = df.groupby("from_facility")[sav_col].sum().rename("savings")
        fac_df = fac_df.join(sav_out, how="left").fillna({"savings": 0})
    else:
        fac_df["savings"] = 0

    colors = ["#ef5350" if v < 0 else "#66bb6a" for v in fac_df["net_flow"]]

    hover_texts = [
        (
            f"<b>{fac}</b><br>"
            f"Net flow: <b>{int(fac_df.loc[fac, 'net_flow']):+,} units</b><br>"
            f"Donating (units out): <b>{int(fac_df.loc[fac, 'units_out']):,}</b><br>"
            f"Receiving (units in): <b>{int(fac_df.loc[fac, 'units_in']):,}</b><br>"
            f"Savings generated: <b>${fac_df.loc[fac, 'savings']:,.0f}</b>"
        )
        for fac in fac_df.index
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=fac_df.index,
        x=fac_df["net_flow"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=0.5)),
        hovertext=hover_texts,
        hoverinfo="text",
        text=[f"{int(v):+,d}" for v in fac_df["net_flow"]],
        textposition="outside",
        textfont=dict(size=11),
    ))

    fig.add_vline(x=0, line_color="#546e7a", line_width=1.5,
                  annotation_text="Balanced", annotation_position="top",
                  annotation_font=dict(size=10, color="#546e7a"))

    fig.update_layout(
        title=dict(text="Facility Net Flow  (🟢 Surplus Donor  |  🔴 Shortage Receiver)",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Net Units (+ outgoing surplus  |  − incoming demand)", zeroline=False,
                   gridcolor="#eeeeee"),
        yaxis=dict(tickfont=dict(size=11), showgrid=False),
        template="plotly_white",
        height=max(320, 60 + len(fac_df) * 44),
        margin=dict(l=10, r=50, t=55, b=40),
        showlegend=False,
        plot_bgcolor="#fafafa",
    )
    return fig

def create_transfer_sankey(df, highlight_pair=None):
    """Sankey diagram of real facility-to-facility transfer flows.
    highlight_pair: optional (from_facility, to_facility) tuple — that ribbon
    gets a vivid colour, all others are dimmed.
    """
    empty = go.Figure()
    empty.add_annotation(text="No transfer data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=380, template="plotly_white")
    if df.empty or "from_facility" not in df.columns or "to_facility" not in df.columns:
        return empty

    qty_col  = "quantity"             if "quantity"             in df.columns else None
    sav_col  = "estimated_savings"    if "estimated_savings"    in df.columns else None
    cost_col = "total_transfer_cost"  if "total_transfer_cost"  in df.columns else None
    if not qty_col:
        return empty

    agg_cols = {qty_col: "sum"}
    if sav_col:  agg_cols[sav_col]  = "sum"
    if cost_col: agg_cols[cost_col] = "sum"

    flows = df.groupby(["from_facility", "to_facility"]).agg(agg_cols).reset_index()
    flows.columns = ["from_facility", "to_facility"] + list(agg_cols.keys())

    # Always keep the highlighted route even if it's outside the top 12 by volume
    if highlight_pair and highlight_pair != ("All Facilities", "All Facilities"):
        hl_f, hl_t = highlight_pair
        def row_matches(r):
            fm = (hl_f == "All Facilities" or r["from_facility"] == hl_f)
            tm = (hl_t == "All Facilities" or r["to_facility"]   == hl_t)
            return fm and tm
        highlighted_rows = flows[flows.apply(row_matches, axis=1)]
        top12 = flows.nlargest(12, qty_col)
        flows = pd.concat([top12, highlighted_rows]).drop_duplicates().reset_index(drop=True)
    else:
        flows = flows.nlargest(12, qty_col)

    def shorten(name):
        return (name.replace("Medical Center", "Med Ctr")
                    .replace("Community Hospital", "Comm Hosp")
                    .replace("Health Clinic", "Clinic")
                    .replace("Regional Medical", "Regional"))

    all_nodes = sorted(set(flows["from_facility"].tolist() + flows["to_facility"].tolist()))
    node_idx  = {n: i for i, n in enumerate(all_nodes)}
    labels    = [shorten(n) for n in all_nodes]
    n_nodes   = len(all_nodes)
    node_colors = [f"hsl({int(220 + 120 * i / max(n_nodes - 1, 1))}, 55%, 55%)"
                   for i in range(n_nodes)]

    # Link colours: highlight selected route(s), dim everything else
    # highlight_pair = (from, to) where either can be "All Facilities" meaning "any"
    has_highlight = highlight_pair is not None and highlight_pair != ("All Facilities", "All Facilities")
    hl_from = highlight_pair[0] if has_highlight else None
    hl_to   = highlight_pair[1] if has_highlight else None

    link_colors, link_customdata = [], []
    for _, row in flows.iterrows():
        sav  = row[sav_col]  if sav_col  else 0
        cost = row[cost_col] if cost_col else 0
        link_customdata.append([int(row[qty_col]), sav, cost])
        if has_highlight:
            from_match = (hl_from == "All Facilities" or row["from_facility"] == hl_from)
            to_match   = (hl_to   == "All Facilities" or row["to_facility"]   == hl_to)
            if from_match and to_match:
                link_colors.append("rgba(255, 107, 53, 0.87)")   # vivid orange — selected
            else:
                link_colors.append("rgba(180, 180, 180, 0.15)")  # dimmed
        else:
            link_colors.append("rgba(100,126,234,0.38)")

    title_suffix = (
        f"  ·  <span style='color:#ff6b35;'>highlighted: {shorten(highlight_pair[0])} → {shorten(highlight_pair[1])}</span>"
        if has_highlight else ""
    )

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18, thickness=22,
            line=dict(color="#ccc", width=0.5),
            label=labels,
            color=node_colors,
            hovertemplate="<b>%{label}</b><br>Total flow: %{value:,} units<extra></extra>",
        ),
        link=dict(
            source=[node_idx[r] for r in flows["from_facility"]],
            target=[node_idx[r] for r in flows["to_facility"]],
            value=flows[qty_col].tolist(),
            customdata=link_customdata,
            color=link_colors,
            hovertemplate=(
                "<b>%{source.label}  →  %{target.label}</b><br>"
                "Quantity: <b>%{customdata[0]:,} units</b><br>"
                "Est. Savings: $%{customdata[1]:,.0f}<br>"
                "Transfer Cost: $%{customdata[2]:,.0f}"
                "<extra></extra>"
            ),
        ),
    ))

    fig.update_layout(
        title=dict(
            text=f"Transfer Network — Unit Flow{title_suffix}",
            font=dict(size=14, color="#2c3e50"), x=0,
        ),
        template="plotly_white",
        height=380,
        margin=dict(l=10, r=10, t=55, b=10),
        font=dict(size=11),
    )
    return fig

def create_cost_breakdown_chart(df, title_override=None, route_active=False):
    """
    Global view  (route_active=False): horizontal Cost vs Savings bars by transfer status.
    Route view   (route_active=True):  subplot — left: cost waterfall, right: donut by rationale.
    """
    empty = go.Figure()
    empty.add_annotation(text="No transfer data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=320, template="plotly_white")
    if df.empty:
        return empty

    cost_col = "total_transfer_cost"    if "total_transfer_cost"    in df.columns else None
    sav_col  = "estimated_savings"      if "estimated_savings"      in df.columns else None
    val_col  = "total_medication_value" if "total_medication_value" in df.columns else None
    qty_col  = "quantity"               if "quantity"               in df.columns else None
    rat_col  = "rationale"              if "rationale"              in df.columns else None
    stat_col = "status"                 if "status"                 in df.columns else None

    # ══════════════════════════════════════════════════════════════════════════
    # ROUTE VIEW — 2-panel subplot
    # ══════════════════════════════════════════════════════════════════════════
    if route_active:
        from plotly.subplots import make_subplots

        total_cost   = float(df[cost_col].sum())  if cost_col else 0
        total_sav    = float(df[sav_col].sum())   if sav_col  else 0
        total_val    = float(df[val_col].sum())   if val_col  else 0
        total_qty    = int(df[qty_col].sum())     if qty_col  else 0
        net          = total_sav - total_cost
        n_transfers  = len(df)

        # ── Left: waterfall-style horizontal summary bar ───────────────────
        # Components: Medication Value · Transfer Overhead · Savings · Net
        categories = ["Medication Value", "Transfer\nOverhead", "Savings\nRecovered", "Net Position"]
        values     = [total_val, total_cost, total_sav, net]
        bar_colors = ["#667eea", "#ef5350", "#26a69a", "#26a69a" if net >= 0 else "#ef5350"]

        # ── Right: donut by transfer rationale ────────────────────────────
        if rat_col and df[rat_col].notna().any():
            rat_counts = df.groupby(rat_col).size().reset_index(name="count")
        else:
            # fallback: by status
            rat_counts = df.groupby(stat_col).size().reset_index(name="count") if stat_col else None

        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.52, 0.48],
            specs=[[{"type": "xy"}, {"type": "domain"}]],
            subplot_titles=["💰 Cost Components", "📋 Transfer Reasons"],
        )

        # Left bars
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker=dict(color=bar_colors, opacity=0.88,
                        line=dict(color="white", width=1.5)),
            text=[f"${v:,.0f}" for v in values],
            textposition="outside",
            textfont=dict(size=12, color="#2c3e50"),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
            showlegend=False,
        ), row=1, col=1)

        # "Today = break-even" line on left
        fig.add_hline(y=0, line_color="#999", line_width=1, row=1, col=1)

        # Right donut
        if rat_counts is not None and len(rat_counts) > 0:
            rat_col_name = rat_counts.columns[0]
            RATIONALE_COLORS = {
                "Expiration Management": "#ef6c00",
                "Shortage Prevention":   "#1565c0",
                "Demand Spike":          "#6a1b9a",
                "Regulatory":            "#2e7d32",
            }
            d_colors = [RATIONALE_COLORS.get(r, "#90a4ae")
                        for r in rat_counts[rat_col_name]]
            fig.add_trace(go.Pie(
                labels=rat_counts[rat_col_name],
                values=rat_counts["count"],
                hole=0.52,
                marker=dict(colors=d_colors, line=dict(color="white", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>%{value} transfers (%{percent})<extra></extra>",
                showlegend=False,
            ), row=1, col=2)

            # Centre annotation in donut
            fig.add_annotation(
                text=f"<b>{n_transfers}</b><br>transfers",
                x=0.78, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=13, color="#2c3e50"),
            )

        net_color  = "#26a69a" if net >= 0 else "#ef5350"
        net_prefix = "+" if net >= 0 else ""
        fig.update_layout(
            title=dict(
                text=title_override or f"Route Cost Analysis  ·  {n_transfers} transfers  ·  {total_qty:,} units  ·  Net <b><span style='color:{net_color}'>{net_prefix}${net:,.0f}</span></b>",
                font=dict(size=13, color="#2c3e50"), x=0,
            ),
            template="plotly_white",
            height=360,
            margin=dict(l=10, r=20, t=75, b=50),
            plot_bgcolor="#fafafa",
        )
        fig.update_yaxes(tickprefix="$", gridcolor="#eeeeee", row=1, col=1)
        return fig

    # ══════════════════════════════════════════════════════════════════════════
    # GLOBAL VIEW — Cost vs Savings by status (horizontal bars)
    # ══════════════════════════════════════════════════════════════════════════
    if not stat_col or (not cost_col and not sav_col):
        return empty

    grp_order    = ["PENDING", "COMPLETED", "REJECTED"]
    STATUS_LABEL = {"PENDING": "🟡 Pending", "COMPLETED": "🟢 Completed", "REJECTED": "🔴 Rejected"}

    agg = {}
    if cost_col: agg[cost_col] = "sum"
    if sav_col:  agg[sav_col]  = "sum"
    agg["order_id"] = "count"

    g = (df.groupby(stat_col)
           .agg(agg)
           .reindex([s for s in grp_order if s in df[stat_col].unique()])
           .fillna(0)
           .reset_index())

    labels  = [STATUS_LABEL.get(s, s) for s in g[stat_col]]
    costs   = g[cost_col].tolist()  if cost_col else [0] * len(g)
    savings = g[sav_col].tolist()   if sav_col  else [0] * len(g)
    counts  = g["order_id"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Transfer Cost", y=labels, x=costs, orientation="h",
        marker=dict(color="#ef5350", opacity=0.82),
        text=[f"  ${v:,.0f}" for v in costs],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{y}</b><br>Transfer Cost: <b>$%{x:,.0f}</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Estimated Savings", y=labels, x=savings, orientation="h",
        marker=dict(color="#26a69a", opacity=0.88),
        text=[f"  ${v:,.0f}" for v in savings],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{y}</b><br>Estimated Savings: <b>$%{x:,.0f}</b><extra></extra>",
    ))

    annotations = []
    x_max = max(max(costs, default=0), max(savings, default=0)) or 1
    for i, (c, s, n) in enumerate(zip(costs, savings, counts)):
        net    = s - c
        color  = "#26a69a" if net >= 0 else "#ef5350"
        prefix = "+" if net >= 0 else ""
        annotations.append(dict(
            x=x_max * 1.01, y=labels[i],
            text=f"<b>Net {prefix}${net:,.0f}</b>  ({int(n)} transfers)",
            showarrow=False, xanchor="left",
            font=dict(size=11, color=color),
            xref="x", yref="y",
        ))

    fig.update_layout(
        title=dict(text=title_override or "Transfer Cost vs Savings by Status",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Amount ($)", gridcolor="#eeeeee", tickprefix="$", rangemode="tozero"),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        barmode="group", bargap=0.25, bargroupgap=0.08,
        template="plotly_white",
        height=max(280, 90 + len(g) * 80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=12)),
        margin=dict(l=10, r=220, t=55, b=40),
        plot_bgcolor="#fafafa",
        annotations=annotations,
    )
    return fig

def create_top_transfer_medications(df, n=12):
    """Horizontal bar — top N medications by quantity transferred, coloured by avg cost_benefit_score."""
    empty = go.Figure()
    empty.add_annotation(text="No medication data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=380, template="plotly_white")
    if df.empty or "medication_name" not in df.columns:
        return empty

    qty_col  = "quantity"           if "quantity"           in df.columns else None
    sav_col  = "estimated_savings"  if "estimated_savings"  in df.columns else None
    cbs_col  = "cost_benefit_score" if "cost_benefit_score" in df.columns else None
    rat_col  = "rationale"          if "rationale"          in df.columns else None

    agg = {}
    if qty_col:  agg[qty_col]  = "sum"
    if sav_col:  agg[sav_col]  = "sum"
    if cbs_col:  agg[cbs_col]  = "mean"
    if rat_col:  agg[rat_col]  = lambda x: x.mode().iloc[0] if len(x) > 0 else "Unknown"
    agg["order_id"] = "count"
    if not agg:
        return empty

    g = (df.groupby("medication_name").agg(agg)
           .reset_index()
           .sort_values(qty_col or list(agg.keys())[0], ascending=False)
           .head(n))

    RATIONALE_COLORS = {
        "Expiration Management": "#ef6c00",
        "Shortage Prevention":   "#1565c0",
        "Demand Spike":          "#6a1b9a",
        "Regulatory":            "#2e7d32",
    }
    bar_colors = ([RATIONALE_COLORS.get(r, "#90a4ae") for r in g[rat_col]]
                  if rat_col in g.columns else ["#667eea"] * len(g))

    qty_vals = g[qty_col].tolist() if qty_col else [1] * len(g)
    sav_vals = g[sav_col].tolist() if sav_col and sav_col in g.columns else [0] * len(g)
    cbs_vals = g[cbs_col].tolist() if cbs_col and cbs_col in g.columns else [0] * len(g)
    cnt_vals = g["order_id"].tolist()
    rat_vals = g[rat_col].tolist() if rat_col in g.columns else ["?"] * len(g)

    # Sort descending for chart (plotly horizontal bars show last row at top)
    idx_order = list(range(len(g) - 1, -1, -1))
    meds      = [g["medication_name"].iloc[i] for i in idx_order]
    qtys      = [qty_vals[i] for i in idx_order]
    savs      = [sav_vals[i] for i in idx_order]
    cbss      = [f"{cbs_vals[i]*100:.0f}%" for i in idx_order]
    cnts      = [cnt_vals[i] for i in idx_order]
    rats      = [rat_vals[i] for i in idx_order]
    colors    = [bar_colors[i] for i in idx_order]

    fig = go.Figure(go.Bar(
        y=meds, x=qtys, orientation="h",
        marker=dict(color=colors, opacity=0.85, line=dict(color="white", width=0.8)),
        customdata=list(zip(savs, cbss, cnts, rats)),
        text=[f"  {q:,} units" for q in qtys],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Qty transferred: <b>%{x:,} units</b><br>"
            "Est. savings: $%{customdata[0]:,.0f}<br>"
            "Avg efficiency: %{customdata[1]}<br>"
            "Transfer count: %{customdata[2]}<br>"
            "Primary reason: %{customdata[3]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    # Legend patches for rationale colours
    for label, color in RATIONALE_COLORS.items():
        if rat_col and label in (rat_vals or []):
            fig.add_trace(go.Bar(
                x=[None], y=[None], orientation="h",
                name=label,
                marker=dict(color=color),
                showlegend=True,
            ))

    fig.update_layout(
        title=dict(text=f"Top {n} Medications by Transfer Volume",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Units Transferred", gridcolor="#eeeeee"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        template="plotly_white",
        height=max(320, 60 + len(g) * 34),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    title="Primary Reason:", font=dict(size=11)),
        margin=dict(l=10, r=20, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_rationale_outcome_chart(df):
    """Grouped bar: for each transfer rationale, show count of COMPLETED / PENDING / REJECTED."""
    empty = go.Figure()
    empty.add_annotation(text="No rationale data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=320, template="plotly_white")
    if df.empty:
        return empty

    rat_col  = "rationale" if "rationale" in df.columns else None
    stat_col = "status"    if "status"    in df.columns else None
    sav_col  = "estimated_savings" if "estimated_savings" in df.columns else None
    if not rat_col or not stat_col:
        return empty

    pivot = (df.groupby([rat_col, stat_col])
               .size()
               .unstack(fill_value=0)
               .reset_index())

    # avg savings per rationale for annotation
    sav_by_rat = (df.groupby(rat_col)[sav_col].sum().to_dict() if sav_col else {})

    STATUS_CFG = {
        "COMPLETED": ("🟢 Completed", "#4caf50"),
        "PENDING":   ("🟡 Pending",   "#ff9800"),
        "REJECTED":  ("🔴 Rejected",  "#ef5350"),
    }

    fig = go.Figure()
    for status, (label, color) in STATUS_CFG.items():
        if status in pivot.columns:
            fig.add_trace(go.Bar(
                name=label,
                x=pivot[rat_col],
                y=pivot[status],
                marker=dict(color=color, opacity=0.85),
                text=pivot[status],
                textposition="auto",
                textfont=dict(size=11),
                hovertemplate="<b>%{x}</b><br>" + label + ": <b>%{y}</b><extra></extra>",
            ))

    # Savings annotation above each bar group
    annotations = []
    if sav_by_rat:
        for rat in pivot[rat_col]:
            sav = sav_by_rat.get(rat, 0)
            annotations.append(dict(
                x=rat, y=pivot.loc[pivot[rat_col] == rat,
                    [c for c in ["COMPLETED","PENDING","REJECTED"] if c in pivot.columns]].sum(axis=1).values[0],
                text=f"${sav:,.0f} saved",
                showarrow=False, yanchor="bottom",
                font=dict(size=10, color="#26a69a"),
                yshift=4,
            ))

    fig.update_layout(
        title=dict(text="Transfer Outcomes by Reason",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Transfer Reason", tickfont=dict(size=11)),
        yaxis=dict(title="Number of Transfers", gridcolor="#eeeeee"),
        barmode="stack",
        template="plotly_white",
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        margin=dict(l=10, r=20, t=55, b=60),
        plot_bgcolor="#fafafa",
        annotations=annotations,
    )
    return fig


def create_route_efficiency_chart(df, top_n=10):
    """Horizontal bar — top facility-pair routes ranked by net savings (savings − cost),
    with a secondary marker showing cost_benefit_score."""
    empty = go.Figure()
    empty.add_annotation(text="No route data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=380, template="plotly_white")
    if df.empty or "from_facility" not in df.columns or "to_facility" not in df.columns:
        return empty

    cost_col = "total_transfer_cost" if "total_transfer_cost" in df.columns else None
    sav_col  = "estimated_savings"   if "estimated_savings"  in df.columns else None
    cbs_col  = "cost_benefit_score"  if "cost_benefit_score" in df.columns else None
    qty_col  = "quantity"            if "quantity"           in df.columns else None
    if not cost_col or not sav_col:
        return empty

    agg = {cost_col: "sum", sav_col: "sum"}
    if cbs_col: agg[cbs_col] = "mean"
    if qty_col: agg[qty_col] = "sum"
    agg["order_id"] = "count"

    g = df.groupby(["from_facility", "to_facility"]).agg(agg).reset_index()
    g["net"]   = g[sav_col] - g[cost_col]
    g["route"] = g["from_facility"].str.replace(" Medical Center","").str.replace(" Community Hospital"," Hosp").str.replace(" Health Clinic"," Clinic").str.replace(" Regional Medical"," Regional") \
               + " → " + \
               g["to_facility"].str.replace(" Medical Center","").str.replace(" Community Hospital"," Hosp").str.replace(" Health Clinic"," Clinic").str.replace(" Regional Medical"," Regional")
    g = g.sort_values("net", ascending=True).tail(top_n)  # top N by net savings, ascending for horiz bar

    net_vals  = g["net"].tolist()
    colors    = ["#26a69a" if v >= 0 else "#ef5350" for v in net_vals]
    cost_vals = g[cost_col].tolist()
    sav_vals  = g[sav_col].tolist()
    qty_vals  = g[qty_col].tolist() if qty_col in g.columns else [0]*len(g)
    cnt_vals  = g["order_id"].tolist()
    cbs_vals  = [f"{v*100:.0f}%" for v in g[cbs_col].tolist()] if cbs_col in g.columns else ["-"]*len(g)

    fig = go.Figure(go.Bar(
        y=g["route"],
        x=net_vals,
        orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(color="white", width=0.8)),
        customdata=list(zip(cost_vals, sav_vals, qty_vals, cnt_vals, cbs_vals)),
        text=[f"  +${v:,.0f}" if v >= 0 else f"  -${abs(v):,.0f}" for v in net_vals],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Net savings: <b>$%{x:,.0f}</b><br>"
            "Transfer cost: $%{customdata[0]:,.0f}<br>"
            "Est. savings: $%{customdata[1]:,.0f}<br>"
            "Units moved: %{customdata[2]:,}<br>"
            "Transfers: %{customdata[3]}<br>"
            "Avg efficiency: %{customdata[4]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.add_vline(x=0, line_color="#546e7a", line_width=1.5,
                  annotation_text="Break-even", annotation_position="top",
                  annotation_font=dict(size=10, color="#546e7a"))

    fig.update_layout(
        title=dict(text=f"Top {top_n} Routes by Net Savings  (Savings − Transfer Cost)",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Net Savings ($)", gridcolor="#eeeeee", tickprefix="$"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        template="plotly_white",
        height=max(320, 60 + len(g) * 40),
        margin=dict(l=10, r=30, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_pending_savings_chart(df, n=12):
    """Top N medications with the most estimated savings still locked in PENDING status."""
    empty = go.Figure()
    empty.add_annotation(text="No pending transfers", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=340, template="plotly_white")
    if df.empty or "status" not in df.columns:
        return empty

    pending = df[df["status"] == "PENDING"].copy() if "status" in df.columns else df
    if pending.empty:
        return empty

    sav_col = "estimated_savings"  if "estimated_savings"  in df.columns else None
    qty_col = "quantity"            if "quantity"            in df.columns else None
    rat_col = "rationale"           if "rationale"           in df.columns else None
    cost_col= "total_transfer_cost" if "total_transfer_cost" in df.columns else None
    if not sav_col or "medication_name" not in df.columns:
        return empty

    agg = {sav_col: "sum"}
    if qty_col:  agg[qty_col]  = "sum"
    if cost_col: agg[cost_col] = "sum"
    if rat_col:  agg[rat_col]  = lambda x: x.mode().iloc[0] if len(x) > 0 else ""
    agg["order_id"] = "count"

    g = (pending.groupby("medication_name").agg(agg)
                .reset_index()
                .sort_values(sav_col, ascending=True)
                .tail(n))

    RATIONALE_COLORS = {
        "Expiration Management": "#ef6c00",
        "Shortage Prevention":   "#1565c0",
        "Demand Spike":          "#6a1b9a",
        "Regulatory":            "#2e7d32",
    }
    bar_colors = ([RATIONALE_COLORS.get(r, "#90a4ae") for r in g[rat_col]]
                  if rat_col in g.columns else ["#ff9800"] * len(g))

    sav_vals  = g[sav_col].tolist()
    qty_vals  = g[qty_col].tolist()  if qty_col  in g.columns else [0]*len(g)
    cost_vals = g[cost_col].tolist() if cost_col in g.columns else [0]*len(g)
    cnt_vals  = g["order_id"].tolist()
    rat_vals  = g[rat_col].tolist()  if rat_col  in g.columns else [""] * len(g)

    fig = go.Figure(go.Bar(
        y=g["medication_name"],
        x=sav_vals,
        orientation="h",
        marker=dict(color=bar_colors, opacity=0.88, line=dict(color="white", width=0.8)),
        customdata=list(zip(qty_vals, cost_vals, cnt_vals, rat_vals)),
        text=[f"  ${v:,.0f}" for v in sav_vals],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Savings at stake: <b>$%{x:,.0f}</b><br>"
            "Qty pending: %{customdata[0]:,} units<br>"
            "Transfer cost: $%{customdata[1]:,.0f}<br>"
            "Pending orders: %{customdata[2]}<br>"
            "Reason: %{customdata[3]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    # Legend patches
    for label, color in RATIONALE_COLORS.items():
        if rat_col and label in (rat_vals or []):
            fig.add_trace(go.Bar(x=[None], y=[None], orientation="h",
                                 name=label, marker=dict(color=color), showlegend=True))

    total_pending_sav = sum(sav_vals)
    fig.update_layout(
        title=dict(
            text=f"Pending Savings at Risk — Top {n} Medications  ·  <b>${total_pending_sav:,.0f}</b> uncaptured",
            font=dict(size=14, color="#2c3e50"), x=0,
        ),
        xaxis=dict(title="Estimated Savings ($)", gridcolor="#eeeeee", tickprefix="$"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        template="plotly_white",
        height=max(300, 60 + len(g) * 34),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    title="Reason:", font=dict(size=11)),
        margin=dict(l=10, r=20, t=65, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_route_med_breakdown(df):
    """Route view — for each medication on this route, stacked bar: COMPLETED|PENDING|REJECTED qty."""
    empty = go.Figure()
    empty.add_annotation(text="Select a route to see medication breakdown",
                         xref="paper", yref="paper", x=0.5, y=0.5,
                         showarrow=False, font=dict(size=12, color="#888"))
    empty.update_layout(height=360, template="plotly_white")
    if df.empty or "medication_name" not in df.columns or "status" not in df.columns:
        return empty

    qty_col = "quantity" if "quantity" in df.columns else None
    if not qty_col:
        return empty

    pivot = (df.groupby(["medication_name", "status"])[qty_col]
               .sum().unstack(fill_value=0).reset_index())

    STATUS_CFG = {
        "COMPLETED": ("Completed", "#4caf50"),
        "PENDING":   ("Pending",   "#ff9800"),
        "REJECTED":  ("Rejected",  "#ef5350"),
    }

    # Sort by total qty descending
    total_q = pivot[[c for c in ["COMPLETED","PENDING","REJECTED"] if c in pivot.columns]].sum(axis=1)
    pivot = pivot.assign(_total=total_q).sort_values("_total").drop(columns="_total")

    fig = go.Figure()
    for status, (label, color) in STATUS_CFG.items():
        if status not in pivot.columns:
            continue
        fig.add_trace(go.Bar(
            name=label,
            y=pivot["medication_name"],
            x=pivot[status],
            orientation="h",
            marker=dict(color=color, opacity=0.87),
            hovertemplate=f"<b>%{{y}}</b><br>{label}: <b>%{{x:,}} units</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Medication Mix on This Route",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Quantity (units)", gridcolor="#eeeeee"),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        barmode="stack",
        template="plotly_white",
        height=max(320, 60 + len(pivot) * 34),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        margin=dict(l=10, r=20, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_route_med_economics(df):
    """Route view — per-medication net value: savings − cost with count annotation."""
    empty = go.Figure()
    empty.add_annotation(text="Select a route to see economics",
                         xref="paper", yref="paper", x=0.5, y=0.5,
                         showarrow=False, font=dict(size=12, color="#888"))
    empty.update_layout(height=360, template="plotly_white")
    if df.empty or "medication_name" not in df.columns:
        return empty

    cost_col = "total_transfer_cost" if "total_transfer_cost" in df.columns else None
    sav_col  = "estimated_savings"   if "estimated_savings"   in df.columns else None
    qty_col  = "quantity"            if "quantity"            in df.columns else None
    if not cost_col or not sav_col:
        return empty

    agg = {cost_col: "sum", sav_col: "sum"}
    if qty_col: agg[qty_col] = "sum"
    agg["order_id"] = "count"

    g = df.groupby("medication_name").agg(agg).reset_index()
    g["net"] = g[sav_col] - g[cost_col]
    g = g.sort_values("net", ascending=True)

    net_vals  = g["net"].tolist()
    colors    = ["#26a69a" if v >= 0 else "#ef5350" for v in net_vals]
    cost_vals = g[cost_col].tolist()
    sav_vals  = g[sav_col].tolist()
    qty_vals  = g[qty_col].tolist() if qty_col in g.columns else [0]*len(g)
    cnt_vals  = g["order_id"].tolist()

    fig = go.Figure(go.Bar(
        y=g["medication_name"],
        x=net_vals,
        orientation="h",
        marker=dict(color=colors, opacity=0.88, line=dict(color="white", width=0.8)),
        customdata=list(zip(cost_vals, sav_vals, qty_vals, cnt_vals)),
        text=[f"  +${v:,.0f}" if v >= 0 else f"  -${abs(v):,.0f}" for v in net_vals],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Net value: <b>$%{x:,.0f}</b><br>"
            "Transfer cost: $%{customdata[0]:,.0f}<br>"
            "Savings: $%{customdata[1]:,.0f}<br>"
            "Units: %{customdata[2]:,}<br>"
            "Transfers: %{customdata[3]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    fig.add_vline(x=0, line_color="#546e7a", line_width=1.5,
                  annotation_text="Break-even",
                  annotation_position="top",
                  annotation_font=dict(size=10, color="#546e7a"))

    fig.update_layout(
        title=dict(text="Net Value per Medication  (Savings − Transfer Cost)",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Net ($)", gridcolor="#eeeeee", tickprefix="$"),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        template="plotly_white",
        height=max(320, 60 + len(g) * 34),
        margin=dict(l=10, r=30, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


# ============================================================================
# PAGE: HOME
# ============================================================================

def page_home():
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>🏥 PHARMA INVENTORY OPTIMIZATION PLATFORM</h1>", unsafe_allow_html=True)
    
    # Check API status
    api_healthy = get_health_check()
    status = "✅ Connected" if api_healthy else "❌ Disconnected"
    st.markdown(f"<p style='text-align: center; color: #666;'>API Status: {status} | {datetime.now().strftime('%b %d, %Y | %I:%M %p')}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dashboard selection cards
    st.markdown("<h2 style='text-align: center;'>📊 AVAILABLE DASHBOARDS</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;'>
                <h3>📈 EXPIRATION RISK</h3>
                <p>Monitor medications approaching expiration dates and optimize disposal/transfer decisions.</p>
                <p style='font-size: 12px; margin-top: 20px;'>Track at-risk inventory, timelines, and category trends</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Expiration Risk Dashboard", key="btn_expiration", use_container_width=True):
            st.session_state.page = "expiration"
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;'>
                <h3>💰 TRANSFER COORDINATION</h3>
                <p>Optimize cross-facility transfers and reduce waste through intelligent distribution.</p>
                <p style='font-size: 12px; margin-top: 20px;'>Identify savings, track transfers, manage compliance</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Transfer Dashboard", key="btn_transfer", use_container_width=True):
            st.session_state.page = "transfer"
            st.experimental_rerun()
    
    col3, col4 = st.columns([2, 1])
    
    with col3:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;'>
                <h3>🔮 DEMAND FORECAST</h3>
                <p>ML-powered demand predictions to prevent stockouts and optimize reordering.</p>
                <p style='font-size: 12px; margin-top: 20px;'>Forecast accuracy, anomalies, external signals</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("View Demand Forecast Dashboard", key="btn_demand", use_container_width=True):
            st.session_state.page = "demand"
            st.experimental_rerun()
    
    st.markdown("---")
    st.info("💡 **Tip:** Use the sidebar to navigate between dashboards or click any dashboard card above to get started.")

# ============================================================================
# PAGE: EXPIRATION RISK

    st.markdown("---")
    st.markdown("### 🎯 AI-Powered Strategic Insights")
    
    # Get all data for master strategy
    exp_data = get_api_data("/api/v1/powerbi/export/expiration-risk")
    trans_data = get_api_data("/api/v1/powerbi/export/transfer-coordination")
    dem_data = get_api_data("/api/v1/powerbi/export/demand-forecast")
    
    df_exp = pd.DataFrame(exp_data) if exp_data else pd.DataFrame()
    df_trans = pd.DataFrame(trans_data) if trans_data else pd.DataFrame()
    df_dem = pd.DataFrame(dem_data) if dem_data else pd.DataFrame()
    
    # Get master strategy
    strategy = get_master_strategy(df_exp, df_trans, df_dem)
    
    display_agent_header(
        "🎯 Executive Strategy Agent",
        strategy['agent_message'],
        icon="📊"
    )
    
    if strategy['recommendations']:
        display_agent_metrics(
            strategy['summary'],
            ['total_strategies', 'immediate_actions', 'efficiency_gain']
        )
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📌 Strategic Recommendations")
            for i, rec in enumerate(strategy['recommendations'], 1):
                st.write(f"{i}. {rec}")
        
        with col2:
            st.subheader("🎯 Priority Areas")
            for i, priority in enumerate(strategy['priorities'], 1):
                st.write(f"{i}. {priority}")

# ============================================================================

def page_expiration():
    st.markdown("<h1 class='dashboard-title'>📈 EXPIRATION RISK DASHBOARD</h1>", unsafe_allow_html=True)
    
    # Fetch data
    data = get_api_data("/api/v1/powerbi/export/expiration-risk")
    if not data or len(data) == 0:
        st.error("Unable to load expiration risk data")
        return
    
    df = pd.DataFrame(data)
    df_full = df.copy()  # preserve unfiltered data for charts that need full scope

    # ── EXPIRATION RISK FILTERS ───────────────────────────────────────────────
    with st.expander("🔍 Filters", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            horizon_map = {
                "🚨 Next 7 Days — Critical": 7,
                "📅 Next 30 Days — Standard": 30,
                "📆 Next 90 Days — Planning": 90,
                "🗓️ Next 180 Days — Extended": 180,
                "📋 All Data": 9999,
                "⚠️ Already Expired (Past)": "past",
                "🗓️ Custom Range": "custom",
            }
            horizon_label = st.selectbox(
                "Expiry Horizon",
                list(horizon_map.keys()),
                index=4,
                key="exp_horizon",
                help="How far ahead (or back) to look for expiring items"
            )
            horizon_val = horizon_map[horizon_label]
        with fcol2:
            if horizon_val == "custom":
                exp_custom = st.date_input(
                    "Custom Expiry Range",
                    value=(datetime.now().date(), (datetime.now() + timedelta(days=180)).date()),
                    key="exp_custom_range"
                )
            else:
                exp_custom = None
            # Risk Level filter — always rendered (conditional rendering causes
            # session-state KeyError when switching to the 'past' view).
            all_risk_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            if "exp_risk_level" not in st.session_state:
                st.session_state["exp_risk_level"] = all_risk_levels
            selected_levels_raw = st.multiselect(
                "Risk Level",
                all_risk_levels,
                key="exp_risk_level",
                help="Filter by risk classification"
            )
            # When viewing already-expired items, ignore the risk level filter
            selected_levels = [] if horizon_val == "past" else selected_levels_raw
        with fcol3:
            if "category" in df.columns:
                cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
                selected_cat = st.selectbox("Category", cats, key="exp_category")
            else:
                selected_cat = "All"

    # Apply expiration filters
    if "days_until_expiry" in df.columns:
        if horizon_val == "custom" and exp_custom:
            dates_list = list(exp_custom) if hasattr(exp_custom, "__iter__") and not isinstance(exp_custom, date) else [exp_custom]
            if len(dates_list) >= 2 and "expiry_date" in df.columns:
                exp_ts = pd.to_datetime(df["expiry_date"], errors="coerce")
                df = df[(exp_ts >= pd.Timestamp(dates_list[0])) & (exp_ts <= pd.Timestamp(dates_list[1]) + timedelta(days=1))]
        elif horizon_val == "past":
            df = df[df["days_until_expiry"] < 0]
        elif horizon_val == 9999:
            pass  # All Data: include everything (future + already expired)
        else:
            df = df[(df["days_until_expiry"] <= int(horizon_val)) & (df["days_until_expiry"] >= 0)]
    if "risk_level" in df.columns and selected_levels:
        # Always preserve already-expired items regardless of risk level filter
        expired_mask = df["days_until_expiry"] < 0 if "days_until_expiry" in df.columns else pd.Series(False, index=df.index)
        df = df[df["risk_level"].isin(selected_levels) | expired_mask]
    if selected_cat != "All" and "category" in df.columns:
        df = df[df["category"] == selected_cat]
    # ─────────────────────────────────────────────────────────────────────────

    # KPI Metrics Row
    col1, col2, col3 = st.columns(3)
    
    # Calculate metrics from actual data
    # Total at-risk value in selected range
    if 'batch_value' in df.columns:
        total_value = df['batch_value'].sum()
    else:
        total_value = 0
    
    # Count items and calculate overdue/soon-to-expire in filtered range
    items_count = len(df)
    
    if 'days_until_expiry' in df.columns:
        # Items already expired (negative days)
        overdue_items = len(df[df['days_until_expiry'] < 0])
        # Items approaching expiration within the selected horizon (not yet expired)
        approaching_items = len(df[df['days_until_expiry'] >= 0])
    else:
        overdue_items = 0
        approaching_items = 0

    # Build dynamic label based on selected horizon
    if horizon_val == "past":
        expiring_label = "ALREADY EXPIRED"
    elif horizon_val == "custom":
        expiring_label = "EXPIRING (CUSTOM)"
    elif horizon_val == 9999:
        expiring_label = "ALL FUTURE EXPIRY"
    else:
        expiring_label = f"EXPIRING 0-{horizon_val}D"

    render_metric_card(col1, f"${total_value:,.0f}", "RANGE VALUE", "in selected dates", is_critical=True)
    render_metric_card(col2, f"{approaching_items} items", expiring_label, "in selected range", is_warning=True)
    render_metric_card(col3, f"{overdue_items} items", "ALREADY EXPIRED", "in selected range", is_critical=True)
    
    st.markdown("---")

    # ── RISK TIMELINE ─ full width ──────────────────────────────────────────────────────────
    st.plotly_chart(
        create_timeline_chart(
            df,
            value_col='days_until_expiry',
            title=f"Expiration Risk Timeline — {horizon_label.split('—')[0].strip()}",
            horizon_val=horizon_val,
        ),
        use_container_width=True,
    )

    # ── SECONDARY CHARTS ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        if 'category' in df.columns:
            st.plotly_chart(
                create_category_pie_chart(df, title="Risk by Category"),
                use_container_width=True
            )
        else:
            st.info("Category data not available")
    with col2:
        st.plotly_chart(create_top_at_risk_medications(df, n=10), use_container_width=True)

    st.markdown("---")

    # Data Table
    st.subheader("📋 Inventory at Risk")
    
    # Select columns that exist in the actual data
    available_cols = ['batch_id', 'medication_name', 'facility_name', 'quantity_on_hand', 'days_until_expiry', 'risk_level', 'batch_value']
    display_cols = [col for col in available_cols if col in df.columns]
    df_display = df[display_cols]

    # Pagination
    page_size = 50
    total_records = len(df_display)
    total_pages = max(1, -(-total_records // page_size))  # ceil division
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1, key="exp_table_page")
    start_idx = (page_num - 1) * page_size
    end_idx = min(start_idx + page_size, total_records)

    st.dataframe(df_display.iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
    st.markdown(f"Showing {start_idx + 1}–{end_idx} of {total_records} records (Page {page_num}/{total_pages})")
    
    st.markdown("---")

    # AGENT INTEGRATION: Get inventory optimization recommendations
    agent_rec = get_expiration_agent_recommendations(df)
    render_ai_status_banner(
        active=True,
        detail=f"{agent_rec['summary'].get('transfers_recommended', 0)} transfers · {agent_rec['summary'].get('disposals_recommended', 0)} disposals recommended"
    )
    display_agent_header(
        "Inventory Optimization Agent",
        agent_rec['agent_message'],
        icon="🤖"
    )
    
    # Display summary metrics
    if agent_rec['summary']['total_at_risk'] > 0:
        display_agent_metrics(
            agent_rec['summary'],
            ['total_at_risk', 'transfers_recommended', 'disposals_recommended', 'potential_savings']
        )
        st.markdown("---")
    
    # Display detailed recommendations
    display_agent_recommendations_table(
        agent_rec['recommendations'],
        "Agent Transfer/Disposal Recommendations",
        source="RULE_BASED",
        show_reasoning=True,
    )

# ============================================================================
# PAGE: TRANSFER COORDINATION

    # ADVANCED AGENT: Cost-Benefit Analysis
    st.markdown("---")
    cost_analysis = get_cost_benefit_analysis(df)
    display_agent_header(
        "💵 Cost-Benefit Analysis",
        cost_analysis['agent_message'],
        icon="💰"
    )
    
    if cost_analysis['opportunities']:
        display_agent_metrics(
            cost_analysis['summary'],
            ['total_roi', 'payback_period', 'opportunities_count']
        )
        st.markdown("---")
        display_agent_recommendations_table(
            cost_analysis['opportunities'],
            "High-Value Transfer Opportunities",
            source="PROPHET",
        )

# ============================================================================

def page_transfer():
    st.markdown("<h1 class='dashboard-title'>💰 TRANSFER COORDINATION DASHBOARD</h1>", unsafe_allow_html=True)
    
    # Fetch data
    data = get_api_data("/api/v1/powerbi/export/transfer-coordination")
    if not data or len(data) == 0:
        st.error("Unable to load transfer data")
        return
    
    df = pd.DataFrame(data)

    # ── TRANSFER COORDINATION FILTERS ─────────────────────────────────────────
    with st.expander("🔍 Filters", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            window_map = {
                "📅 Next 7 Days": 7,
                "📅 Next 30 Days": 30,
                "📆 Next 90 Days": 90,
                "📆 Next 180 Days": 180,
                "🗓️ All Time": -1,
                "🗓️ Custom Range": -2,
            }
            window_label = st.selectbox(
                "Delivery Timeline",
                list(window_map.keys()),
                index=1,
                key="trans_window",
                help="Filter transfers by expected delivery date"
            )
            window_days = window_map[window_label]
            if window_days == -2:
                trans_custom = st.date_input(
                    "Custom Date Range",
                    value=(datetime.now().date(), (datetime.now() + timedelta(days=30)).date()),
                    key="trans_custom_range"
                )
            else:
                trans_custom = None
        with fcol2:
            all_actions = ["✅ APPROVE", "⏳ REVIEW", "❌ HOLD"]
            if "trans_action" not in st.session_state:
                st.session_state["trans_action"] = all_actions
            selected_actions = st.multiselect(
                "Action",
                all_actions,
                key="trans_action",
                help="Filter by ROI-based action recommendation"
            )
        with fcol3:
            min_savings = st.number_input(
                "Min. Estimated Savings ($)",
                min_value=0, value=0, step=500,
                key="trans_min_savings",
                help="Hide transfers below this savings threshold"
            )
            compliance_only = st.checkbox(
                "Compliance-Cleared Only",
                value=False,
                key="trans_compliance",
                help="Only show transfers with OK compliance status"
            )

    # Apply transfer filters — use expected_delivery_date (has 177 unique days)
    date_cols = ["expected_delivery_date", "created_date", "updated_at"]
    if window_days > 0:
        # Show records with delivery date in the NEXT window_days from today
        now = pd.Timestamp(datetime.now()).normalize()
        cutoff_end = now + timedelta(days=window_days)
        for col in date_cols:
            if col in df.columns:
                ts = pd.to_datetime(df[col], errors="coerce")
                if ts.notna().any():
                    if ts.dt.tz is not None:
                        ts = ts.dt.tz_localize(None)
                    df = df[ts.isna() | ((ts >= now) & (ts <= cutoff_end))]
                    break
    elif window_days == -2 and trans_custom:
        dates_list = list(trans_custom) if hasattr(trans_custom, "__iter__") and not isinstance(trans_custom, date) else [trans_custom]
        if len(dates_list) >= 2:
            for col in date_cols:
                if col in df.columns:
                    ts = pd.to_datetime(df[col], errors="coerce")
                    if ts.notna().any():
                        if ts.dt.tz is not None:
                            ts = ts.dt.tz_localize(None)
                        s, e = pd.Timestamp(dates_list[0]), pd.Timestamp(dates_list[1]) + timedelta(days=1)
                        df = df[ts.isna() | ((ts >= s) & (ts < e))]
                        break
    # Compute derived action & priority columns for filtering
    _cost2    = pd.to_numeric(df['total_transfer_cost'] if 'total_transfer_cost' in df.columns else 0, errors='coerce').fillna(0)
    _savings2 = pd.to_numeric(df['estimated_savings']   if 'estimated_savings'   in df.columns else 0, errors='coerce').fillna(0)
    _comp2    = df['compliance_status'].astype(str) if 'compliance_status' in df.columns else pd.Series('OK', index=df.index)
    _roi2     = _savings2 / _cost2.replace(0, float('nan'))
    _action2  = pd.Series('❌ HOLD', index=df.index)
    _action2[_roi2 > 2] = '⏳ REVIEW'
    _action2[(_roi2 > 5) & _comp2.isin(['OK', '', 'None', 'nan'])] = '✅ APPROVE'
    if selected_actions:
        df = df[_action2.isin(selected_actions)]
    if "estimated_savings" in df.columns and min_savings > 0:
        df = df[df["estimated_savings"] >= min_savings]
    if compliance_only and "compliance_status" in df.columns:
        df = df[df["compliance_status"] == "OK"]
    # ─────────────────────────────────────────────────────────────────────────

    # KPI Metrics Row
    col1, col2, col3 = st.columns(3)

    # Calculate from actual transfer data
    potential_savings = df["estimated_savings"].sum()      if "estimated_savings"      in df.columns else 0
    total_cost        = df["total_transfer_cost"].sum()    if "total_transfer_cost"    in df.columns else 0
    pending_units     = (df.loc[df["status"] == "PENDING", "quantity"].sum()
                         if ("status" in df.columns and "quantity" in df.columns) else 0)
    avg_efficiency    = (df["cost_benefit_score"].mean() * 100
                         if "cost_benefit_score" in df.columns and df["cost_benefit_score"].notna().any()
                         else None)
    completed_count   = int(df[df["status"] == "COMPLETED"].shape[0]) if "status" in df.columns else 0
    total_count       = max(len(df), 1)

    # Trend: savings vs cost (ROI)
    roi = (potential_savings / total_cost * 100) if total_cost > 0 else 0
    savings_trend = f"ROI {roi:.0f}%  ({completed_count}/{total_count} completed)"

    # KPI 3: avg efficiency score or pending units label
    if avg_efficiency is not None:
        kpi3_val   = f"{avg_efficiency:.0f}%"
        kpi3_label = "AVG EFFICIENCY SCORE"
        kpi3_trend = f"{completed_count} transfers completed"
    else:
        kpi3_val   = f"{pending_units:,} units"
        kpi3_label = "UNITS PENDING TRANSFER"
        kpi3_trend = f"{completed_count} transfers completed"

    render_metric_card(col1, f"${potential_savings:,.0f}", "POTENTIAL SAVINGS", savings_trend)
    render_metric_card(col2, f"${total_cost:,.0f}", "TOTAL TRANSFER COST", f"{total_count} transfers in window", is_warning=True)
    render_metric_card(col3, kpi3_val, kpi3_label, kpi3_trend, is_critical=(avg_efficiency is not None and avg_efficiency < 50))

    st.markdown("---")

    # ── Route drill-down selector ────────────────────────────────────────────
    # All facilities appearing anywhere in the transfer data (from or to)
    all_facilities = sorted(set(
        (df["from_facility"].dropna().tolist() if "from_facility" in df.columns else []) +
        (df["to_facility"].dropna().tolist()   if "to_facility"   in df.columns else [])
    ))
    all_from = all_facilities
    all_to   = all_facilities

    # Handle clear-route flag: delete widget keys BEFORE they render (safe in 1.24)
    if st.session_state.pop("route_clear_pending", False):
        st.session_state.pop("route_from", None)
        st.session_state.pop("route_to",   None)

    rc1, rc2, rc3 = st.columns([2, 2, 1])
    with rc1:
        sel_from = st.selectbox(
            "🔀 Route — From Facility",
            ["All Facilities"] + all_from,
            key="route_from",
            help="Select a source facility to highlight its transfers"
        )
    with rc2:
        # Always offer all facilities as destinations — not just ones with existing
        # transfer records — so every possible route can be selected and highlighted.
        # Exclude the currently selected "from" facility to avoid self-routes.
        if sel_from != "All Facilities":
            to_options = [f for f in all_to if f != sel_from]
        else:
            to_options = all_to
        full_to_opts = ["All Facilities"] + to_options
        # If stored route_to is no longer valid for the current sel_from, reset it
        _stored_to = st.session_state.get("route_to", "All Facilities")
        if _stored_to not in full_to_opts:
            st.session_state["route_to"] = "All Facilities"
        sel_to = st.selectbox(
            "🏥 Route — To Facility",
            full_to_opts,
            key="route_to",
            help="Select a destination facility"
        )
    with rc3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("✖ Clear Route", key="route_clear", use_container_width=True):
            st.session_state["route_clear_pending"] = True
            st.experimental_rerun()

    # Build route-filtered dataframe for cost breakdown / table
    route_active = sel_from != "All Facilities" or sel_to != "All Facilities"
    df_route = df.copy()
    if sel_from != "All Facilities" and "from_facility" in df_route.columns:
        df_route = df_route[df_route["from_facility"] == sel_from]
    if sel_to != "All Facilities" and "to_facility" in df_route.columns:
        df_route = df_route[df_route["to_facility"] == sel_to]

    highlight_pair = None
    if sel_from != "All Facilities" or sel_to != "All Facilities":
        highlight_pair = (sel_from, sel_to)

    if route_active:
        route_label = f"{sel_from if sel_from != 'All Facilities' else 'Any'} → {sel_to if sel_to != 'All Facilities' else 'Any'}"
        st.info(f"📍 Showing route: **{route_label}** — {len(df_route)} transfers  "
                f"| Total Cost: **${df_route['total_transfer_cost'].sum():,.0f}**  "
                f"| Savings: **${df_route['estimated_savings'].sum():,.0f}**",
                icon=None)

    # ── Visualizations ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_facility_flow_chart(df), use_container_width=True)

    with col2:
        st.plotly_chart(create_transfer_sankey(df, highlight_pair=highlight_pair), use_container_width=True)

    st.markdown("---")

    if route_active:
        # Route view: medication mix + per-drug economics for that specific route
        rv1, rv2 = st.columns(2)
        with rv1:
            st.plotly_chart(create_route_med_breakdown(df_route), use_container_width=True)
        with rv2:
            st.plotly_chart(create_route_med_economics(df_route), use_container_width=True)
    else:
        # Global view panel 1: best/worst routes by net savings
        st.plotly_chart(create_route_efficiency_chart(df), use_container_width=True)
        st.markdown("---")
        # Global view panel 2: top medications by transfer volume
        st.plotly_chart(create_top_transfer_medications(df), use_container_width=True)
        st.markdown("---")
        # Global view panel 3: uncaptured savings still in PENDING
        st.plotly_chart(create_pending_savings_chart(df), use_container_width=True)

    st.markdown("---")

    # Transfer Proposals Table — also filters to selected route
    st.subheader("📋 Transfer Proposals" + (f" — {route_label}" if route_active else ""))

    display_df = df_route if route_active else df
    if len(display_df) > 0:
        # ── Action summary bar (ROI-based) ───────────────────────────────────
        if 'total_transfer_cost' in display_df.columns and 'estimated_savings' in display_df.columns:
            _c = pd.to_numeric(display_df['total_transfer_cost'], errors='coerce').fillna(0)
            _s = pd.to_numeric(display_df['estimated_savings'],   errors='coerce').fillna(0)
            _comp = display_df['compliance_status'].astype(str) if 'compliance_status' in display_df.columns else pd.Series('OK', index=display_df.index)
            _roi = _s / _c.replace(0, float('nan'))
            _action = pd.Series('❌ HOLD', index=display_df.index)
            _action[_roi > 2] = '⏳ REVIEW'
            _action[(_roi > 5) & _comp.isin(['OK', '', 'None', 'nan'])] = '✅ APPROVE'
            approve_n = int((_action == '✅ APPROVE').sum())
            review_n  = int((_action == '⏳ REVIEW').sum())
            hold_n    = int((_action == '❌ HOLD').sum())

        # Filter out 0-quantity proposals — these are data artifacts where the
        # consumption rate was ~0 so transfer qty = 0 × 14 days = 0.
        zero_qty_count = int((display_df["quantity"] == 0).sum()) if "quantity" in display_df.columns else 0
        display_df_valid = display_df[display_df["quantity"] > 0] if "quantity" in display_df.columns else display_df

        PAGE_SIZE = 20
        total_records = len(display_df_valid)
        total_pages = max(1, (total_records + PAGE_SIZE - 1) // PAGE_SIZE)

        if 'trans_proposals_page' not in st.session_state:
            st.session_state['trans_proposals_page'] = 0
        # Reset page if it's out of range (e.g. after filter change)
        if st.session_state['trans_proposals_page'] >= total_pages:
            st.session_state['trans_proposals_page'] = 0
        page = st.session_state['trans_proposals_page']

        page_df = display_df_valid.iloc[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

        transfers_data = []
        for idx, row in page_df.iterrows():
            cost    = float(row.get('total_transfer_cost', 0) or 0)
            savings = float(row.get('estimated_savings', 0) or 0)
            compliance = str(row.get('compliance_status', 'OK') or 'OK')
            roi = savings / cost if cost > 0 else 0
            if roi > 5 and compliance in ('OK', '', 'None'):
                action = "✅ APPROVE"
                priority_val = "HIGH"
            elif roi > 2:
                action = "⏳ REVIEW"
                priority_val = "MEDIUM"
            else:
                action = "❌ HOLD"
                priority_val = "LOW"
            transfers_data.append({
                'From':      row.get('from_facility', 'Unknown'),
                'To':        row.get('to_facility', 'Unknown'),
                'Medication': row.get('medication_name', 'Unknown'),
                'Qty':       int(row.get('quantity', 0)),
                'Cost':      f"${cost:,.0f}",
                'Savings':   f"${savings:,.0f}",
                'ROI':       f"{roi:.1f}x",
                'Action':    action,
                'Priority':  priority_val,
                'Rationale': str(row.get('rationale', '—')),
            })
        transfers = pd.DataFrame(transfers_data)
        col_order = ['From','To','Medication','Qty','Cost','Savings','ROI','Action','Priority','Rationale']
        transfers = transfers[[c for c in col_order if c in transfers.columns]]
        st.dataframe(transfers, use_container_width=True, hide_index=True)

        # Pagination controls
        start_rec = page * PAGE_SIZE + 1
        end_rec = min((page + 1) * PAGE_SIZE, total_records)
        pcol1, pcol2, pcol3 = st.columns([1, 3, 1])
        with pcol1:
            if st.button("◀ Prev", disabled=(page == 0), key="trans_page_prev"):
                st.session_state['trans_proposals_page'] -= 1
                st.experimental_rerun()
        with pcol2:
            note = f"Showing {start_rec}–{end_rec} of {total_records} transfers  (page {page+1} of {total_pages})"
            if zero_qty_count:
                note += f"  ·  {zero_qty_count} zero-qty hidden"
            st.markdown(f"<div style='text-align:center; padding-top:6px; color:#888; font-size:0.85rem;'>{note}</div>", unsafe_allow_html=True)
        with pcol3:
            if st.button("Next ▶", disabled=(page >= total_pages - 1), key="trans_page_next"):
                st.session_state['trans_proposals_page'] += 1
                st.experimental_rerun()
    else:
        st.info("No transfers found for this route / filter combination")
    
    st.markdown("---")

    # AGENT INTEGRATION: Get supply chain transfer recommendations
    agent_rec = get_transfer_agent_recommendations(df)
    display_agent_header(
        "Supply Chain Coordination Agent — Actionable Opportunities",
        agent_rec['agent_message'] + "  ·  Classifies valid transfers by ROI to show which to approve, review, or hold.",
        icon="🚚"
    )
    
    # ROI Action breakdown — counts from actual filtered data
    _fc = pd.to_numeric(df['total_transfer_cost'] if 'total_transfer_cost' in df.columns else pd.Series(0, index=df.index), errors='coerce').fillna(0)
    _fs = pd.to_numeric(df['estimated_savings']   if 'estimated_savings'   in df.columns else pd.Series(0, index=df.index), errors='coerce').fillna(0)
    _fcomp = df['compliance_status'].astype(str) if 'compliance_status' in df.columns else pd.Series('OK', index=df.index)
    _froi  = _fs / _fc.replace(0, float('nan'))
    _faction = pd.Series('❌ HOLD', index=df.index)
    _faction[_froi > 2] = '⏳ REVIEW'
    _faction[(_froi > 5) & _fcomp.isin(['OK', '', 'None', 'nan'])] = '✅ APPROVE'
    approve_count = int((_faction == '✅ APPROVE').sum())
    review_count  = int((_faction == '⏳ REVIEW').sum())
    hold_count    = int((_faction == '❌ HOLD').sum())
    if len(df) > 0:
        total_savings = f"${_fs.sum():,.0f}" if 'estimated_savings' in df.columns else '$0'
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("✅ APPROVE", approve_count,  help="ROI > 5x and compliance OK")
        mc2.metric("⏳ REVIEW",  review_count,   help="ROI between 2x – 5x")
        mc3.metric("❌ HOLD",    hold_count,      help="ROI < 2x")
        mc4.metric("💰 Total Potential Savings", total_savings)
        st.caption("✅ APPROVE — ROI > 5x and compliance OK  ·  ⏳ REVIEW — ROI between 2x–5x  ·  ❌ HOLD — ROI < 2x")

# ============================================================================
# DEMAND FORECAST CHART HELPERS
# ============================================================================

def create_demand_pipeline_chart(df, selected_col="predicted_demand_30d"):
    """Grouped bar — predicted demand across 3 horizons (7d/14d/30d) per medication category.
    The selected_col horizon is highlighted; others are shown dimmed for context."""
    empty = go.Figure()
    empty.add_annotation(text="No forecast data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=340, template="plotly_white")
    if df.empty or "category" not in df.columns:
        return empty

    horizons = [
        ("predicted_demand_7d",  "7-Day",  "#42a5f5"),
        ("predicted_demand_14d", "14-Day", "#7e57c2"),
        ("predicted_demand_30d", "30-Day", "#ef5350"),
    ]
    available = [(col, lbl, clr) for col, lbl, clr in horizons if col in df.columns]
    if not available:
        return empty

    agg = {col: "sum" for col, _, _ in available}
    agg["medication_name"] = "nunique"
    g = df.groupby("category").agg(agg).reset_index()

    fig = go.Figure()
    for col, label, color in available:
        is_selected = (col == selected_col)
        opacity = 0.92 if is_selected else 0.35
        vals = g[col].tolist()
        fig.add_trace(go.Bar(
            name=label + (" ◀ selected" if is_selected else ""),
            x=g["category"],
            y=vals,
            marker=dict(color=color, opacity=opacity),
            text=[f"{int(v):,}" if v > 0 and is_selected else "" for v in vals],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>" + label + " demand: <b>%{y:,} units</b><extra></extra>",
        ))

    selected_label = next((lbl for col, lbl, _ in horizons if col == selected_col), "")
    fig.update_layout(
        title=dict(text=f"Predicted Demand Pipeline by Category  — <b>{selected_label}</b> selected  (others dimmed)",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title="Medication Category", tickfont=dict(size=11)),
        yaxis=dict(title="Predicted Units", gridcolor="#eeeeee"),
        barmode="group",
        template="plotly_white",
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1),
        margin=dict(l=10, r=20, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_top_demand_medications(df, horizon_col="predicted_demand_30d", n=12):
    """Top N medications by predicted demand for the selected horizon, coloured by urgency."""
    empty = go.Figure()
    empty.add_annotation(text="No medication forecast data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=380, template="plotly_white")
    if df.empty or "medication_name" not in df.columns:
        return empty

    dem_col = horizon_col if horizon_col in df.columns else "predicted_demand_30d"
    if dem_col not in df.columns:
        return empty

    conf_col = "forecast_confidence"  if "forecast_confidence"  in df.columns else None
    mape_col = "model_accuracy_mape"  if "model_accuracy_mape"  in df.columns else None
    urg_col  = "urgency"              if "urgency"              in df.columns else None
    cat_col  = "category"             if "category"             in df.columns else None
    act_col  = "suggested_action"     if "suggested_action"     in df.columns else None

    agg = {dem_col: "sum"}
    if conf_col: agg[conf_col] = "mean"
    if mape_col: agg[mape_col] = "mean"
    if urg_col:  agg[urg_col]  = lambda x: x.mode().iloc[0] if len(x) > 0 else "MEDIUM"
    if cat_col:  agg[cat_col]  = "first"
    if act_col:  agg[act_col]  = lambda x: x.mode().iloc[0] if len(x) > 0 else "MONITOR"

    g = (df.groupby("medication_name").agg(agg)
           .reset_index()
           .sort_values(dem_col, ascending=True)
           .tail(n))

    URG_COLORS = {"CRITICAL": "#c62828", "HIGH": "#ef6c00",
                  "MEDIUM": "#fbc02d",   "LOW": "#66bb6a"}
    bar_colors = ([URG_COLORS.get(u, "#90a4ae") for u in g[urg_col]]
                  if urg_col in g.columns else ["#42a5f5"] * len(g))

    dem_vals  = g[dem_col].tolist()
    cat_vals  = g[cat_col].tolist() if cat_col in g.columns else ["-"]*len(g)
    act_vals  = g[act_col].tolist() if act_col in g.columns else ["-"]*len(g)

    days_label = horizon_col.replace("predicted_demand_", "").replace("d", "-Day")
    fig = go.Figure(go.Bar(
        y=g["medication_name"],
        x=dem_vals,
        orientation="h",
        marker=dict(color=bar_colors, opacity=0.87, line=dict(color="white", width=0.8)),
        customdata=list(zip(cat_vals, act_vals)),
        text=[f"  {v:,} units" if v > 0 else "  No forecast" for v in dem_vals],
        textposition="inside", insidetextanchor="start",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Predicted demand: <b>%{x:,} units</b><br>"
            "Category: %{customdata[0]}<br>"
            "Action: %{customdata[1]}"
            "<extra></extra>"
        ),
        showlegend=False,
    ))

    # Urgency legend
    for urg, color in URG_COLORS.items():
        if urg_col and urg in (g[urg_col].tolist() if urg_col in g.columns else []):
            fig.add_trace(go.Bar(x=[None], y=[None], orientation="h",
                                 name=urg, marker=dict(color=color), showlegend=True))

    fig.update_layout(
        title=dict(text=f"Top {n} Medications — {days_label} Forecast  (coloured by urgency)",
                   font=dict(size=14, color="#2c3e50"), x=0),
        xaxis=dict(title=f"Predicted Demand ({days_label})", gridcolor="#eeeeee"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        template="plotly_white",
        height=max(320, 60 + len(g) * 34),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                    title="Urgency:", font=dict(size=11)),
        margin=dict(l=10, r=20, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    return fig


def create_model_confidence_chart(df):
    """Heatmap-style: avg forecast_confidence and model_accuracy_mape per category × model_type."""
    from plotly.subplots import make_subplots

    empty = go.Figure()
    empty.add_annotation(text="No model data", xref="paper", yref="paper",
                         x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#888"))
    empty.update_layout(height=300, template="plotly_white")
    if df.empty:
        return empty

    conf_col = "forecast_confidence" if "forecast_confidence" in df.columns else None
    mape_col = "model_accuracy_mape" if "model_accuracy_mape" in df.columns else None
    cat_col  = "category"            if "category"            in df.columns else None
    mod_col  = "model_type"          if "model_type"          in df.columns else None
    if not conf_col and not mape_col:
        return empty

    group_col = mod_col if mod_col and df[mod_col].nunique() > 1 else cat_col
    if not group_col:
        return empty

    agg = {}
    if conf_col: agg[conf_col] = "mean"
    if mape_col: agg[mape_col] = "mean"
    agg["medication_name"] = "nunique"
    g = df.groupby(group_col).agg(agg).reset_index()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Avg Forecast Confidence (%)", "Avg Model Error (MAPE %)"],
        column_widths=[0.5, 0.5],
    )

    if conf_col:
        conf_vals = [v * 100 for v in g[conf_col]]
        fig.add_trace(go.Bar(
            x=g[group_col], y=conf_vals,
            marker=dict(
                color=conf_vals,
                colorscale=[[0, "#ef5350"], [0.7, "#fbc02d"], [1.0, "#4caf50"]],
                cmin=0, cmax=100, showscale=False,
            ),
            text=[f"{v:.0f}%" for v in conf_vals],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Confidence: %{y:.1f}%<extra></extra>",
            showlegend=False,
        ), row=1, col=1)

    if mape_col:
        mape_vals = [v * 100 for v in g[mape_col]]
        mape_colors = ["#4caf50" if v <= 10 else "#fbc02d" if v <= 20 else "#ef5350"
                       for v in mape_vals]
        fig.add_trace(go.Bar(
            x=g[group_col], y=mape_vals,
            marker=dict(color=mape_colors, opacity=0.88),
            text=[f"{v:.1f}%" for v in mape_vals],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>MAPE: %{y:.1f}% (lower = better)<extra></extra>",
            showlegend=False,
        ), row=1, col=2)
        # Target line at 15%
        fig.add_hline(y=15, line_dash="dash", line_color="#546e7a", line_width=1.5,
                      annotation_text="15% target",
                      annotation_font=dict(size=10, color="#546e7a"),
                      row=1, col=2)

    fig.update_layout(
        title=dict(text="Model Performance by " + group_col.replace("_", " ").title(),
                   font=dict(size=14, color="#2c3e50"), x=0),
        template="plotly_white",
        height=320,
        margin=dict(l=10, r=20, t=55, b=40),
        plot_bgcolor="#fafafa",
    )
    fig.update_yaxes(gridcolor="#eeeeee", ticksuffix="%")
    return fig


# ============================================================================
# PAGE: DEMAND FORECAST
# ============================================================================

def page_demand():
    st.markdown("<h1 class='dashboard-title'>🔮 DEMAND FORECAST DASHBOARD</h1>", unsafe_allow_html=True)

    data = get_api_data("/api/v1/powerbi/export/demand-forecast")
    if not data or len(data) == 0:
        st.error("Unable to load demand forecast data")
        return
    df = pd.DataFrame(data)

    # ── FILTERS ───────────────────────────────────────────────────────────────
    # Use fixed, stable option lists to avoid Streamlit session-state KeyErrors
    # that occur when data-driven option lists change between reruns.
    with st.expander("🔍 Filters", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            horizon_opts = {
                "7 Days — Short-term":  ("predicted_demand_7d",  7),
                "14 Days — Bi-weekly": ("predicted_demand_14d", 14),
                "30 Days — Monthly":   ("predicted_demand_30d", 30),
            }
            # Always show all 3 options so the selectbox structure never changes
            # between reruns (prevents session-state KeyError).
            dem_horizon = st.selectbox(
                "Forecast Horizon",
                list(horizon_opts.keys()),
                index=2,           # default: 30-Day
                key="dem_horizon",
            )
            # Fallback: if the chosen column is missing, use the first available
            _col, _days = horizon_opts[dem_horizon]
            if _col not in df.columns:
                _col = next((c for c in ("predicted_demand_7d", "predicted_demand_14d",
                                         "predicted_demand_30d") if c in df.columns),
                            "predicted_demand_30d")
                _days = {"predicted_demand_7d": 7, "predicted_demand_14d": 14,
                         "predicted_demand_30d": 30}.get(_col, 30)
            forecast_col, forecast_days = _col, _days
        with fcol2:
            all_urgencies = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            # Initialise session state BEFORE the widget so Streamlit never
            # falls back to a default that resets user selections on reruns.
            if "dem_urgency" not in st.session_state:
                st.session_state["dem_urgency"] = all_urgencies
            selected_urgencies = st.multiselect(
                "Urgency Level", all_urgencies, key="dem_urgency")
        with fcol3:
            cats = ["All"] + (sorted(df["category"].dropna().unique().tolist())
                              if "category" in df.columns else [])
            _stored_cat = st.session_state.get("dem_category", "All")
            _cat_idx = cats.index(_stored_cat) if _stored_cat in cats else 0
            dem_category = st.selectbox("Medication Category", cats,
                                        index=_cat_idx, key="dem_category")

    # Apply filters
    if "urgency" in df.columns and selected_urgencies:
        df = df[df["urgency"].isin(selected_urgencies)]
    if dem_category != "All" and "category" in df.columns:
        df = df[df["category"] == dem_category]
    # ─────────────────────────────────────────────────────────────────────────

    if df.empty:
        st.warning("No data matches the current filters.")
        return

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    kc1, kc2, kc3, kc4 = st.columns(4)

    total_meds = df["medication_name"].nunique() if "medication_name" in df.columns else len(df)
    total_cats = df["category"].nunique()         if "category"        in df.columns else 0

    avg_conf   = (df["forecast_confidence"].mean() * 100
                  if "forecast_confidence" in df.columns and df["forecast_confidence"].notna().any()
                  else None)
    avg_mape   = (df["model_accuracy_mape"].mean() * 100
                  if "model_accuracy_mape"  in df.columns and df["model_accuracy_mape"].notna().any()
                  else None)
    anomaly_count = (int(df["anomalies_detected"].astype(int).sum())
                     if "anomalies_detected" in df.columns else 0)
    critical_count = (int((df["urgency"] == "CRITICAL").sum())
                      if "urgency" in df.columns else 0)
    high_count     = (int((df["urgency"] == "HIGH").sum())
                      if "urgency" in df.columns else 0)

    conf_str = f"{avg_conf:.0f}%" if avg_conf is not None else "N/A"
    mape_str = f"{avg_mape:.1f}%" if avg_mape is not None else "N/A"
    conf_trend = "Target: >85% ✅" if avg_conf and avg_conf >= 85 else "across all forecast models"
    mape_trend = "Good (<15%) ✅" if avg_mape and avg_mape <= 15 else "mean absolute % error"

    # Card 1: total forecasted units for the selected horizon — changes with the horizon filter
    _horizon_label = forecast_col.replace("predicted_demand_", "").upper()   # e.g. "7D"
    total_demand = (int(df[forecast_col].sum())
                    if forecast_col in df.columns else 0)
    demand_str = f"{total_demand:,}"
    demand_sub = f"{_horizon_label} horizon · {total_meds:,} medications across {total_cats} categories"

    render_metric_card(kc1, demand_str, f"TOTAL FORECAST DEMAND ({_horizon_label})", demand_sub)
    render_metric_card(kc2, conf_str, "AVG FORECAST CONFIDENCE", conf_trend)
    render_metric_card(kc3, mape_str, "MODEL ERROR (MAPE)", mape_trend)
    render_metric_card(kc4, str(anomaly_count),
                       "HISTORICAL DEMAND ANOMALIES",
                       f"irregular data points · {critical_count} critical meds · {high_count} high meds",
                       is_critical=(anomaly_count > 0))

    st.markdown("---")

    # ── Panel 1: Demand Pipeline by Category (full width) ─────────────────────
    st.plotly_chart(create_demand_pipeline_chart(df, forecast_col), use_container_width=True)
    st.markdown("---")

    # ── Panel 2: Top Medications ──────────────────────────────────────────────
    st.plotly_chart(create_top_demand_medications(df, forecast_col), use_container_width=True)
    st.markdown("---")

    # ── Agent Integration ─────────────────────────────────────────────────────
    agent_rec = get_demand_agent_insights(df, forecast_col)
    display_agent_header("Demand Forecasting Agent", agent_rec["agent_message"], icon="📊")
    display_agent_metrics(agent_rec["summary"],
                          ["forecast_accuracy", "recommendations_count", "historical_anomalies"])
    st.markdown("---")

    if agent_rec.get("actionable_recommendations"):
        st.subheader("💡 AI Recommendations")
        st.dataframe(pd.DataFrame(agent_rec["actionable_recommendations"]),
                     use_container_width=True, hide_index=True)
        st.markdown("---")

    if agent_rec.get("high_risk_medications"):
        st.subheader("🚨 High-Risk Medications (Stockout Risk)")
        st.dataframe(pd.DataFrame(agent_rec["high_risk_medications"]),
                     use_container_width=True, hide_index=True)
        st.markdown("---")

    alerts = get_predictive_alerts(df)
    display_agent_header("🔔 Predictive Alerts", alerts["agent_message"], icon="⚙️")
    if alerts.get("alerts"):
        display_agent_metrics(alerts["summary"], ["alert_count", "high_priority"])
        st.markdown("---")
        st.subheader("📋 System Alerts")
        st.dataframe(pd.DataFrame(alerts["alerts"]), use_container_width=True, hide_index=True)

def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📊 NAVIGATION")
        
        if st.button("🏠 HOME", use_container_width=True, key="nav_home"):
            st.session_state.page = 'home'
            st.experimental_rerun()
        
        st.markdown("---")
        st.markdown("**DASHBOARDS**")
        
        if st.button("📈 Expiration Risk", use_container_width=True, key="nav_exp"):
            st.session_state.page = 'expiration'
            st.experimental_rerun()
        
        if st.button("💰 Transfer Coordination", use_container_width=True, key="nav_trans"):
            st.session_state.page = 'transfer'
            st.experimental_rerun()
        
        if st.button("🔮 Demand Forecast", use_container_width=True, key="nav_dem"):
            st.session_state.page = 'demand'
            st.experimental_rerun()
        
        st.markdown("---")
        # Get actual facility names from session (set by API on first load)
        if 'facility_list' not in st.session_state:
            st.session_state.facility_list = ["All", "Central Valley Hospital", "Downtown Medical Center", "Eastside Regional Medical", "Northgate Community Hospital", "Suburban Health Clinic"]
        
        facility_options = st.session_state.facility_list
        
        # Safe facility initialization and selectbox
        if 'facility' not in st.session_state:
            st.session_state.facility = facility_options[0]  # Default to 'All'
        
        # Get current facility index, defaulting to 0 if not found
        try:
            current_facility = st.session_state.facility
            facility_index = facility_options.index(current_facility) if current_facility in facility_options else 0
        except (AttributeError, ValueError, IndexError):
            facility_index = 0
        
        st.session_state.facility = st.selectbox("Facility", facility_options, index=facility_index)
        
        st.markdown("---")
        api_status = "✅ Connected" if get_health_check() else "❌ Disconnected"
        st.markdown(f"**API Status:** {api_status}")
    
    # Page routing
    if st.session_state.page == 'home':
        page_home()
    elif st.session_state.page == 'expiration':
        page_expiration()
    elif st.session_state.page == 'transfer':
        page_transfer()
    elif st.session_state.page == 'demand':
        page_demand()

if __name__ == "__main__":
    main()
