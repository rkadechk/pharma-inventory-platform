"""CrewAI Agent Framework Integration for Pharmaceutical Inventory Platform

Agents that analyze real synthetic data and provide decision support:
- Risk Assessment Agent (inventory expiration risks)
- Optimization Agent (transfer coordination recommendations)  
- Demand Analyst Agent (forecast analysis)
- Report Generation Agent (executive summaries)
"""

from crewai import Agent, Task, Crew
from langchain.chat_models import ChatOpenAI
import pandas as pd
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Path to synthetic data
SYNTHETIC_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data-generation",
    "synthetic_data"
)

# Initialize LLM (uses OPENAI_API_KEY environment variable)
llm = ChatOpenAI(
    model_name="gpt-4o", 
    temperature=0.7,
    model_kwargs={"stop": None}
)


class PharmacyDataLoader:
    """Load and cache pharmaceutical data from CSVs"""
    
    _cache = {}
    
    @classmethod
    def load_all_data(cls):
        """Load all synthetic data files"""
        if cls._cache:
            return cls._cache
        
        try:
            inventory_path = os.path.join(SYNTHETIC_DATA_DIR, "inventory.csv")
            transfers_path = os.path.join(SYNTHETIC_DATA_DIR, "transfers.csv")
            forecast_path = os.path.join(SYNTHETIC_DATA_DIR, "demand_forecast.csv")
            meds_path = os.path.join(SYNTHETIC_DATA_DIR, "medications.csv")
            facs_path = os.path.join(SYNTHETIC_DATA_DIR, "facilities.csv")
            
            cls._cache = {
                'inventory': pd.read_csv(inventory_path) if os.path.exists(inventory_path) else pd.DataFrame(),
                'transfers': pd.read_csv(transfers_path) if os.path.exists(transfers_path) else pd.DataFrame(),
                'forecast': pd.read_csv(forecast_path) if os.path.exists(forecast_path) else pd.DataFrame(),
                'medications': pd.read_csv(meds_path) if os.path.exists(meds_path) else pd.DataFrame(),
                'facilities': pd.read_csv(facs_path) if os.path.exists(facs_path) else pd.DataFrame(),
            }
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            cls._cache = {k: pd.DataFrame() for k in ['inventory', 'transfers', 'forecast', 'medications', 'facilities']}
        
        return cls._cache


