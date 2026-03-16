"""
Data Quality Report Generator
Generates human-readable quality reports for all pipeline data
"""

from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal
import json


class DataQualityReportGenerator:
    """Generate quality reports for data validation results"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.report = {}
    
    def generate_input_quality_report(self, validation_results: Dict[str, bool]) -> str:
        """
        Generate quality report for input data
        
        Args:
            validation_results: Dict with validation method names as keys
        
        Returns:
            Formatted report string
        """
        
        total_checks = len(validation_results)
        passed = sum(1 for v in validation_results.values() if v is True)
        failed = total_checks - passed
        
        report = []
        report.append("=" * 60)
        report.append(f"INPUT DATA QUALITY REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append(f"SUMMARY")
        report.append(f"Total Checks: {total_checks}")
        report.append(f"Passed: {passed} ✓")
        report.append(f"Failed: {failed} ✗")
        
        if total_checks > 0:
            pass_rate = (passed / total_checks) * 100
            report.append(f"Pass Rate: {pass_rate:.1f}%")
        
        report.append("")
        
        # Details
        report.append("VALIDATION DETAILS")
        for validator_name, passed_validation in validation_results.items():
            status = "✓ PASS" if passed_validation else "✗ FAIL"
            report.append(f"  {validator_name}: {status}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_forecast_quality_report(self, 
                                          forecasts: List[Dict[str, Any]],
                                          accuracy_metrics: Dict[str, float]) -> str:
        """
        Generate quality report for forecasts
        
        Args:
            forecasts: List of forecast objects
            accuracy_metrics: Dict with accuracy scores
        
        Returns:
            Formatted report string
        """
        
        report = []
        report.append("=" * 60)
        report.append(f"FORECAST QUALITY REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append(f"Total Forecasts: {len(forecasts)}")
        report.append(f"Avg Confidence: {accuracy_metrics.get('avg_confidence', 0):.2%}")
        report.append(f"Avg MAPE: {accuracy_metrics.get('avg_mape', 0):.2%}")
        report.append(f"Models Used: {accuracy_metrics.get('models_used', {})}")
        report.append("")
        
        # By model
        report.append("FORECAST BY MODEL")
        for model_type in ['PROPHET', 'ARIMA']:
            count = sum(1 for f in forecasts if f.get('model_type') == model_type)
            if count > 0:
                model_forecasts = [f for f in forecasts if f.get('model_type') == model_type]
                avg_conf = sum(f.get('confidence_level', 0) for f in model_forecasts) / len(model_forecasts)
                report.append(f"  {model_type}: {count} forecasts (avg confidence: {avg_conf:.2%})")
        
        report.append("")
        
        # Anomalies detected
        anomalies = sum(1 for f in forecasts if f.get('anomaly_detected'))
        report.append(f"ANOMALIES DETECTED: {anomalies}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_recommendation_quality_report(self,
                                               recommendations: List[Dict[str, Any]],
                                               action_costs: Dict[str, Decimal]) -> str:
        """
        Generate quality report for recommendations
        
        Args:
            recommendations: List of recommendation objects
            action_costs: Dict with cost breakdown
        
        Returns:
            Formatted report string
        """
        
        report = []
        report.append("=" * 60)
        report.append(f"RECOMMENDATION QUALITY REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append(f"Total Recommendations: {len(recommendations)}")
        
        action_counts = {}
        for rec in recommendations:
            action = rec.get('action_type', 'UNKNOWN')
            action_counts[action] = action_counts.get(action, 0) + 1
        
        report.append("")
        report.append("ACTION BREAKDOWN")
        for action_type in ['TRANSFER', 'DISPOSE', 'HOLD']:
            count = action_counts.get(action_type, 0)
            percentage = (count / len(recommendations) * 100) if recommendations else 0
            report.append(f"  {action_type}: {count} ({percentage:.1f}%)")
        
        report.append("")
        
        # Cost analysis
        report.append("COST ANALYSIS")
        total_cost = sum(action_costs.values())
        report.append(f"Total Estimated Cost: ${float(total_cost):,.2f}")
        
        for action, cost in action_costs.items():
            percentage = (float(cost) / float(total_cost) * 100) if total_cost > 0 else 0
            report.append(f"  {action}: ${float(cost):,.2f} ({percentage:.1f}%)")
        
        report.append("")
        
        # Confidence
        if recommendations:
            avg_confidence = sum(r.get('confidence_score', 0) for r in recommendations) / len(recommendations)
            report.append(f"Average Confidence: {avg_confidence:.2%}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_supply_chain_quality_report(self,
                                            decisions: List[Dict[str, Any]],
                                            total_cost: Decimal) -> str:
        """
        Generate quality report for supply chain decisions
        
        Args:
            decisions: List of supply chain decisions
            total_cost: Total estimated cost
        
        Returns:
            Formatted report string
        """
        
        report = []
        report.append("=" * 60)
        report.append(f"SUPPLY CHAIN QUALITY REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append(f"Total Decisions: {len(decisions)}")
        report.append(f"Total Estimated Cost: ${float(total_cost):,.2f}")
        
        decision_counts = {}
        for dec in decisions:
            decision_type = dec.get('decision_type', 'UNKNOWN')
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
        
        report.append("")
        report.append("DECISION BREAKDOWN")
        for decision_type in ['REORDER', 'TRANSFER']:
            count = decision_counts.get(decision_type, 0)
            percentage = (count / len(decisions) * 100) if decisions else 0
            report.append(f"  {decision_type}: {count} ({percentage:.1f}%)")
        
        report.append("")
        
        # Lead times
        if decisions:
            lead_times = [d.get('lead_time_estimate_days', 0) for d in decisions]
            avg_lead_time = sum(lead_times) / len(lead_times)
            min_lead_time = min(lead_times)
            max_lead_time = max(lead_times)
            
            report.append("LEAD TIME ANALYSIS")
            report.append(f"  Average: {avg_lead_time:.1f} days")
            report.append(f"  Min: {min_lead_time} days")
            report.append(f"  Max: {max_lead_time} days")
            report.append("")
        
        # Confidence
        if decisions:
            avg_confidence = sum(d.get('confidence_score', 0) for d in decisions) / len(decisions)
            report.append(f"Average Confidence: {avg_confidence:.2%}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_pipeline_quality_report(self, stage_results: Dict[str, Any]) -> str:
        """
        Generate overall pipeline quality report
        
        Args:
            stage_results: Results from all pipeline stages
        
        Returns:
            Formatted report string
        """
        
        report = []
        report.append("=" * 60)
        report.append(f"PIPELINE QUALITY REPORT - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Stage status
        report.append("STAGE EXECUTION STATUS")
        for stage_name, stage_result in stage_results.items():
            status = "✓ PASS" if stage_result.get('success', False) else "✗ FAIL"
            duration = stage_result.get('duration_ms', 0)
            report.append(f"  Stage {stage_name}: {status} ({duration}ms)")
        
        report.append("")
        
        # Overall health
        passed_stages = sum(1 for r in stage_results.values() if r.get('success'))
        total_stages = len(stage_results)
        health_score = passed_stages / total_stages if total_stages > 0 else 0
        
        report.append("OVERALL HEALTH")
        report.append(f"Health Score: {health_score:.2%}")
        report.append(f"Passed: {passed_stages}/{total_stages}")
        
        if health_score < 0.8:
            report.append("⚠️  WARNING: Low overall system health")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate machine-readable JSON report
        
        Args:
            report_data: All report data
        
        Returns:
            JSON formatted report
        """
        
        return json.dumps(report_data, indent=2, default=str)
