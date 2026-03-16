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
        
        # Build lookup dicts
        meds_dict = {row['id']: row['name'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
        cat_dict = {row['id']: row['category'] for _, row in meds_df.iterrows()} if not meds_df.empty else {}
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
        logger.error(f"Expiration risk export failed: {str(e)}, traceback: {e.__traceback__}")
        # Return fallback hardcoded data
        today = datetime.now().date()
        return {
            "data": [
                {
                    "batch_id": "BAT-0847",
                    "medication_id": 1,
                    "medication_name": "Amoxicillin 500mg",
                    "facility_id": "FAC001",
                    "facility_name": "Hospital A",
                    "quantity_on_hand": 2450,
                    "unit_cost": 10.50,
                    "batch_value": 25725.00,
                    "expiry_date": str(today + timedelta(days=6)),
                    "days_until_expiry": 6,
                    "risk_level": "CRITICAL",
                    "category": "Antibiotics",
                    "recommendation": "TRANSFER or DISPOSE",
                },
                {
                    "batch_id": "BAT-0902",
                    "medication_id": 2,
                    "medication_name": "Ibuprofen 200mg",
                    "facility_id": "FAC002",
                    "facility_name": "Clinic B",
                    "quantity_on_hand": 5670,
                    "unit_cost": 3.75,
                    "batch_value": 21262.50,
                    "expiry_date": str(today + timedelta(days=9)),
                    "days_until_expiry": 9,
                    "risk_level": "HIGH",
                    "category": "Pain Relief",
                    "recommendation": "TRANSFER",
                },
                {
                    "batch_id": "BAT-0756",
                    "medication_id": 3,
                    "medication_name": "Metformin 1000mg",
                    "facility_id": "FAC003",
                    "facility_name": "Hospital C",
                    "quantity_on_hand": 1230,
                    "unit_cost": 2.50,
                    "batch_value": 3075.00,
                    "expiry_date": str(today + timedelta(days=18)),
                    "days_until_expiry": 18,
                    "risk_level": "MEDIUM",
                    "category": "Diabetes Meds",
                    "recommendation": "MONITOR",
                },
                {
                    "batch_id": "BAT-0891",
                    "medication_id": 4,
                    "medication_name": "Aspirin 100mg",
                    "facility_id": "FAC001",
                    "facility_name": "Hospital A",
                    "quantity_on_hand": 3400,
                    "unit_cost": 1.25,
                    "batch_value": 4250.00,
                    "expiry_date": str(today + timedelta(days=13)),
                    "days_until_expiry": 13,
                    "risk_level": "HIGH",
                    "category": "Pain Relief",
                    "recommendation": "TRANSFER",
                },
                {
                    "batch_id": "BAT-0934",
                    "medication_id": 5,
                    "medication_name": "Lisinopril 10mg",
                    "facility_id": "FAC004",
                    "facility_name": "Clinic D",
                    "quantity_on_hand": 890,
                    "unit_cost": 8.75,
                    "batch_value": 7787.50,
                    "expiry_date": str(today + timedelta(days=16)),
                    "days_until_expiry": 16,
                    "risk_level": "MEDIUM",
                    "category": "Cardiovascular",
                    "recommendation": "MONITOR",
                },
            ],
            "format": "json",
            "rows": 5,
            "note": "Using fallback hardcoded data due to CSV loading error"
        }


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
            cost = row.get('cost_usd', 0)
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
                "status": row.get('transfer_status', 'PENDING'),
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
        # Return fallback hardcoded data
        return {
            "data": [
                {
                    "order_id": "ORD001",
                    "from_facility": "Hospital A",
                    "from_facility_id": "FAC001",
                    "to_facility": "Clinic C",
                    "to_facility_id": "FAC003",
                    "medication_id": 1,
                    "medication_name": "Amoxicillin 500mg",
                    "quantity": 450,
                    "unit_cost": 10.50,
                    "transfer_cost_per_unit": 2.50,
                    "total_transfer_cost": 1125.00,
                    "total_medication_value": 4725.00,
                    "decision_type": "TRANSFER",
                    "status": "PENDING",
                    "compliance_status": "OK",
                    "expected_delivery_date": str(datetime.now().date() + timedelta(days=2)),
                    "created_date": str(datetime.now().date() - timedelta(days=1)),
                    "rationale": "High demand at Clinic C, approaching expiry at Hospital A",
                    "estimated_savings": 2850.00,
                    "cost_benefit_score": 0.88,
                },
                {
                    "order_id": "ORD002",
                    "from_facility": "Hospital B",
                    "from_facility_id": "FAC002",
                    "to_facility": "Clinic F",
                    "to_facility_id": "FAC006",
                    "medication_id": 2,
                    "medication_name": "Ibuprofen 200mg",
                    "quantity": 890,
                    "unit_cost": 3.75,
                    "transfer_cost_per_unit": 1.50,
                    "total_transfer_cost": 1335.00,
                    "total_medication_value": 3337.50,
                    "decision_type": "TRANSFER",
                    "status": "PENDING",
                    "compliance_status": "OK",
                    "expected_delivery_date": str(datetime.now().date() + timedelta(days=2)),
                    "created_date": str(datetime.now().date() - timedelta(days=1)),
                    "rationale": "Rebalancing inventory across network",
                    "estimated_savings": 1800.00,
                    "cost_benefit_score": 0.82,
                },
                {
                    "order_id": "ORD003",
                    "from_facility": "Clinic D",
                    "from_facility_id": "FAC004",
                    "to_facility": "Hospital E",
                    "to_facility_id": "FAC005",
                    "medication_id": 3,
                    "medication_name": "Metformin 1000mg",
                    "quantity": 670,
                    "unit_cost": 2.50,
                    "transfer_cost_per_unit": 1.25,
                    "total_transfer_cost": 837.50,
                    "total_medication_value": 1675.00,
                    "decision_type": "TRANSFER",
                    "status": "READY",
                    "compliance_status": "OK",
                    "expected_delivery_date": str(datetime.now().date() + timedelta(days=1)),
                    "created_date": str(datetime.now().date() - timedelta(days=3)),
                    "rationale": "High demand forecast at Hospital E",
                    "estimated_savings": 950.00,
                    "cost_benefit_score": 0.90,
                },
                {
                    "order_id": "ORD004",
                    "from_facility": "Hospital G",
                    "from_facility_id": "FAC007",
                    "to_facility": "Hospital C",
                    "to_facility_id": "FAC003",
                    "medication_id": 5,
                    "medication_name": "Lisinopril 10mg",
                    "quantity": 340,
                    "unit_cost": 8.75,
                    "transfer_cost_per_unit": 3.50,
                    "total_transfer_cost": 1190.00,
                    "total_medication_value": 2975.00,
                    "decision_type": "TRANSFER",
                    "status": "BLOCKED",
                    "compliance_status": "REVIEW",
                    "expected_delivery_date": str(datetime.now().date() + timedelta(days=3)),
                    "created_date": str(datetime.now().date() - timedelta(days=2)),
                    "rationale": "Compliance issue - needs regulatory review",
                    "estimated_savings": 1250.00,
                    "cost_benefit_score": 0.75,
                },
                {
                    "order_id": "ORD005",
                    "from_facility": "Hospital A",
                    "from_facility_id": "FAC001",
                    "to_facility": "Hospital E",
                    "to_facility_id": "FAC005",
                    "medication_id": 4,
                    "medication_name": "Aspirin 100mg",
                    "quantity": 780,
                    "unit_cost": 1.25,
                    "transfer_cost_per_unit": 0.75,
                    "total_transfer_cost": 585.00,
                    "total_medication_value": 975.00,
                    "decision_type": "TRANSFER",
                    "status": "APPROVED",
                    "compliance_status": "OK",
                    "expected_delivery_date": str(datetime.now().date() + timedelta(days=1)),
                    "created_date": str(datetime.now().date()),
                    "rationale": "Planned consolidation transfer",
                    "estimated_savings": 320.00,
                    "cost_benefit_score": 0.85,
                },
            ],
            "format": "json",
            "rows": 5,
            "note": "Using fallback hardcoded data due to CSV loading error"
        }


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
        # Return fallback hardcoded data
        return {
            "data": [
                {
                    "medication_id": 1,
                    "medication_name": "Ibuprofen 200mg",
                    "category": "Pain Relief",
                    "forecast_date": str(datetime.now()),
                    "current_inventory": 5240,
                    "predicted_demand_7d": 1850,
                    "predicted_demand_14d": 3950,
                    "predicted_demand_30d": 8450,
                    "forecast_confidence": 0.89,
                    "model_type": "PROPHET",
                    "model_accuracy_mape": 0.123,
                    "min_safe_stock": 2000,
                    "max_stock": 8000,
                    "suggested_action": "MONITOR",
                    "urgency": "LOW",
                    "risk_level": "LOW",
                    "anomalies_detected": 0,
                    "external_signals": "None",
                },
                {
                    "medication_id": 2,
                    "medication_name": "Amoxicillin 500mg",
                    "category": "Antibiotics",
                    "forecast_date": str(datetime.now()),
                    "current_inventory": 1450,
                    "predicted_demand_7d": 1200,
                    "predicted_demand_14d": 2400,
                    "predicted_demand_30d": 5100,
                    "forecast_confidence": 0.85,
                    "model_type": "PROPHET",
                    "model_accuracy_mape": 0.156,
                    "min_safe_stock": 1500,
                    "max_stock": 6000,
                    "suggested_action": "REORDER",
                    "urgency": "HIGH",
                    "risk_level": "HIGH",
                    "anomalies_detected": 1,
                    "external_signals": "Disease outbreak (flu cases +45%)",
                },
                {
                    "medication_id": 3,
                    "medication_name": "Metformin 1000mg",
                    "category": "Diabetes Meds",
                    "forecast_date": str(datetime.now()),
                    "current_inventory": 3900,
                    "predicted_demand_7d": 980,
                    "predicted_demand_14d": 2100,
                    "predicted_demand_30d": 4200,
                    "forecast_confidence": 0.91,
                    "model_type": "ARIMA",
                    "model_accuracy_mape": 0.089,
                    "min_safe_stock": 2000,
                    "max_stock": 7000,
                    "suggested_action": "MONITOR",
                    "urgency": "LOW",
                    "risk_level": "LOW",
                    "anomalies_detected": 0,
                    "external_signals": "None",
                },
                {
                    "medication_id": 4,
                    "medication_name": "Lisinopril 10mg",
                    "category": "Cardiovascular",
                    "forecast_date": str(datetime.now()),
                    "current_inventory": 840,
                    "predicted_demand_7d": 950,
                    "predicted_demand_14d": 2100,
                    "predicted_demand_30d": 5240,
                    "forecast_confidence": 0.83,
                    "model_type": "PROPHET",
                    "model_accuracy_mape": 0.178,
                    "min_safe_stock": 1500,
                    "max_stock": 5000,
                    "suggested_action": "URGENT_REORDER",
                    "urgency": "CRITICAL",
                    "risk_level": "CRITICAL",
                    "anomalies_detected": 2,
                    "external_signals": "Temperature increase (seasonal demand spike)",
                },
                {
                    "medication_id": 5,
                    "medication_name": "Aspirin 100mg",
                    "category": "Pain Relief",
                    "forecast_date": str(datetime.now()),
                    "current_inventory": 2100,
                    "predicted_demand_7d": 750,
                    "predicted_demand_14d": 1600,
                    "predicted_demand_30d": 2450,
                    "forecast_confidence": 0.87,
                    "model_type": "BASELINE",
                    "model_accuracy_mape": 0.210,
                    "min_safe_stock": 1200,
                    "max_stock": 4000,
                    "suggested_action": "MONITOR",
                    "urgency": "LOW",
                    "risk_level": "LOW",
                    "anomalies_detected": 0,
                    "external_signals": "None",
                },
            ],
            "format": "json",
            "rows": 5,
            "note": "Using fallback hardcoded data due to CSV loading error"
        }


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
        return {
            "error": str(e),
            "summary": {
                "timestamp": datetime.now().isoformat(),
                "data_completeness": {
                    "inventory_records": 0,
                    "transfer_records": 0,
                    "forecast_records": 0,
                    "total_records": 0,
                }
            }
        }
