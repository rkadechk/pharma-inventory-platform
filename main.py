"""
Main Crew Execution
Demonstrates the pharmaceutical inventory optimization platform in action
"""

from crewai import Crew, Task
from datetime import datetime
import json
from pathlib import Path

from agents.pharma_agents import create_pharma_agents
from agents.config import get_claude_client, test_claude_connection
from tools.inventory_tools import create_inventory_tools
from tools.transfer_tools import create_transfer_tools
from tools.forecasting_tools import create_forecasting_tools
from database.data_loader import get_data_loader


def create_crew_with_tasks():
    """
    Create and execute a CrewAI crew with three specialized agents
    and their sequential tasks
    
    Returns:
        Crew instance ready for execution
    """
    
    # Initialize agents
    expiration_manager, transfer_coordinator, forecasting_analyst = create_pharma_agents()
    
    # Initialize tools
    inventory_tools = create_inventory_tools()
    transfer_tools = create_transfer_tools()
    forecasting_tools = create_forecasting_tools()
    
    # Assign tools to agents
    expiration_manager.tools = [
        inventory_tools.query_inventory,
        inventory_tools.get_expiring_medications,
        inventory_tools.check_facility_capacity,
        inventory_tools.create_alert
    ]
    
    transfer_coordinator.tools = [
        transfer_tools.find_transfer_matches,
        transfer_tools.calculate_transfer_cost,
        transfer_tools.create_transfer_proposal,
        transfer_tools.check_regulatory_constraints,
        transfer_tools.approve_transfer
    ]
    
    forecasting_analyst.tools = [
        forecasting_tools.run_demand_forecast,
        forecasting_tools.detect_demand_anomaly,
        forecasting_tools.get_external_signals,
        forecasting_tools.assess_stockout_risk,
        forecasting_tools.recommend_replenishment
    ]
    
    # Define tasks
    task_1 = Task(
        description="""
        Analyze the pharmaceutical inventory across all facilities.
        Identify medications expiring within 14 days and alert facility managers.
        Check storage capacity at each facility and flag any that are over 80% full.
        Create priority alerts for items expiring within 7 days.
        
        Report should include:
        1. List of medications expiring within 14 days (with quantities and facilities)
        2. Total inventory at-risk value
        3. Facilities with high capacity utilization
        4. Recommended actions for waste prevention
        """,
        agent=expiration_manager,
        expected_output="Expiration analysis report with prioritized actions"
    )
    
    task_2 = Task(
        description="""
        Based on the expiration analysis from the Expiration Manager,
        find transfer opportunities to redistribute surplus and shortage items
        across facilities.
        
        For each viable transfer:
        1. Calculate logistics cost
        2. Check regulatory constraints
        3. Create transfer proposals
        4. Identify compliance requirements
        
        Prioritize transfers that:
        - Prevent medication waste (expiring items)
        - Address shortage situations (coverage < 7 days)
        - Are cost-effective
        
        Report should include:
        1. List of recommended transfers with cost analysis
        2. Regulatory constraints and compliance requirements
        3. Estimated waste prevention value
        4. Implementation timeline
        """,
        agent=transfer_coordinator,
        expected_output="Transfer coordination plan with proposals and cost analysis"
    )
    
    task_3 = Task(
        description="""
        Assess demand patterns and future requirements across all facilities.
        Using the transfer proposals from the Transfer Coordinator,
        identify any remaining stockout risks or inventory imbalances.
        
        For each critical medication:
        1. Run 30-day demand forecast
        2. Detect consumption anomalies
        3. Check for external signals affecting demand
        4. Assess stockout risk
        5. Recommend replenishment quantities and timing
        
        Report should include:
        1. Demand forecasts for critical medications
        2. Identified anomalies and root causes
        3. External factors affecting demand
        4. Stockout risk assessment
        5. Replenishment recommendations with priority levels
        """,
        agent=forecasting_analyst,
        expected_output="Demand analysis and replenishment strategy report"
    )
    
    # Create crew
    crew = Crew(
        agents=[expiration_manager, transfer_coordinator, forecasting_analyst],
        tasks=[task_1, task_2, task_3],
        verbose=False,
        memory=True
    )
    
    return crew


