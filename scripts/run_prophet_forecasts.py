"""
run_prophet_forecasts.py
========================
Reads synthetic consumption.csv, trains a real Facebook Prophet model per
medication, and rewrites demand_forecast.csv with genuine forecast outputs.

Usage:
    python scripts/run_prophet_forecasts.py
"""

import warnings
warnings.filterwarnings("ignore")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Suppress noisy prophet/cmdstan logs
import logging
logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)

from prophet import Prophet

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent / "data-generation" / "synthetic_data"
CONSUMPTION_CSV   = BASE / "consumption.csv"
MEDICATIONS_CSV   = BASE / "medications.csv"
INVENTORY_CSV     = BASE / "inventory.csv"
DEMAND_OUTPUT_CSV = BASE / "demand_forecast.csv"


def compute_urgency(current_inv: int, forecast_30: float, min_safety: int):
    """Return (urgency_level, suggested_action) based on stock coverage."""
    if forecast_30 <= 0:
        return "LOW", "MONITOR"
    days_cover = (current_inv / (forecast_30 / 30)) if forecast_30 > 0 else 999
    if days_cover < 7:
        return "CRITICAL", "EMERGENCY_ORDER"
    if days_cover < 14:
        return "HIGH", "EXPEDITE_ORDER"
    if current_inv < min_safety:
        return "MEDIUM", "REORDER"
    return "LOW", "MONITOR"


def run_prophet(daily_df: pd.DataFrame, periods: int = 30) -> dict:
    """
    Train Prophet on a daily aggregated DataFrame (columns: ds, y).
    Returns dict with yhat list, confidence, and mape.
    """
    if len(daily_df) < 7:
        return None

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.90,
        changepoint_prior_scale=0.05,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(daily_df)

    future = model.make_future_dataframe(periods=periods, freq="D")
    forecast = model.predict(future)

    tail = forecast.tail(periods)
    yhat = tail["yhat"].clip(lower=0).tolist()
    yhat_lower = tail["yhat_lower"].clip(lower=0).tolist()
    yhat_upper = tail["yhat_upper"].clip(lower=0).tolist()

    # MAPE on in-sample fitted values
    merged = daily_df.merge(
        forecast[["ds", "yhat"]], on="ds", how="inner"
    )
    merged = merged[merged["y"] > 0]
    if len(merged) >= 5:
        mape = float(np.mean(np.abs((merged["y"] - merged["yhat"]) / merged["y"])))
        mape = round(min(mape, 0.99), 3)
    else:
        mape = 0.15

    # Confidence = 1 - average relative interval width
    avg_width = np.mean(np.array(yhat_upper) - np.array(yhat_lower))
    avg_yhat  = np.mean(yhat) if np.mean(yhat) > 0 else 1
    confidence = round(float(np.clip(1 - avg_width / (2 * avg_yhat), 0.50, 0.99)), 2)

    return {
        "yhat": yhat,
        "yhat_lower": yhat_lower,
        "yhat_upper": yhat_upper,
        "mape": mape,
        "confidence": confidence,
    }


def detect_anomalies(daily_df: pd.DataFrame) -> int:
    """Count days where consumption deviates > 2 std from mean."""
    if len(daily_df) < 14:
        return 0
    mean = daily_df["y"].mean()
    std  = daily_df["y"].std()
    if std == 0:
        return 0
    return int(((daily_df["y"] - mean).abs() > 2 * std).sum())


