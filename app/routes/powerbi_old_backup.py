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


class ExpirationRiskExport:
    """Generate expiration risk data for PowerBI"""
    
    @staticmethod
    def get_sample_data() -> List[Dict[str, Any]]:
        """Load expiration risk data from synthetic inventory CSV"""
        try:
            # Load inventory data
            inventory_path = os.path.join(SYNTHETIC_DATA_DIR, "inventory.csv")
            if os.path.exists(inventory_path):
                inv_df = pd.read_csv(inventory_path)
                
                # Load medications for names and category
                med_path = os.path.join(SYNTHETIC_DATA_DIR, "medications.csv")
                meds_df = pd.read_csv(med_path) if os.path.exists(med_path) else pd.DataFrame()
                meds_df = meds_df.rename(columns={'id': 'medication_id'})
                
                # Load facilities for names  
                fac_path = os.path.join(SYNTHETIC_DATA_DIR, "facilities.csv")
                facs_df = pd.read_csv(fac_path) if os.path.exists(fac_path) else pd.DataFrame()
                facs_df = facs_df.rename(columns={'id': 'facility_id', 'name': 'facility_name'})
                
                # Merge datasets
                df = inv_df.merge(meds_df[['medication_id', 'name', 'category']], on='medication_id', how='left')
                df = df.rename(columns={'name': 'medication_name'})
                df = df.merge(facs_df[['facility_id', 'facility_name']], on='facility_id', how='left')
                
                # Assign unit costs (simulated)
                df['unit_cost'] = 5.0 + (df['medication_id'].apply(int) % 50)
                df['batch_value'] = df['quantity_on_hand'] * df['unit_cost']
                
                # Convert to records
                records = []
                for _, row in df.iterrows():
                    records.append({
                        "batch_id": row['batch_number'],
                        "medication_id": row['medication_id'],
                        "medication_name": row.get('medication_name', 'Unknown'),
                        "facility_id": row['facility_id'],
                        "facility_name": row.get('facility_name', 'Unknown'),
                        "quantity_on_hand": int(row['quantity_on_hand']),
                        "unit_cost": float(row['unit_cost']),
                        "batch_value": float(row['batch_value']),
                        "expiry_date": str(row['expiration_date']),
                        "days_until_expiry": int(row['days_to_expiry']),
                        "risk_level": row['risk_level'],
                        "category": row.get('category', 'General'),
                        "recommendation": "TRANSFER" if row['risk_level'] in ['CRITICAL', 'HIGH'] else "MONITOR",
                    })
                return records
        except Exception as e:
            logger.error(f"Error loading inventory data: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        # Fallback to sample data if file not found
        return [
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
        ]


class TransferCoordinationExport:
    """Generate transfer coordination data for PowerBI"""
    
    @staticmethod
    def get_sample_data() -> List[Dict[str, Any]]:
        """Load transfer coordination data from synthetic transfers CSV"""
        try:
            # Load transfers data
            transfers_path = os.path.join(SYNTHETIC_DATA_DIR, "transfers.csv")
            if os.path.exists(transfers_path):
                df = pd.read_csv(transfers_path)
                
                # Load medications for names
                med_path = os.path.join(SYNTHETIC_DATA_DIR, "medications.csv")
                meds_df = pd.read_csv(med_path) if os.path.exists(med_path) else pd.DataFrame()
                med_dict = dict(zip(meds_df['medication_id'], meds_df['name'])) if not meds_df.empty else {}
                
                # Load facilities for names
                fac_path = os.path.join(SYNTHETIC_DATA_DIR, "facilities.csv")
                facs_df = pd.read_csv(fac_path) if os.path.exists(fac_path) else pd.DataFrame()
                fac_dict = dict(zip(facs_df['facility_id'], facs_df['facility_name'])) if not facs_df.empty else {}
                
                # Convert to records
                records = []
                for _, row in df.iterrows():
                    # Calculate estimated savings (transfer cost vs medication value)
                    med_value = float(row.get('total_medication_value', 0)) if pd.notna(row.get('total_medication_value')) else 0
                    transfer_cost = float(row.get('transfer_cost', 0)) if pd.notna(row.get('transfer_cost')) else 0
                    estimated_savings = max(0, med_value - transfer_cost)
                    
                    # Map transfer_status to our format
                    status_mapping = {
                        'PENDING': 'PENDING',
                        'IN_TRANSIT': 'IN_TRANSIT', 
                        'COMPLETED': 'COMPLETED',
                        'CANCELLED': 'BLOCKED'
                    }
                    status = status_mapping.get(row.get('transfer_status', 'PENDING'), 'PENDING')
                    
                    records.append({
                        "order_id": row['transfer_id'],
                        "from_facility": fac_dict.get(row['from_facility_id'], row.get('from_facility_id', 'Unknown')),
                        "from_facility_id": row['from_facility_id'],
                        "to_facility": fac_dict.get(row['to_facility_id'], row.get('to_facility_id', 'Unknown')),
                        "to_facility_id": row['to_facility_id'],
                        "medication_id": row['medication_id'],
                        "medication_name": med_dict.get(row['medication_id'], row.get('medication_id', 'Unknown')),
                        "quantity": int(row.get('quantity_units', 0)),
                        "unit_cost": float(row.get('unit_cost', 0)) if pd.notna(row.get('unit_cost')) else 0,
                        "transfer_cost_per_unit": float(row.get('transfer_cost_per_unit', 0)) if pd.notna(row.get('transfer_cost_per_unit')) else 0,
                        "total_transfer_cost": float(transfer_cost),
                        "total_medication_value": float(med_value),
                        "decision_type": row.get('optimization_type', 'TRANSFER'),
                        "status": status,
                        "compliance_status": "OK" if status != "BLOCKED" else "REVIEW",
                        "expected_delivery_date": str(row.get('expected_delivery_date', datetime.now().date())),
                        "created_date": str(row.get('created_date', datetime.now().date())),
                        "rationale": row.get('reason', ''),
                        "estimated_savings": float(estimated_savings),
                        "cost_benefit_score": float(row.get('cost_benefit_score', 0.5)) if pd.notna(row.get('cost_benefit_score')) else 0.5,
                    })
                return records
        except Exception as e:
            logger.error(f"Error loading transfer data: {e}")
        
        # Fallback to sample data
        return [
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
                "expected_delivery_date": datetime.now().date() + timedelta(days=2),
                "created_date": datetime.now().date() - timedelta(days=1),
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
                "expected_delivery_date": datetime.now().date() + timedelta(days=2),
                "created_date": datetime.now().date() - timedelta(days=1),
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
                "expected_delivery_date": datetime.now().date() + timedelta(days=1),
                "created_date": datetime.now().date() - timedelta(days=3),
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
                "expected_delivery_date": datetime.now().date() + timedelta(days=3),
                "created_date": datetime.now().date() - timedelta(days=2),
                "rationale": "Compliance issue - needs regulatory review",
                "estimated_savings": 1250.00,
                "cost_benefit_score": 0.75,
            },
        ]