def validate_prerequisites():
    """Validate that all prerequisites are met"""
    
    print("\n" + "="*70)
    print("VALIDATING PREREQUISITES")
    print("="*70)
    
    checks = []
    
    # Check 1: Claude API configuration
    print("\n1️⃣ Checking Claude API configuration...")
    try:
        is_configured = test_claude_connection()
        if is_configured:
            checks.append(("Claude API", True))
            print("   ✅ Claude API is configured and accessible")
        else:
            checks.append(("Claude API", False))
            print("   ❌ Claude API not configured")
            print("      → Set ANTHROPIC_API_KEY in .env file")
    except Exception as e:
        checks.append(("Claude API", False))
        print(f"   ❌ Claude API error: {str(e)}")
    
    # Check 2: Data loading
    print("\n2️⃣ Checking synthetic data...")
    try:
        loader = get_data_loader()
        data = loader.load_csv_files()
        checks.append(("Synthetic Data", len(data) > 0))
        if len(data) > 0:
            print(f"   ✅ Loaded {len(data)} data tables")
        else:
            print("   ❌ No data tables loaded")
    except Exception as e:
        checks.append(("Synthetic Data", False))
        print(f"   ❌ Data loading error: {str(e)}")
    
    # Check 3: Agents
    print("\n3️⃣ Checking agents...")
    try:
        from agents.pharma_agents import create_pharma_agents
        agents = create_pharma_agents()
        checks.append(("Agents", len(agents) == 3))
        if len(agents) == 3:
            print(f"   ✅ Initialized 3 agents")
            for agent in agents:
                print(f"      - {agent.role}")
        else:
            print(f"   ❌ Expected 3 agents, got {len(agents)}")
    except Exception as e:
        checks.append(("Agents", False))
        print(f"   ❌ Agent initialization error: {str(e)}")
    
    # Summary
    print("\n" + "-"*70)
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    print(f"Prerequisites: {passed}/{total} checks passed")
    print("-"*70)
    
    return all(result for _, result in checks)


def run_example():
    """Run example crew execution"""
    
    print("\n" + "="*70)
    print("PHARMACEUTICAL INVENTORY OPTIMIZATION PLATFORM")
    print("Phase 1 - Single Cycle Execution")
    print("="*70)
    
    # Validate prerequisites
    if not validate_prerequisites():
        print("\n❌ Prerequisites not met. Cannot proceed.")
        print("   Please:")
        print("   1. Set ANTHROPIC_API_KEY in .env file")
        print("   2. Ensure synthetic data is in data-generation/synthetic_data/")
        return
    
    # Create crew
    print("\n📋 Creating crew and tasks...")
    crew = create_crew_with_tasks()
    
    # Execute
    print("\n🚀 Starting crew execution...")
    print("-"*70)
    
    try:
        result = crew.kickoff()
        
        print("\n" + "="*70)
        print("EXECUTION COMPLETE")
        print("="*70)
        print("\n📊 Results:")
        print(result)
        
        # Save results
        output_file = Path("crew_execution_results.json")
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "execution_summary": str(result),
                "status": "completed"
            }, f, indent=2)
        
        print(f"\n✅ Results saved to {output_file}")
        
    except Exception as e:
        print(f"\n❌ Execution error: {str(e)}")
        print("\nDebug information:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Message: {str(e)}")


if __name__ == "__main__":
    """
    Main entry point for the pharmaceutical inventory optimization platform.
    
    This script:
    1. Validates all prerequisites (API key, data, agents)
    2. Creates a CrewAI crew with 3 specialized agents
    3. Defines 3 sequential tasks (expiration → transfer → forecasting)
    4. Executes the crew and outputs results
    
    Usage:
        # Basic run
        python main.py
        
        # With API key set
        export ANTHROPIC_API_KEY="sk-ant-..."
        python main.py
    """
    
    run_example()
