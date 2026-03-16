"""
Demand Forecasting Tools
Tools for demand prediction, anomaly detection, and risk assessment
Used by Forecasting Analyst agent
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from database.data_loader import get_data_loader

class ForecastingTools:
    """Tool collection for demand forecasting"""
    
    def __init__(self):
        """Initialize with data loader"""
        self.loader = get_data_loader()
    
    def run_demand_forecast(
        self,
        medication_id: str,
        facility_id: str,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Run demand forecast for specific medication at facility
        
        Args:
            medication_id: Medication to forecast
            facility_id: Target facility
            forecast_days: Number of days to forecast
        
        Returns:
            Forecast with predicted demand
        """
        
        consumption_df = self.loader.data['consumption'].copy()
        inventory_df = self.loader.data['inventory']
        medications_df = self.loader.data['medications']
        
        # Filter for specific medication and facility
        consumption_df['consumption_date'] = pd.to_datetime(consumption_df['consumption_date'])
        med_consumption = consumption_df[
            (consumption_df['medication_id'] == medication_id) &
            (consumption_df['facility_id'] == facility_id)
        ]
        
        if len(med_consumption) == 0:
            return {
                "status": "no_historical_data",
                "medication_id": medication_id,
                "facility_id": facility_id,
                "message": "Insufficient historical data for forecast"
            }
        
        # Calculate basic statistics
        daily_consumption = med_consumption.groupby('consumption_date')['quantity_consumed'].sum()
        
        mean_consumption = daily_consumption.mean()
        std_consumption = daily_consumption.std()
        trend = (daily_consumption.iloc[-1] - daily_consumption.iloc[0]) / len(daily_consumption)
        
        # Simple forecast (linear trend + normal distribution)
        forecast = []
        base_date = daily_consumption.index[-1]
        
        for day in range(1, forecast_days + 1):
            forecast_date = base_date + timedelta(days=day)
            predicted_qty = mean_consumption + (trend * day)
            confidence_interval = (
                max(0, predicted_qty - 2 * std_consumption),
                predicted_qty + 2 * std_consumption
            )
            
            forecast.append({
                "forecast_date": forecast_date.strftime('%Y-%m-%d'),
                "predicted_quantity": max(0, int(predicted_qty)),
                "confidence_lower": int(confidence_interval[0]),
                "confidence_upper": int(confidence_interval[1]),
                "confidence_percent": 95
            })
        
        # Get current inventory
        current_inventory = inventory_df[
            (inventory_df['medication_id'] == medication_id) &
            (inventory_df['facility_id'] == facility_id)
        ]['quantity_on_hand'].sum()
        
        med_info = medications_df[medications_df['medication_id'] == medication_id].iloc[0]
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "facility_id": facility_id,
            "forecast_days": forecast_days,
            "current_inventory": int(current_inventory),
            "historical_daily_mean": round(mean_consumption, 2),
            "historical_daily_std": round(std_consumption, 2),
            "trend": round(trend, 4),
            "forecast": forecast,
            "recommendation": _generate_forecast_recommendation(current_inventory, forecast, mean_consumption)
        }
    
    def detect_demand_anomaly(
        self,
        medication_id: str,
        facility_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect anomalies in consumption patterns
        
        Args:
            medication_id: Medication to analyze
            facility_id: Target facility
            lookback_days: Days of history to analyze
        
        Returns:
            Anomaly detection results
        """
        
        consumption_df = self.loader.data['consumption'].copy()
        consumption_df['consumption_date'] = pd.to_datetime(consumption_df['consumption_date'])
        
        # Filter data
        med_consumption = consumption_df[
            (consumption_df['medication_id'] == medication_id) &
            (consumption_df['facility_id'] == facility_id)
        ].sort_values('consumption_date')
        
        if len(med_consumption) < 5:
            return {
                "status": "insufficient_data",
                "medication_id": medication_id,
                "facility_id": facility_id,
                "message": "Insufficient data for anomaly detection"
            }
        
        # Calculate daily consumption
        daily = med_consumption.groupby('consumption_date')['quantity_consumed'].sum()
        
        # Z-score based anomaly detection
        mean = daily.mean()
        std = daily.std()
        z_scores = np.abs((daily - mean) / std) if std > 0 else np.zeros(len(daily))
        
        # Identify anomalies (|Z| > 2)
        anomalies = []
        for date, z_score in z_scores.items():
            consumption = daily[date]
            if z_score > 2:
                anomalies.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "consumption": int(consumption),
                    "expected_range": f"{int(mean - 2*std)} to {int(mean + 2*std)}",
                    "z_score": round(z_score, 2),
                    "severity": "HIGH" if z_score > 3 else "MEDIUM",
                    "possible_causes": _identify_anomaly_causes(consumption, mean, std)
                })
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "facility_id": facility_id,
            "analysis_period_days": lookback_days,
            "mean_daily_consumption": round(mean, 2),
            "std_deviation": round(std, 2),
            "total_anomalies": len(anomalies),
            "anomalies": anomalies,
            "risk_assessment": "HIGH" if len(anomalies) > 2 else "MEDIUM" if len(anomalies) > 0 else "LOW"
        }
    
    def get_external_signals(
        self,
        facility_id: str,
        signal_type: str = None
    ) -> Dict[str, Any]:
        """
        Get external signals affecting demand (weather, disease outbreaks, etc)
        
        Args:
            facility_id: Target facility
            signal_type: Optional signal type (weather, disease, seasonal, etc)
        
        Returns:
            External signal data
        """
        
        signals_df = self.loader.data['external_signals'].copy()
        
        # Filter by facility if applicable
        if 'facility_id' in signals_df.columns:
            signals_df = signals_df[signals_df['facility_id'] == facility_id]
        
        # Filter by signal type if specified
        if signal_type and 'signal_type' in signals_df.columns:
            signals_df = signals_df[signals_df['signal_type'] == signal_type]
        
        # Get recent signals (last 30 days)
        signals_df['signal_date'] = pd.to_datetime(signals_df['signal_date'])
        recent = signals_df[
            signals_df['signal_date'] >= (datetime.now() - timedelta(days=30))
        ].sort_values('signal_date', ascending=False)
        
        # Categorize by impact
        high_impact = recent[recent['impact_score'] >= 7] if 'impact_score' in recent.columns else pd.DataFrame()
        medium_impact = recent[(recent['impact_score'] >= 4) & (recent['impact_score'] < 7)] if 'impact_score' in recent.columns else pd.DataFrame()
        
        return {
            "status": "success",
            "facility_id": facility_id,
            "signal_type": signal_type,
            "total_signals": len(recent),
            "high_impact_count": len(high_impact),
            "medium_impact_count": len(medium_impact),
            "signals": recent[['signal_date', 'signal_type', 'description', 'impact_score']].to_dict(orient='records') if len(recent) > 0 else [],
            "recommendations": _analyze_signals_impact(recent)
        }
    
    def assess_stockout_risk(
        self,
        medication_id: str,
        facility_id: str
    ) -> Dict[str, Any]:
        """
        Assess risk of stockout in next 7 days
        
        Args:
            medication_id: Medication to assess
            facility_id: Target facility
        
        Returns:
            Stockout risk assessment
        """
        
        inventory_df = self.loader.data['inventory']
        consumption_df = self.loader.data['consumption'].copy()
        
        # Get current inventory
        current_qty = inventory_df[
            (inventory_df['medication_id'] == medication_id) &
            (inventory_df['facility_id'] == facility_id)
        ]['quantity_on_hand'].sum()
        
        # Get recent consumption rate
        consumption_df['consumption_date'] = pd.to_datetime(consumption_df['consumption_date'])
        recent = consumption_df[
            (consumption_df['medication_id'] == medication_id) &
            (consumption_df['facility_id'] == facility_id) &
            (consumption_df['consumption_date'] >= (datetime.now() - pd.Timedelta(days=7)))
        ]
        
        if len(recent) == 0:
            daily_consumption = 0
        else:
            daily_consumption = recent['quantity_consumed'].sum() / 7
        
        # Calculate coverage
        coverage_days = current_qty / daily_consumption if daily_consumption > 0 else 999
        
        # Risk assessment
        if coverage_days < 3:
            risk_level = "CRITICAL"
            action = "URGENT: Replenish immediately"
        elif coverage_days < 7:
            risk_level = "HIGH"
            action = "URGENT: Schedule replenishment"
        elif coverage_days < 14:
            risk_level = "MEDIUM"
            action = "WARN: Monitor closely"
        else:
            risk_level = "LOW"
            action = "NORMAL: Routine monitoring"
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "facility_id": facility_id,
            "current_inventory": int(current_qty),
            "daily_consumption_rate": round(daily_consumption, 2),
            "coverage_days": round(coverage_days, 2),
            "risk_level": risk_level,
            "recommended_action": action,
            "suggested_replenishment": max(0, int((500 - current_qty)))  # Target 500 units
        }
    
    def recommend_replenishment(
        self,
        medication_id: str,
        facility_id: str
    ) -> Dict[str, Any]:
        """
        Recommend replenishment quantities and timing
        
        Args:
            medication_id: Medication to replenish
            facility_id: Target facility
        
        Returns:
            Replenishment recommendation
        """
        
        # Get stockout risk
        risk = self.assess_stockout_risk(medication_id, facility_id)
        
        # Get forecast
        forecast = self.run_demand_forecast(medication_id, facility_id, 30)
        
        if forecast['status'] != 'success':
            return {
                "status": "insufficient_data",
                "medication_id": medication_id,
                "facility_id": facility_id
            }
        
        # Calculate optimal replenishment
        next_30_days_demand = sum(
            f['predicted_quantity'] for f in forecast['forecast'][:30]
        )
        
        target_safety_stock = int(forecast['historical_daily_mean'] * 7)  # 7 days buffer
        current = risk['current_inventory']
        needed = max(0, (next_30_days_demand + target_safety_stock) - current)
        
        return {
            "status": "success",
            "medication_id": medication_id,
            "facility_id": facility_id,
            "current_inventory": current,
            "next_30_days_demand": next_30_days_demand,
            "safety_stock_target": target_safety_stock,
            "recommended_order_quantity": needed,
            "priority": risk['risk_level'],
            "rationale": f"Current stock covers {risk['coverage_days']} days; recommend order of {needed} units to maintain 7-day safety buffer",
            "recommended_delivery_days": 3 if risk['risk_level'] == 'CRITICAL' else 7
        }


def _generate_forecast_recommendation(current: int, forecast: List, mean: float) -> str:
    """Generate recommendation based on forecast"""
    total_demand = sum(f['predicted_quantity'] for f in forecast)
    if current < total_demand:
        return f"WARNING: Current inventory insufficient. Demand {total_demand} > Stock {current}"
    elif current < total_demand * 1.2:
        return "CAUTION: Limited buffer above forecasted demand"
    else:
        return "NORMAL: Adequate stock for forecasted demand"


def _identify_anomaly_causes(consumption: float, mean: float, std: float) -> List[str]:
    """Identify possible causes of anomalies"""
    if consumption > mean + 2*std:
        return ["Outbreak or sudden disease increase", "Hospital admission surge", "Medication switch recommendation"]
    elif consumption < mean - 2*std:
        return ["Supply issue or shortage elsewhere", "Medication recalled", "Change in treatment protocol", "Facility closure/reduced operations"]
    return ["Unknown"]


def _analyze_signals_impact(signals_df: pd.DataFrame) -> List[str]:
    """Analyze impact of external signals"""
    if len(signals_df) == 0:
        return ["No external signals detected"]
    
    recommendations = []
    
    if len(signals_df) > 0:
        for _, signal in signals_df.head(3).iterrows():
            if 'impact_score' in signal and signal['impact_score'] >= 7:
                recommendations.append(f"HIGH IMPACT: {signal.get('description', 'Signal detected')} - Consider increased safety stock")
    
    if len(recommendations) == 0:
        recommendations.append("Monitor signals for impact on medication demand")
    
    return recommendations


# Create tool instances for agent use
def create_forecasting_tools():
    """Factory function to create forecasting tools"""
    return ForecastingTools()


if __name__ == "__main__":
    # Test forecasting tools
    print("\n🔧 Testing Forecasting Tools\n")
    
    tools = create_forecasting_tools()
    
    # Get sample medication and facility
    meds = tools.loader.data['medications']['medication_id'].unique()
    facilities = tools.loader.data['facilities']['facility_id'].unique()
    
    if len(meds) > 0 and len(facilities) > 0:
        med_id = meds[0]
        fac_id = facilities[0]
        
        # Test 1: Run demand forecast
        print("✅ Test 1: Run demand forecast")
        forecast = tools.run_demand_forecast(med_id, fac_id)
        if forecast['status'] == 'success':
            print(f"   Forecast generated for 30 days")
            print(f"   Mean daily consumption: {forecast['historical_daily_mean']}")
        else:
            print(f"   Status: {forecast['status']}")
        
        # Test 2: Detect anomalies
        print("\n✅ Test 2: Detect demand anomaly")
        anomaly = tools.detect_demand_anomaly(med_id, fac_id)
        if anomaly['status'] == 'success':
            print(f"   Found {anomaly['total_anomalies']} anomalies")
            print(f"   Risk: {anomaly['risk_assessment']}")
        else:
            print(f"   Status: {anomaly['status']}")
        
        # Test 3: Get external signals
        print("\n✅ Test 3: Get external signals")
        signals = tools.get_external_signals(fac_id)
        print(f"   Total signals: {signals['total_signals']}")
        print(f"   High impact: {signals['high_impact_count']}")
        
        # Test 4: Assess stockout risk
        print("\n✅ Test 4: Assess stockout risk")
        risk = tools.assess_stockout_risk(med_id, fac_id)
        print(f"   Coverage: {risk['coverage_days']} days")
        print(f"   Risk Level: {risk['risk_level']}")
        
        # Test 5: Recommend replenishment
        print("\n✅ Test 5: Recommend replenishment")
        replenish = tools.recommend_replenishment(med_id, fac_id)
        if replenish['status'] == 'success':
            print(f"   Recommended order: {replenish['recommended_order_quantity']} units")
            print(f"   Priority: {replenish['priority']}")
        
        print("\n✅ All forecasting tool tests passed!\n")
    else:
        print("⚠️  Insufficient sample data for testing\n")
