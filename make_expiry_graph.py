"""Expiry Risk Detection Dashboard — single comprehensive graph."""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

DATA = './data-generation/synthetic_data/'
inv = pd.read_csv(DATA + 'inventory.csv')
con = pd.read_csv(DATA + 'consumption.csv')
med = pd.read_csv(DATA + 'medications.csv')

# ── value lookup ──
avg_p = con.groupby('medication_id')['unit_price'].mean()
iv = inv.merge(avg_p.rename('ap'), left_on='medication_id', right_index=True, how='left')
iv['val'] = iv['quantity_on_hand'] * iv['ap']

risk_order  = ['EXPIRED', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
risk_colors = ['#212121', '#e53935', '#fb8c00', '#fdd835', '#43a047']
rc_map      = dict(zip(risk_order, risk_colors))

rc  = inv['risk_level'].value_counts().reindex(risk_order).fillna(0).astype(int)
rv  = iv.groupby('risk_level')['val'].sum().reindex(risk_order).fillna(0)
total_val   = iv['val'].sum()
at_risk_val = rv[['EXPIRED', 'CRITICAL', 'HIGH']].sum()

# ── monthly expiry forecast (next 13 months) ──
inv['exp_date'] = pd.to_datetime(inv['expiration_date'])
near = inv[inv['days_to_expiry'].between(-6, 395)].copy()
near['exp_month'] = near['exp_date'].dt.to_period('M').astype(str)
monthly = near.groupby('exp_month').size().reset_index()
monthly.columns = ['month', 'count']
monthly = monthly.sort_values('month').head(13)
today_m = '2026-03'
monthly['urgent'] = monthly['month'].apply(
    lambda m: '#e53935' if m <= '2026-04' else '#fb8c00' if m <= '2026-07' else '#1a73e8')

# ── top 10 medications at risk ──
iv_med = iv.merge(med[['id', 'name']], left_on='medication_id', right_on='id', how='left')
med_ec = (iv_med[iv_med['risk_level'].isin(['EXPIRED', 'CRITICAL', 'HIGH'])]
          .groupby(['name', 'risk_level'])['val'].sum()
          .reset_index())
top10 = (med_ec.groupby('name')['val'].sum()
         .sort_values(ascending=False).head(10).index.tolist())
med_top = (med_ec[med_ec['name'].isin(top10)]
           .pivot_table(index='name', columns='risk_level', values='val', fill_value=0)
           .reindex(risk_order[:3], axis=1, fill_value=0)
           .loc[:, lambda df: df.columns[df.sum() > 0]])
med_top = med_top.loc[top10[::-1]]   # reverse for horizontal bar (top = highest)

# ── per-facility at-risk value ──
fac_risk = (iv[iv['risk_level'].isin(['EXPIRED', 'CRITICAL', 'HIGH'])]
            .groupby(['facility_id', 'risk_level'])['val'].sum()
            .reset_index())
fac_order = (fac_risk.groupby('facility_id')['val'].sum()
             .sort_values(ascending=False).index.tolist())

# ════════════════════════════════════════════════════════════════════
# Build 4-panel Dashboard
# ════════════════════════════════════════════════════════════════════
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        '① Risk Level Distribution — 3,000 Batches',
        '② Top 10 Medications: At-Risk Inventory Value',
        '③ Monthly Batch Expiry Forecast (Next 13 Months)',
        '④ Expiry Risk by Facility ($USD at Risk)'),
    specs=[[{"type": "domain"}, {"type": "xy"}],
           [{"type": "xy"}, {"type": "xy"}]],
    vertical_spacing=0.16,
    horizontal_spacing=0.12)

# ─── Panel 1: Donut ───
pull_vals = [0.1 if r in ('EXPIRED', 'CRITICAL') else 0 for r in risk_order]
fig.add_trace(go.Pie(
    labels=risk_order,
    values=rc.values,
    marker_colors=risk_colors,
    pull=pull_vals,
    hole=0.55,
    textinfo='label+percent+value',
    textfont=dict(size=11),
    hovertemplate='<b>%{label}</b><br>Batches: %{value}<br>Share: %{percent}<extra></extra>',
    sort=False),
    row=1, col=1)
fig.add_annotation(
    x=0.19, y=0.71, xref='paper', yref='paper',
    text=f'<b>3,000</b><br>Total<br>Batches',
    showarrow=False, font=dict(size=12, color='#333'), align='center')