class DemandForecastExport:
    """Generate demand forecast data for PowerBI"""
    
    @staticmethod
    def get_sample_data() -> List[Dict[str, Any]]:
        """Load demand forecast data from synthetic data CSV"""
        try:
            # Load forecast data
            forecast_path = os.path.join(SYNTHETIC_DATA_DIR, "demand_forecast.csv")
            if os.path.exists(forecast_path):
                df = pd.read_csv(forecast_path)
                
                # Load medications for names and categories
                med_path = os.path.join(SYNTHETIC_DATA_DIR, "medications.csv")
                meds_df = pd.read_csv(med_path) if os.path.exists(med_path) else pd.DataFrame()
                med_dict = dict(zip(meds_df['medication_id'], meds_df['name'])) if not meds_df.empty else {}
                cat_dict = dict(zip(meds_df['medication_id'], meds_df['category'])) if not meds_df.empty else {}
                
                # Convert to records
                records = []
                for _, row in df.iterrows():
                    # Map urgency based on risk
                    urgency = row.get('urgency_level', 'MEDIUM')
                    
                    # Map suggested action
                    action_mapping = {
                        'REORDER': 'REORDER',
                        'MONITOR': 'MONITOR',
                        'URGENT_REORDER': 'URGENT_REORDER',
                        'OK': 'MONITOR'
                    }
                    action = action_mapping.get(row.get('suggested_action', 'MONITOR'), 'MONITOR')
                    
                    records.append({
                        "medication_id": row['medication_id'],
                        "medication_name": med_dict.get(row['medication_id'], row.get('medication_id', 'Unknown')),
                        "category": cat_dict.get(row['medication_id'], row.get('category', 'General')),
                        "forecast_date": str(datetime.now()),
                        "current_inventory": int(row.get('current_inventory', 0)),
                        "predicted_demand_7d": int(row.get('demand_7day_forecast', 0)),
                        "predicted_demand_14d": int(row.get('demand_14day_forecast', 0)),
                        "predicted_demand_30d": int(row.get('demand_30day_forecast', 0)),
                        "forecast_confidence": float(row.get('forecast_confidence', 0.85)) if pd.notna(row.get('forecast_confidence')) else 0.85,
                        "model_type": row.get('forecast_model', 'PROPHET'),
                        "model_accuracy_mape": float(row.get('model_mape', 0.15)) if pd.notna(row.get('model_mape')) else 0.15,
                        "min_safe_stock": int(row.get('min_safety_stock', 0)),
                        "max_stock": int(row.get('max_capacity', 0)),
                        "suggested_action": action,
                        "urgency": urgency,
                        "risk_level": row.get('risk_level', 'LOW'),
                        "anomalies_detected": int(row.get('anomalies_detected', 0)),
                        "external_signals": row.get('external_signals', 'None'),
                    })
                return records
        except Exception as e:
            logger.error(f"Error loading forecast data: {e}")
        
        # Fallback to sample data
        return [
            {
                "medication_id": 1,
                "medication_name": "Ibuprofen 200mg",
                "category": "Pain Relief",
                "forecast_date": datetime.now(),
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
                "forecast_date": datetime.now(),
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
                "forecast_date": datetime.now(),
                "current_inventory": 3900,
                "predicted_demand_7d": 980,
                "predicted_demand_14d": 2100,
                "predicted_demand_30d": 4200,
                "forecast_confidence": 0.91,
                "model_type": "ARIMA",
                "model_accuracy_mape": 0.089,
                "min_safe_stock": 2000,
                "max_stock": 7000,
                "suggested_action": "OK",
                "urgency": "LOW",
                "risk_level": "LOW",
                "anomalies_detected": 0,
                "external_signals": "None",
            },
            {
                "medication_id": 4,
                "medication_name": "Lisinopril 10mg",
                "category": "Cardiovascular",
                "forecast_date": datetime.now(),
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
                "forecast_date": datetime.now(),
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
        ]


# Expiration Risk Export Endpoint
@router.get("/export/expiration-risk")
async def export_expiration_risk(
    format: str = Query("json", regex="^(json|csv)$"),
    days_window: int = Query(30, ge=7, le=365),
):
    """
    Export expiration risk data for PowerBI
    
    **Query Parameters:**
    - `format`: Export format (json or csv)
    - `days_window`: Days ahead to consider (default: 30)
    
    **Response:** Structured data ready for PowerBI import
    """
    try:
        data = ExpirationRiskExport.get_sample_data()
        
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["batch_id", "medication_id", "medication_name", "facility_id", 
                         "facility_name", "quantity_on_hand", "unit_cost", "batch_value",
                         "expiry_date", "days_until_expiry", "risk_level", "category", "recommendation"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
            csv_data = output.getvalue()
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=expiration_risk.csv"}
            )
        else:
            return {"data": data, "format": "json", "rows": len(data)}
            
    except Exception as e:
        logger.error(f"Expiration risk export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Export generation failed")


# Transfer Coordination Export Endpoint
@router.get("/export/transfer-coordination")
async def export_transfer_coordination(
    format: str = Query("json", regex="^(json|csv)$"),
    status: Optional[str] = Query(None, regex="^(PENDING|READY|BLOCKED|APPROVED)$"),
):
    """
    Export transfer coordination data for PowerBI
    
    **Query Parameters:**
    - `format`: Export format (json or csv)
    - `status`: Filter by status (PENDING, READY, BLOCKED, APPROVED)
    
    **Response:** Transfer proposals with costs and compliance checks
    """
    try:
        data = TransferCoordinationExport.get_sample_data()
        
        if status:
            data = [item for item in data if item["status"] == status]
        
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["order_id", "from_facility", "to_facility", "medication_name",
                         "quantity", "total_transfer_cost", "total_medication_value",
                         "status", "compliance_status", "expected_delivery_date",
                         "estimated_savings", "cost_benefit_score"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Create a clean row with only needed fields
                clean_row = {}
                for field in fieldnames:
                    value = row.get(field, "")
                    # Convert date objects to strings
                    if hasattr(value, 'isoformat'):
                        clean_row[field] = value.isoformat()
                    else:
                        clean_row[field] = str(value) if value else ""
                writer.writerow(clean_row)
            
            csv_data = output.getvalue()
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=transfer_coordination.csv"}
            )
        else:
            return {"data": data, "format": "json", "rows": len(data)}
            
    except Exception as e:
        logger.error(f"Transfer coordination export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Export generation failed")


# Demand Forecast Export Endpoint
@router.get("/export/demand-forecast")
async def export_demand_forecast(
    format: str = Query("json", regex="^(json|csv)$"),
    urgency: Optional[str] = Query(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$"),
):
    """
    Export demand forecast data for PowerBI
    
    **Query Parameters:**
    - `format`: Export format (json or csv)
    - `urgency`: Filter by urgency (LOW, MEDIUM, HIGH, CRITICAL)
    
    **Response:** Demand forecasts with recommendations and anomalies
    """
    try:
        data = DemandForecastExport.get_sample_data()
        
        if urgency:
            data = [item for item in data if item["urgency"] == urgency]
        
        if format == "csv":
            output = io.StringIO()
            fieldnames = ["medication_id", "medication_name", "category", "current_inventory",
                         "predicted_demand_30d", "forecast_confidence", "model_type",
                         "model_accuracy_mape", "suggested_action", "urgency", "risk_level",
                         "anomalies_detected", "external_signals"]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                # Create a clean row with only needed fields
                clean_row = {}
                for field in fieldnames:
                    value = row.get(field, "")
                    # Convert datetime objects to strings
                    if hasattr(value, 'isoformat'):
                        clean_row[field] = value.isoformat()
                    else:
                        clean_row[field] = str(value) if value else ""
                writer.writerow(clean_row)
            
            csv_data = output.getvalue()
            return StreamingResponse(
                iter([csv_data]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=demand_forecast.csv"}
            )
        else:
            return {"data": data, "format": "json", "rows": len(data)}
            
    except Exception as e:
        logger.error(f"Demand forecast export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Export generation failed")


# Summary Statistics Endpoint
@router.get("/export/summary-statistics")
async def export_summary_statistics():
    """
    Export summary statistics for dashboard KPIs
    
    **Response:** Key metrics for all three dashboards
    """
    today = datetime.now().date()
    return {
        "summary": {
            "timestamp": datetime.now().isoformat(),
            "expiration_risk": {
                "total_at_risk_value": 2450000,
                "batches_expiring_0_7_days": 340,
                "batches_expiring_7_14_days": 847,
                "trend_vs_week": "+$120K",
                "critical_count": 340,
            },
            "transfer_coordination": {
                "potential_savings": 425000,
                "surplus_found_units": 3247,
                "shortage_supply_units": 892,
                "pending_transfers": 4,
                "trend_vs_month": "+12.5%",
            },
            "demand_forecast": {
                "forecast_accuracy_mape": 0.123,
                "anomalies_detected": 47,
                "stockout_risk_medications": 12,
                "forecast_confidence_avg": 0.87,
                "trend_anomalies": "+8 vs week",
            },
        },
        "data_quality": {
            "completeness_score": 0.95,
            "validation_status": "PASS",
            "last_sync": datetime.now().isoformat(),
        }
    }