def main():
    print("=" * 60)
    print("  Prophet Demand Forecasting on Synthetic Data")
    print("=" * 60)

    # Load data
    print("\n→ Loading consumption data...")
    consumption = pd.read_csv(CONSUMPTION_CSV, parse_dates=["transaction_date"])
    consumption = consumption[consumption["transaction_type"] == "CONSUMPTION"]
    consumption["date"] = consumption["transaction_date"].dt.date
    print(f"  {len(consumption):,} consumption transactions loaded")

    print("→ Loading medications...")
    medications = pd.read_csv(MEDICATIONS_CSV)
    med_ids = medications["id"].tolist()
    print(f"  {len(med_ids)} medications")

    print("→ Loading inventory for current stock levels...")
    inventory = pd.read_csv(INVENTORY_CSV)
    current_stock = (
        inventory.groupby("medication_id")["quantity_on_hand"].sum().to_dict()
    )

    # Load existing demand_forecast.csv for safety stock / capacity info
    existing = pd.read_csv(DEMAND_OUTPUT_CSV).set_index("medication_id")

    results = []
    failed = []

    print(f"\n→ Running Prophet for {len(med_ids)} medications...\n")

    for i, med_id in enumerate(med_ids, 1):
        med_cons = consumption[consumption["medication_id"] == med_id].copy()

        # Aggregate daily
        daily = (
            med_cons.groupby("date")["quantity"]
            .sum()
            .reset_index()
            .rename(columns={"date": "ds", "quantity": "y"})
        )
        daily["ds"] = pd.to_datetime(daily["ds"])
        daily = daily.sort_values("ds")

        model_type = "PROPHET"
        result = run_prophet(daily, periods=30)

        if result is None:
            # Fallback: simple 30-day mean
            model_type = "BASELINE"
            avg_daily = daily["y"].mean() if not daily.empty else 5
            yhat = [float(avg_daily)] * 30
            result = {
                "yhat": yhat,
                "yhat_lower": [max(0, v * 0.8) for v in yhat],
                "yhat_upper": [v * 1.2 for v in yhat],
                "mape": 0.20,
                "confidence": 0.70,
            }
            failed.append(med_id)

        yhat = result["yhat"]
        d7  = round(sum(yhat[:7]))
        d14 = round(sum(yhat[:14]))
        d30 = round(sum(yhat))

        cur_inv = int(current_stock.get(med_id, 0))

        # Safety stock / capacity from existing CSV if available
        if med_id in existing.index:
            min_safety = int(existing.loc[med_id, "min_safety_stock"])
            max_cap    = int(existing.loc[med_id, "max_capacity"])
            ext_sig    = existing.loc[med_id, "external_signals"]
        else:
            min_safety = max(100, d30 // 4)
            max_cap    = d30 * 3
            ext_sig    = "None"

        urgency, action = compute_urgency(cur_inv, d30, min_safety)
        anomalies = detect_anomalies(daily)

        # Risk level based on urgency
        risk_map = {"CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM", "LOW": "LOW"}
        risk = risk_map.get(urgency, "LOW")

        print(
            f"  [{i:02d}/{len(med_ids)}] {med_id}  "
            f"7d={d7:>5}  14d={d14:>5}  30d={d30:>6}  "
            f"model={model_type}  conf={result['confidence']:.0%}"
        )

        results.append({
            "medication_id":        med_id,
            "demand_7day_forecast":  d7,
            "demand_14day_forecast": d14,
            "demand_30day_forecast": d30,
            "current_inventory":    cur_inv,
            "forecast_confidence":  result["confidence"],
            "forecast_model":       model_type,
            "model_mape":           result["mape"],
            "min_safety_stock":     min_safety,
            "max_capacity":         max_cap,
            "urgency_level":        urgency,
            "suggested_action":     action,
            "risk_level":           risk,
            "anomalies_detected":   anomalies,
            "external_signals":     ext_sig,
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv(DEMAND_OUTPUT_CSV, index=False)

    print("\n" + "=" * 60)
    print(f"  ✅  Saved {len(results)} forecasts → {DEMAND_OUTPUT_CSV}")
    if failed:
        print(f"  ⚠️  {len(failed)} medications fell back to BASELINE (not enough data): {failed}")
    print("\n  Model distribution:")
    print(out_df["forecast_model"].value_counts().to_string())
    print("\n  Urgency distribution:")
    print(out_df["urgency_level"].value_counts().to_string())
    print("=" * 60)


if __name__ == "__main__":
    main()