class ExpirationRiskAnalyst:
    """Agent that analyzes expiration risks and recommends actions"""
    
    def __init__(self):
        data = PharmacyDataLoader.load_all_data()
        self.inventory = data['inventory']
        self.medications = data['medications']
        self.facilities = data['facilities']
    
    def analyze(self) -> dict:
        """Analyze expiration risks in inventory"""
        
        if self.inventory.empty:
            return {"error": "No inventory data available"}
        
        # Risk analysis
        critical_count = len(self.inventory[self.inventory['risk_level'] == 'CRITICAL'])
        high_count = len(self.inventory[self.inventory['risk_level'] == 'HIGH'])
        total_at_risk_value = self.inventory[
            self.inventory['risk_level'].isin(['CRITICAL', 'HIGH'])
        ]['quantity_on_hand'].sum() * 5.0  # Simple unit cost
        
        # Prepare context for agent
        risk_summary = f"""
        INVENTORY EXPIRATION RISK ANALYSIS:
        - Total Batches: {len(self.inventory)}
        - Critical Risk (0-7 days): {critical_count} batches
        - High Risk (7-14 days): {high_count} batches
        - Total At-Risk Value: ${total_at_risk_value:,.2f}
        - Risk Distribution: {dict(self.inventory['risk_level'].value_counts())}
        
        Top expiring items:
        {self._get_top_expiring_items()}
        """
        
        return {
            "analysis_type": "expiration_risk",
            "summary": risk_summary,
            "critical_count": int(critical_count),
            "high_count": int(high_count),
            "at_risk_value": float(total_at_risk_value),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_top_expiring_items(self) -> str:
        """Get top 10 expiring items"""
        top = self.inventory.nsmallest(10, 'days_to_expiry')[
            ['batch_number', 'medication_id', 'quantity_on_hand', 'days_to_expiry', 'risk_level']
        ]
        return top.to_string()


class TransferOptimizer:
    """Agent that recommends optimal transfer decisions"""
    
    def __init__(self):
        data = PharmacyDataLoader.load_all_data()
        self.transfers = data['transfers']
        self.inventory = data['inventory']
        self.facilities = data['facilities']
        self.medications = data['medications']
    
    def analyze(self) -> dict:
        """Analyze transfer opportunities and recommend decisions"""
        
        if self.transfers.empty:
            return {"error": "No transfer data available"}
        
        # Analyze pending transfers
        pending = self.transfers[self.transfers['transfer_status'] == 'PENDING']
        completed = self.transfers[self.transfers['transfer_status'] == 'COMPLETED']
        
        # Cost analysis
        total_potential_savings = pending['total_medication_value'].sum() * 0.15  # 15% potential savings
        avg_benefit_score = pending['cost_benefit_score'].mean() if 'cost_benefit_score' in pending.columns else 0.75
        
        # Build analysis context
        transfer_summary = f"""
        TRANSFER COORDINATION ANALYSIS:
        - Total Transfers: {len(self.transfers)}
        - Pending Transfers: {len(pending)}
        - Completed Transfers: {len(completed)}
        - Total Potential Savings: ${total_potential_savings:,.2f}
        - Average Benefit Score: {avg_benefit_score:.2f}
        
        Top Transfer Opportunities:
        {self._get_top_transfers(pending)}
        
        Compliance Status:
        - Transfers Requiring Review: {len(pending[pending['cost_benefit_score'] < 0.7]) if 'cost_benefit_score' in pending.columns else 0}
        - High-Value Transfers: {len(pending[pending['total_medication_value'] > pending['total_medication_value'].quantile(0.75)]) if not pending.empty else 0}
        """
        
        return {
            "analysis_type": "transfer_optimization",
            "summary": transfer_summary,
            "pending_count": int(len(pending)),
            "potential_savings": float(total_potential_savings),
            "avg_benefit_score": float(avg_benefit_score),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_top_transfers(self, transfers: pd.DataFrame) -> str:
        """Get top transfer opportunities"""
        if transfers.empty:
            return "No pending transfers"
        
        top = transfers.nlargest(5, 'total_medication_value')[
            ['transfer_id', 'medication_id', 'source_facility_id', 'target_facility_id', 
             'quantity_transferred', 'total_medication_value']
        ]
        return top.to_string()


class DemandForecaster:
    """Agent that analyzes demand forecasts and makes recommendations"""
    
    def __init__(self):
        data = PharmacyDataLoader.load_all_data()
        self.forecast = data['forecast']
        self.medications = data['medications']
    
    def analyze(self) -> dict:
        """Analyze demand forecasts and identify anomalies"""
        
        if self.forecast.empty:
            return {"error": "No forecast data available"}
        
        # Forecast analysis
        critical_urgency = len(self.forecast[self.forecast['urgency_level'] == 'CRITICAL'])
        high_urgency = len(self.forecast[self.forecast['urgency_level'] == 'HIGH'])
        anomalies_total = self.forecast['anomalies_detected'].sum()
        avg_confidence = self.forecast['forecast_confidence'].mean()
        
        # Build analysis context
        forecast_summary = f"""
        DEMAND FORECAST ANALYSIS:
        - Total Forecasts: {len(self.forecast)}
        - Critical Urgency: {critical_urgency} medications
        - High Urgency: {high_urgency} medications
        - Total Anomalies Detected: {int(anomalies_total)}
        - Average Forecast Confidence: {avg_confidence:.2%}
        
        High-Risk Medications (Stockout Risk):
        {self._get_high_risk_medications()}
        
        Recommendations:
        - Medications Needing Immediate Action: {critical_urgency + high_urgency}
        - External Signals Affecting Demand: {self.forecast['external_signals'].notna().sum()}
        """
        
        return {
            "analysis_type": "demand_forecast",
            "summary": forecast_summary,
            "critical_urgency": int(critical_urgency),
            "high_urgency": int(high_urgency),
            "anomalies_detected": int(anomalies_total),
            "avg_confidence": float(avg_confidence),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_high_risk_medications(self) -> str:
        """Get medications with highest risk"""
        critical = self.forecast[self.forecast['urgency_level'].isin(['CRITICAL', 'HIGH'])]
        if critical.empty:
            return "No high-risk medications"
        
        high_risk = critical.nlargest(5, 'anomalies_detected')[
            ['medication_id', 'urgency_level', 'current_inventory', 'forecast_confidence', 'anomalies_detected']
        ]
        return high_risk.to_string()


# ============================================
# CrewAI Agent Definitions
# ============================================

class PharmacyCrewAgents:
    """Define CrewAI agents for pharmacy operations"""
    
    @staticmethod
    def create_risk_assessment_agent():
        """Risk Assessment Agent - analyzes expiration risks"""
        return Agent(
            role="Risk Assessment Specialist",
            goal="Identify expiration risks and recommend transfer/disposal actions to minimize medication waste",
            backstory="Expert pharmacist with 15 years of inventory management experience. Specializes in risk mitigation.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
    
    @staticmethod
    def create_optimization_agent():
        """Optimization Agent - recommends transfer decisions"""
        return Agent(
            role="Supply Chain Optimizer",
            goal="Analyze transfer opportunities to minimize costs and optimize inventory distribution across facilities",
            backstory="Logistics engineer with expertise in pharmaceutical supply chain optimization. Focuses on cost-benefit analysis.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
    
    @staticmethod
    def create_demand_analyst_agent():
        """Demand Analyst Agent - interprets forecasts"""
        return Agent(
            role="Demand Forecast Analyst",
            goal="Analyze demand predictions and identify potential stockout risks and demand anomalies",
            backstory="Data scientist specializing in pharmaceutical demand patterns. Expert in identifying anomalies and external signals.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )
    
    @staticmethod
    def create_report_agent():
        """Report Generation Agent - creates executive summaries"""
        return Agent(
            role="Executive Report Generator",
            goal="Create comprehensive, actionable reports summarizing all analyses and recommendations",
            backstory="Business analyst who excels at translating complex data into actionable insights for pharmacy leadership.",
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )


class PharmacyCrew:
    """Crew of agents analyzing pharmaceutical inventory operations"""
    
    def __init__(self):
        self.risk_analyst_data = ExpirationRiskAnalyst().analyze()
        self.optimizer_data = TransferOptimizer().analyze()
        self.forecaster_data = DemandForecaster().analyze()
    
    def run_risk_assessment(self) -> dict:
        """Run risk assessment analysis"""
        
        agent = PharmacyCrewAgents.create_risk_assessment_agent()
        
        task = Task(
            description=f"""
            Analyze the following expiration risk data and provide:
            1. Root causes of expiration risks
            2. Recommended actions (transfers, disposals, donations)
            3. Timeline for action
            4. Estimated impact (cost savings, waste reduction)
            
            Provide specific, actionable recommendations.
            
            DATA: {json.dumps(self.risk_analyst_data, indent=2)}
            """,
            expected_output="Detailed risk assessment with specific recommendations",
            agent=agent,
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        return {
            "analysis": self.risk_analyst_data,
            "recommendations": str(result),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_optimization_analysis(self) -> dict:
        """Run transfer optimization analysis"""
        
        agent = PharmacyCrewAgents.create_optimization_agent()
        
        task = Task(
            description=f"""
            Analyze transfer opportunities and provide:
            1. Top 5 transfer recommendations with cost-benefit analysis
            2. Facility balancing strategies
            3. Priority ranking (urgency, ROI, compliance)
            4. Implementation timeline
            5. Risk mitigation strategies
            
            Focus on maximizing savings while maintaining compliance.
            
            DATA: {json.dumps(self.optimizer_data, indent=2)}
            """,
            expected_output="Prioritized transfer recommendations with financial impact",
            agent=agent,
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        return {
            "analysis": self.optimizer_data,
            "recommendations": str(result),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_demand_analysis(self) -> dict:
        """Run demand forecast analysis"""
        
        agent = PharmacyCrewAgents.create_demand_analyst_agent()
        
        task = Task(
            description=f"""
            Analyze demand forecasts and provide:
            1. Medications with stockout risk (with urgency scores)
            2. Anomaly analysis and root causes
            3. External signals impact on demand (weather, disease outbreaks, etc.)
            4. Reorder recommendations with quantities and timing
            5. Confidence assessment of forecasts
            
            Identify actionable insights for procurement teams.
            
            DATA: {json.dumps(self.forecaster_data, indent=2)}
            """,
            expected_output="Demand analysis with stockout risk assessment and reorder recommendations",
            agent=agent,
        )
        
        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        
        return {
            "analysis": self.forecaster_data,
            "recommendations": str(result),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_full_analysis(self) -> dict:
        """Run comprehensive multi-agent analysis"""
        
        risk_agent = PharmacyCrewAgents.create_risk_assessment_agent()
        opt_agent = PharmacyCrewAgents.create_optimization_agent()
        demand_agent = PharmacyCrewAgents.create_demand_analyst_agent()
        report_agent = PharmacyCrewAgents.create_report_agent()
        
        # Task 1: Risk Assessment
        risk_task = Task(
            description=f"""Analyze expiration risks in inventory. DATA: {json.dumps(self.risk_analyst_data, indent=2)}""",
            expected_output="Risk assessment summary",
            agent=risk_agent,
        )
        
        # Task 2: Optimization
        opt_task = Task(
            description=f"""Analyze transfer opportunities. DATA: {json.dumps(self.optimizer_data, indent=2)}""",
            expected_output="Transfer optimization recommendations",
            agent=opt_agent,
        )
        
        # Task 3: Demand Analysis
        demand_task = Task(
            description=f"""Analyze demand forecasts. DATA: {json.dumps(self.forecaster_data, indent=2)}""",
            expected_output="Demand analysis and reorder recommendations",
            agent=demand_agent,
        )
        
        # Task 4: Executive Report
        report_task = Task(
            description="""
            Create an executive report synthesizing all three analyses:
            1. Executive Summary (1 paragraph)
            2. Key Findings (3-5 bullets per area)
            3. Top 10 Recommendations (prioritized)
            4. Financial Impact Summary
            5. Implementation Timeline
            
            Make it actionable for pharmacy leadership.
            """,
            expected_output="Executive report with integrated recommendations",
            agent=report_agent,
        )
        
        crew = Crew(
            agents=[risk_agent, opt_agent, demand_agent, report_agent],
            tasks=[risk_task, opt_task, demand_task, report_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        return {
            "risk_analysis": self.risk_analyst_data,
            "optimization_analysis": self.optimizer_data,
            "demand_analysis": self.forecaster_data,
            "executive_report": str(result),
            "timestamp": datetime.now().isoformat()
        }
