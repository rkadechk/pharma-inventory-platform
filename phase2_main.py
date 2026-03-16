"""
Phase 2 Main Entry Point

Demonstrates full pharmaceutical inventory optimization system with all three agents.
Loads synthetic data and executes integrated agent pipeline.
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pharma_optimization.log')
    ]
)

logger = logging.getLogger(__name__)

# Import agents and orchestrator
from agents.models import Supplier
from agents.orchestrator import PharmaceuticalInventoryOrchestrator
from database.data_loader import DataLoader


class Phase2MainExecutor:
    """
    Phase 2 main executor: Runs the full pharmaceutical inventory optimization.
    """
    
    def __init__(self, db_path: str = "pharma_dev.db"):
        self.db_path = db_path
        self.data_loader = DataLoader(db_path)
        self.orchestrator = PharmaceuticalInventoryOrchestrator()
        
        logger.info("Phase 2 Main Executor initialized")
    
    async def run_full_optimization(self) -> Dict:
        """
        Execute full optimization pipeline.
        
        Returns:
            Dictionary with results, metrics, and action plan
        """
        
        logger.info("\n" + "="*80)
        logger.info("PHASE 2 - PHARMACEUTICAL INVENTORY OPTIMIZATION")
        logger.info("Starting integrated multi-agent system")
        logger.info("="*80)
        
        try:
            # Step 1: Load data
            logger.info("\n[STEP 1] Loading synthetic data...")
            facility_inventory, consumption_history, suppliers, transfer_costs, external_signals = \
                await self._load_data()
            
            logger.info(f"✓ Loaded data:")
            logger.info(f"  - Facility inventory: {len(facility_inventory)} batch records")
            logger.info(f"  - Consumption history: {len(consumption_history)} transaction records")
            logger.info(f"  - Suppliers: {len(suppliers)}")
            logger.info(f"  - Facility transfer routes: {len(transfer_costs)}")
            
            # Step 2: Execute orchestrator
            logger.info("\n[STEP 2] Executing orchestrator with 3 core agents...")
            
            results = await self.orchestrator.execute_full_optimization(
                facility_inventory=facility_inventory,
                consumption_history=consumption_history,
                suppliers=suppliers,
                transfer_cost_matrix=transfer_costs,
                external_signals=external_signals
            )
            
            # Step 3: Display results
            logger.info("\n[STEP 3] Processing results...")
            
            await self._display_results(results)
            
            # Step 4: Save results
            logger.info("\n[STEP 4] Saving results...")
            
            await self._save_results(results)
            
            logger.info("\n" + "="*80)
            logger.info("PHASE 2 OPTIMIZATION COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            
            return results
        
        except Exception as e:
            logger.error(f"Error during optimization: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def _load_data(self) -> tuple:
        """
        Load data from database.
        """
        
        # Load from database
        try:
            facility_inventory = self.data_loader.load_all_inventory()
            consumption_history = self.data_loader.load_consumption_history()
            suppliers = self.data_loader.load_suppliers()
            external_signals = self.data_loader.load_external_signals()
        except Exception as e:
            logger.warning(f"Could not load from database: {e}. Using synthetic data instead.")
            facility_inventory, consumption_history, suppliers, external_signals = \
                self._generate_synthetic_data()
        
        # Build transfer cost matrix
        transfer_costs = self._build_transfer_cost_matrix(facility_inventory)
        
        return facility_inventory, consumption_history, suppliers, transfer_costs, external_signals
    
    def _generate_synthetic_data(self) -> tuple:
        """
        Generate synthetic data for demo if database not available.
        """
        
        logger.info("Generating synthetic data for demo...")
        
        # Facilities
        facilities = ['FACILITY_A', 'FACILITY_B', 'FACILITY_C', 'FACILITY_D']
        medications = ['MEDICATION_001', 'MEDICATION_002', 'MEDICATION_003', 
                      'MEDICATION_004', 'MEDICATION_005']
        
        # Create synthetic facility inventory
        inventory_records = []
        for facility in facilities:
            for med in medications:
                batch_id = f"{facility}_{med}_BATCH_{np.random.randint(1000, 9999)}"
                quantity = np.random.randint(100, 500)
                expiry_date = datetime.now() + timedelta(days=np.random.randint(30, 365))
                
                inventory_records.append({
                    'facility_id': facility,
                    'facility_name': f"{facility}_Hospital",
                    'medication_id': med,
                    'batch_id': batch_id,
                    'quantity': quantity,
                    'expiry_date': expiry_date,
                    'receive_date': datetime.now() - timedelta(days=np.random.randint(30, 180)),
                    'unit_price': np.random.uniform(10, 50)
                })
        
        facility_inventory = pd.DataFrame(inventory_records)
        
        # Create synthetic consumption history
        consumption_records = []
        for med in medications:
            for day_offset in range(-30, 0):
                date = datetime.now() + timedelta(days=day_offset)
                quantity = np.random.randint(20, 100)
                
                consumption_records.append({
                    'medication_id': med,
                    'date': date.date(),
                    'quantity_dispensed': quantity
                })
        
        consumption_history = pd.DataFrame(consumption_records)
        
        # Create synthetic suppliers
        suppliers = [
            Supplier(
                supplier_id='SUPPLIER_001',
                supplier_name='PharmaCorp Solutions',
                unit_price=35.00,
                lead_time_days=5,
                minimum_order_quantity=100,
                on_time_delivery_rate=0.95,
                reliability_score=0.85,
                medications_supplied=['MEDICATION_001', 'MEDICATION_002']
            ),
            Supplier(
                supplier_id='SUPPLIER_002',
                supplier_name='MedExpress Inc',
                unit_price=32.50,
                lead_time_days=3,
                minimum_order_quantity=50,
                on_time_delivery_rate=0.98,
                reliability_score=0.92,
                medications_supplied=['MEDICATION_003', 'MEDICATION_004', 'MEDICATION_005']
            ),
            Supplier(
                supplier_id='SUPPLIER_003',
                supplier_name='HealthCare Plus',
                unit_price=40.00,
                lead_time_days=2,
                minimum_order_quantity=200,
                on_time_delivery_rate=0.92,
                reliability_score=0.80,
                medications_supplied=['MEDICATION_001', 'MEDICATION_003', 'MEDICATION_005']
            )
        ]
        
        # External signals (e.g., disease outbreak, seasonal trend)
        external_signals = [
            {
                'signal_type': 'DISEASE_OUTBREAK',
                'affected_medications': ['MEDICATION_001'],
                'start_date': datetime.now().date(),
                'end_date': (datetime.now() + timedelta(days=14)).date(),
                'intensity': 1.5
            }
        ]
        
        logger.info(f"✓ Generated synthetic data:")
        logger.info(f"  - {len(facility_inventory)} inventory records")
        logger.info(f"  - {len(consumption_history)} consumption records")
        logger.info(f"  - {len(suppliers)} suppliers")
        
        return facility_inventory, consumption_history, suppliers, external_signals
    
    def _build_transfer_cost_matrix(self, facility_inventory: pd.DataFrame) -> Dict:
        """
        Build transfer cost matrix between facilities.
        Cost = base + distance factor
        """
        
        facilities = facility_inventory['facility_id'].unique()
        transfer_costs = {}
        
        # Assign approximate distances (in miles) between facilities
        facility_distances = {
            ('FACILITY_A', 'FACILITY_B'): 25,
            ('FACILITY_A', 'FACILITY_C'): 45,
            ('FACILITY_A', 'FACILITY_D'): 80,
            ('FACILITY_B', 'FACILITY_C'): 35,
            ('FACILITY_B', 'FACILITY_D'): 60,
            ('FACILITY_C', 'FACILITY_D'): 50,
        }
        
        # Build cost matrix (bidirectional)
        for f1 in facilities:
            for f2 in facilities:
                if f1 != f2:
                    key = (f1, f2)
                    distance = 0
                    
                    # Look up distance (make symmetric)
                    if key in facility_distances:
                        distance = facility_distances[key]
                    elif (f2, f1) in facility_distances:
                        distance = facility_distances[(f2, f1)]
                    else:
                        distance = 50  # Default distance
                    
                    # Cost = $500 base + $2 per mile + $0.50 per unit (averaged)
                    base_cost = 500
                    distance_cost = distance * 2
                    transfer_costs[key] = base_cost + distance_cost
        
        return transfer_costs
    
    async def _display_results(self, results: Dict):
        """
        Display optimization results to user.
        """
        
        if results.get('status') != 'completed':
            logger.error(f"Optimization failed: {results.get('error', 'Unknown error')}")
            return
        
        logger.info("\n" + "-"*80)
        logger.info("OPTIMIZATION RESULTS SUMMARY")
        logger.info("-"*80)
        
        # Execution time
        exec_time = results.get('execution_time_seconds', 0)
        logger.info(f"\nExecution Time: {exec_time:.2f} seconds")
        
        # Action Plan Summary
        action_plan = results.get('action_plan', {})
        priority_actions = action_plan.get('priority_actions', [])
        routine_actions = action_plan.get('routine_actions', [])
        risk_alerts = action_plan.get('risk_alerts', [])
        
        logger.info(f"\nAction Plan:")
        logger.info(f"  Priority Actions: {len(priority_actions)}")
        for i, action in enumerate(priority_actions[:3], 1):
            logger.info(f"    {i}. {action.get('type')} - {action.get('medication_id')} "
                       f"(Cost: ${action.get('cost', 0):.2f})")
        
        logger.info(f"  Routine Actions: {len(routine_actions)}")
        logger.info(f"  Risk Alerts: {len(risk_alerts)}")
        
        # Financial Impact
        impact = action_plan.get('total_estimated_impact', {})
        logger.info(f"\nFinancial Impact:")
        logger.info(f"  Disposal Cost: ${impact.get('inventory_disposal_cost', 0):,.2f}")
        logger.info(f"  Transfer Savings: ${impact.get('network_transfer_savings', 0):,.2f}")
        logger.info(f"  Reorder Cost: ${impact.get('supply_reorder_cost', 0):,.2f}")
        logger.info(f"  Net Impact: ${impact.get('net_impact', 0):,.2f}")
        
        # System Metrics
        metrics = results.get('system_metrics')
        if metrics:
            logger.info(f"\nSystem Health Metrics:")
            logger.info(f"  Facilities: {metrics.total_facilities}")
            logger.info(f"  Medications: {metrics.total_medications}")
            logger.info(f"  Stock Value: ${metrics.total_stock_value:,.2f}")
            logger.info(f"  Stock Coverage: {metrics.stock_coverage_days:.1f} days")
            logger.info(f"  System Health: {metrics.system_health_score:.1%}")
        
        # Agent Metrics
        logger.info(f"\nAgent Performance:")
        for agent_name, metrics in results.get('agent_metrics', {}).items():
            logger.info(f"  {agent_name}:")
            logger.info(f"    Decisions: {metrics.get('decisions_made', 0)}")
            logger.info(f"    Avg Confidence: {metrics.get('average_confidence', 0):.2%}")
    
    async def _save_results(self, results: Dict):
        """
        Save results to file.
        """
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Save JSON results
        import json
        
        # Prepare data for JSON serialization
        results_copy = results.copy()
        
        # Convert non-serializable objects
        if 'system_metrics' in results_copy and results_copy['system_metrics']:
            metrics = results_copy['system_metrics']
            results_copy['system_metrics'] = {
                'timestamp': metrics.timestamp.isoformat(),
                'total_facilities': metrics.total_facilities,
                'total_medications': metrics.total_medications,
                'total_stock_value': float(metrics.total_stock_value),
                'stock_coverage_days': float(metrics.stock_coverage_days),
                'system_health_score': float(metrics.system_health_score)
            }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = output_dir / f"optimization_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results_copy, f, indent=2, default=str)
        
        logger.info(f"✓ Results saved to {results_file}")


async def main():
    """
    Main entry point for Phase 2.
    """
    
    executor = Phase2MainExecutor()
    results = await executor.run_full_optimization()
    
    return results


if __name__ == "__main__":
    # Run async main
    results = asyncio.run(main())
    
    # Exit successfully
    logger.info("\nPhase 2 implementation complete. Ready for testing and expansion.")
