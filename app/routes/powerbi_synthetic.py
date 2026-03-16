"""PowerBI Data Export Routes - Using Real Synthetic Data from CSVs"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
import csv
import io
import pandas as pd
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/powerbi", tags=["PowerBI Data Export"])

# Path to synthetic data
SYNTHETIC_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data-generation",
    "synthetic_data"
)


def load_all_data():
    """Load and cache all synthetic data"""
    try:
        inventory_path = os.path.join(SYNTHETIC_DATA_DIR, "inventory.csv")
        meds_path = os.path.join(SYNTHETIC_DATA_DIR, "medications.csv")
        facs_path = os.path.join(SYNTHETIC_DATA_DIR, "facilities.csv")
        trans_path = os.path.join(SYNTHETIC_DATA_DIR, "transfers.csv")
        forecast_path = os.path.join(SYNTHETIC_DATA_DIR, "demand_forecast.csv")
        
        inventory_df = pd.read_csv(inventory_path) if os.path.exists(inventory_path) else pd.DataFrame()
        meds_df = pd.read_csv(meds_path) if os.path.exists(meds_path) else pd.DataFrame()
        facs_df = pd.read_csv(facs_path) if os.path.exists(facs_path) else pd.DataFrame()
        trans_df = pd.read_csv(trans_path) if os.path.exists(trans_path) else pd.DataFrame()
        forecast_df = pd.read_csv(forecast_path) if os.path.exists(forecast_path) else pd.DataFrame()
        
        return inventory_df, meds_df, facs_df, trans_df, forecast_df
    except Exception as e:
        logger.error(f"Error loading synthetic data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


# Expiration Risk Export Endpoint
@router.get("/export/expiration-risk")
async def export_expiration_risk(
    format: str = Query("json", regex="^(json|csv)$"),
    days_window: int = Query(30, ge=7, le=365),
):
    """
    Export expiration risk data for PowerBI - 3000+ real records
    """
    try:
        inventory_df, meds_df, facs_df, _, _ = load_all_data()
        
        if inventory_df.empty:
            raise ValueError("No inventory data available")
        
        # Merge with medications
        meds_dict = {row['id']: row['name'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        cat_dict = {row['id']: row['category'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        
        # Merge with facilities  
        facs_dict = {row['id']: row['name'] for _, row in facs_df.iterrows()} if not facs_df.empty else {}
        
        # Build records
        records = []
        for _, row in inventory_df.iterrows():
            med_id = row['medication_id']
            unit_cost = 5.0 + (int(med_id) % 50) if isinstance(med_id, (int, float)) else 5.0
            batch_value = row['quantity_on_hand'] * unit_cost
            
            records.append({
                "batch_id": row['batch_number'],
                "medication_id": med_id,
                "medication_name": meds_dict.get(med_id, f"Med {med_id}"),
                "facility_id": row['facility_id'],
                "facility_name": facs_dict.get(row['facility_id'], f"Fac {row['facility_id']}"),
                "quantity_on_hand": int(row['quantity_on_hand']),
                "unit_cost": float(unit_cost),
                "batch_value": float(batch_value),
                "expiry_date": str(row['expiration_date']),
                "days_until_expiry": int(row['days_to_expiry']),
                "risk_level": row['risk_level'],
                "category": cat_dict.get(med_id, "Other"),
                "recommendation": "TRANSFER" if row['risk_level'] in ['CRITICAL', 'HIGH'] else "MONITOR",
            })
        
        # Export format
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["batch_id", "medication_id", "medication_name", "facility_id",
                         "facility_name", "quantity_on_hand", "unit_cost", "batch_value",
                         "expiry_date", "days_until_expiry", "risk_level", "category", "recommendation"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=expiration_risk.csv"}
            )
        else:
            return {"data": records, "format": "json", "rows": len(records)}
            
    except Exception as e:
        logger.error(f"Expiration risk export failed: {str(e)}")
        return {"data": [], "error": str(e), "rows": 0}


# Transfer Coordination Export Endpoint
@router.get("/export/transfer-coordination")
async def export_transfer_coordination(
    format: str = Query("json", regex="^(json|csv)$"),
    status: Optional[str] = Query(None),
):
    """
    Export transfer coordination data for PowerBI - 500+ real records
    """
    try:
        _, meds_df, facs_df, trans_df, _ = load_all_data()
        
        if trans_df.empty:
            raise ValueError("No transfer data available")
        
        # Build lookup dicts
        meds_dict = {row['id']: row['name'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        facs_dict = {row['id']: row['name'] for _, row in facs_df.iterrows()} if not facs_df.empty else {}
        
        # Build records
        records = []
        for _, row in trans_df.iterrows():
            med_id = row['medication_id']
            src_fac = row['source_facility_id']
            tgt_fac = row['target_facility_id']
            qty = row.get('quantity_transferred', row.get('quantity_requested', 0))
            cost = row['cost_usd'] if 'cost_usd' in row else 0
            unit_cost = 5.0 + (int(med_id) % 50) if isinstance(med_id, (int, float)) else 5.0
            med_value = qty * unit_cost
            
            records.append({
                "order_id": row['transfer_id'],
                "from_facility": facs_dict.get(src_fac, f"Fac {src_fac}"),
                "from_facility_id": src_fac,
                "to_facility": facs_dict.get(tgt_fac, f"Fac {tgt_fac}"),
                "to_facility_id": tgt_fac,
                "medication_id": med_id,
                "medication_name": meds_dict.get(med_id, f"Med {med_id}"),
                "quantity": int(qty),
                "unit_cost": float(unit_cost),
                "transfer_cost_per_unit": 0.5,
                "total_transfer_cost": float(cost),
                "total_medication_value": float(med_value),
                "decision_type": "TRANSFER",
                "status": row['transfer_status'],
                "compliance_status": "OK",
                "expected_delivery_date": str(row.get('received_date', row.get('transfer_date', ''))),
                "created_date": str(row.get('created_date', '')),
                "rationale": row.get('reason', ''),
                "estimated_savings": float(med_value * 0.3),
                "cost_benefit_score": 0.75,
            })
        
        # Filter by status if provided
        if status:
            records = [r for r in records if r["status"] == status]
        
        # Export format
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["order_id", "from_facility", "to_facility", "medication_name",
                         "quantity", "total_transfer_cost", "total_medication_value",
                         "status", "compliance_status", "expected_delivery_date",
                         "estimated_savings", "cost_benefit_score"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=transfer_coordination.csv"}
            )
        else:
            return {"data": records, "format": "json", "rows": len(records)}
            
    except Exception as e:
        logger.error(f"Transfer coordination export failed: {str(e)}")
        return {"data": [], "error": str(e), "rows": 0}


# Demand Forecast Export Endpoint
@router.get("/export/demand-forecast")
async def export_demand_forecast(
    format: str = Query("json", regex="^(json|csv)$"),
    urgency: Optional[str] = Query(None),
):
    """
    Export demand forecast data for PowerBI - 4500+ real records
    """
    try:
        _, meds_df, _, _, forecast_df = load_all_data()
        
        if forecast_df.empty:
            raise ValueError("No forecast data available")
        
        # Build lookup dicts
        meds_dict = {row['id']: row['name'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        cat_dict = {row['id']: row['category'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        
        # Build records
        records = []
        for _, row in forecast_df.iterrows():
            med_id = row['medication_id']
            
            records.append({
                "medication_id": med_id,
                "medication_name": meds_dict.get(med_id, f"Med {med_id}"),
                "category": cat_dict.get(med_id, "Other"),
                "forecast_date": str(datetime.now()),
                "current_inventory": int(row.get('current_inventory', 0)),
                "predicted_demand_7d": int(row.get('demand_7day_forecast', 0)),
                "predicted_demand_14d": int(row.get('demand_14day_forecast', 0)),
                "predicted_demand_30d": int(row.get('demand_30day_forecast', 0)),
                "forecast_confidence": float(row.get('forecast_confidence', 0.85)),
                "model_type": row.get('forecast_model', 'PROPHET'),
                "model_accuracy_mape": float(row.get('model_mape', 0.15)),
                "min_safe_stock": int(row.get('min_safety_stock', 0)),
                "max_stock": int(row.get('max_capacity', 0)),
                "suggested_action": row.get('suggested_action', 'MONITOR'),
                "urgency": row.get('urgency_level', 'MEDIUM'),
                "risk_level": row.get('risk_level', 'LOW'),
                "anomalies_detected": int(row.get('anomalies_detected', 0)),
                "external_signals": str(row.get('external_signals', 'None')),
            })
        
        # Filter by urgency if provided
        if urgency:
            records = [r for r in records if r["urgency"] == urgency]
        
        # Export format
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["medication_id", "medication_name", "category", "current_inventory",
                         "predicted_demand_30d", "forecast_confidence", "model_type",
                         "model_accuracy_mape", "suggested_action", "urgency", "risk_level",
                         "anomalies_detected", "external_signals"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=demand_forecast.csv"}
            )
        else:
            return {"data": records, "format": "json", "rows": len(records)}
            
    except Exception as e:
        logger.error(f"Demand forecast export failed: {str(e)}")
        return {"data": [], "error": str(e), "rows": 0}


# Summary Statistics Endpoint
@router.get("/export/summary-statistics")
async def export_summary_statistics():
    """
    Export summary statistics for dashboard KPIs
    """
    try:
        inventory_df, _, _, trans_df, forecast_df = load_all_data()
        
        expiration_count = len(inventory_df[inventory_df['risk_level'].isin(['CRITICAL', 'HIGH'])]) if not inventory_df.empty else 0
        transfer_count = len(trans_df) if not trans_df.empty else 0
        forecast_count = len(forecast_df) if not forecast_df.empty else 0
        
        return {
            "summary": {
                "timestamp": datetime.now().isoformat(),
                "data_completeness": {
                    "inventory_records": len(inventory_df),
                    "transfer_records": transfer_count,
                    "forecast_records": forecast_count,
                    "total_records": len(inventory_df) + transfer_count + forecast_count,
                },
                "expiration_risk": {
                    "total_batches": len(inventory_df),
                    "at_risk_count": expiration_count,
                    "risk_distribution": dict(inventory_df['risk_level'].value_counts()) if not inventory_df.empty else {},
                },
                "transfer_coordination": {
                    "total_transfers": transfer_count,
                    "pending_transfers": len(trans_df[trans_df['transfer_status'] == 'PENDING']) if not trans_df.empty else 0,
                },
                "demand_forecast": {
                    "forecast_records": forecast_count,
                },
            }
        }
    except Exception as e:
        logger.error(f"Summary statistics export failed: {str(e)}")
        return {"error": str(e)}