# ─── Panel 2: Horizontal Stacked Bar — top 10 meds ───
for rl in [c for c in ['HIGH', 'CRITICAL', 'EXPIRED'] if c in med_top.columns]:
    fig.add_trace(go.Bar(
        y=med_top.index,
        x=med_top[rl],
        name=rl,
        orientation='h',
        marker_color=rc_map[rl],
        text=[f'${v/1e3:.0f}K' if v > 500 else '' for v in med_top[rl]],
        textposition='inside',
        textfont=dict(size=9, color='white'),
        hovertemplate=f'<b>%{{y}}</b><br>{rl}: $%{{x:,.0f}}<extra></extra>',
        legendgroup=rl,
        showlegend=True),
        row=1, col=2)

# ─── Panel 3: Monthly Expiry Bar ───
fig.add_trace(go.Bar(
    x=monthly['month'],
    y=monthly['count'],
    marker_color=monthly['urgent'],
    text=monthly['count'],
    textposition='outside',
    textfont=dict(size=10),
    hovertemplate='<b>%{x}</b><br>Batches expiring: %{y}<extra></extra>',
    showlegend=False),
    row=2, col=1)
# urgent zone shading — use add_shape to avoid pie-subplot conflict
fig.add_shape(
    type='rect',
    xref='x3', yref='y3 domain',
    x0='2026-02', x1='2026-04',
    y0=0, y1=1,
    fillcolor='rgba(229,57,53,0.08)', line_width=0)
fig.add_annotation(
    x='2026-03', y=monthly['count'].max() * 1.22,
    xref='x3', yref='y3',
    text='<b>CRITICAL</b><br>window', showarrow=False,
    font=dict(size=10, color='#c62828'),
    bgcolor='rgba(255,235,235,0.9)', bordercolor='#e53935', borderwidth=1)

# ─── Panel 4: Stacked Bar by Facility ───
for rl in ['EXPIRED', 'CRITICAL', 'HIGH']:
    sub = fac_risk[fac_risk['risk_level'] == rl].set_index('facility_id')
    vals = [sub.loc[f, 'val'] if f in sub.index else 0 for f in fac_order]
    fig.add_trace(go.Bar(
        name=rl,
        x=fac_order,
        y=vals,
        marker_color=rc_map[rl],
        text=[f'${v/1e3:.0f}K' if v > 2000 else '' for v in vals],
        textposition='inside',
        textfont=dict(size=9, color='white'),
        hovertemplate=f'<b>%{{x}}</b><br>{rl}: $%{{y:,.0f}}<extra></extra>',
        legendgroup=rl,
        showlegend=False),
        row=2, col=2)
# Total labels on top
fac_totals = fac_risk.groupby('facility_id')['val'].sum().reindex(fac_order).fillna(0)
for fac, tot in fac_totals.items():
    fig.add_annotation(
        x=fac, y=tot + 1800,
        xref='x4', yref='y4',
        text=f'<b>${tot/1e3:.0f}K</b>',
        showarrow=False, font=dict(size=10, color='#333'))

# ════════════════════════════════════════════════════════════════════
# Layout
# ════════════════════════════════════════════════════════════════════
fig.update_layout(
    title=dict(
        text=(
            'Expiry Risk Detection Dashboard — Pharmaceutical Inventory<br>'
            f'<sup>3,000 batches monitored | {rc["EXPIRED"]+rc["CRITICAL"]} batches in critical window '
            f'| ${at_risk_val/1e3:.0f}K at risk (HIGH+CRITICAL+EXPIRED) '
            f'| {at_risk_val/total_val*100:.1f}% of total ${total_val/1e6:.2f}M inventory</sup>'),
        font=dict(size=22), x=0.5),
    barmode='stack',
    plot_bgcolor='white',
    paper_bgcolor='#f5f7fa',
    height=840,
    legend=dict(
        title='Risk Level',
        orientation='v',
        x=1.01, y=0.85,
        font=dict(size=11),
        bordercolor='#ccc', borderwidth=1))

fig.update_yaxes(gridcolor='#eee', row=1, col=2)
fig.update_xaxes(tickformat='$,.0f', row=1, col=2, title_text='Value at Risk ($)')
fig.update_yaxes(title_text='Number of Batches Expiring', gridcolor='#eee', row=2, col=1)
fig.update_xaxes(title_text='Month', tickangle=-40, tickfont=dict(size=9), row=2, col=1)
fig.update_yaxes(title_text='At-Risk Value ($)', tickformat='$,.0f', gridcolor='#eee', row=2, col=2)
fig.update_xaxes(title_text='Facility', row=2, col=2)

fig.write_html('./g_expiry_risk_dashboard.html')
print('✅  Saved: g_expiry_risk_dashboard.html')
print(f'   Expired: {rc["EXPIRED"]} | Critical: {rc["CRITICAL"]} | High: {rc["HIGH"]}')
print(f'   At-risk value: ${at_risk_val:,.0f}  ({at_risk_val/total_val*100:.1f}%)')
