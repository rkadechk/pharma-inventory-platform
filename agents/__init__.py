"""Agents Module - Pharmaceutical Inventory Platform"""

from .config import test_claude_connection, get_claude_client, CLAUDE_MODEL

# Note: CrewAI agents (expiration_manager, transfer_coordinator, forecasting_analyst)
# are not imported here as they require CrewAI library
# See agents/pharma_agents.py for original CrewAI implementation

# Import actual test agents
from .demand_agent import DemandForecastingAgent
from .inventory_agent import InventoryOptimizationAgent
from .supply_chain_agent import SupplyChainCoordinationAgent

__all__ = [
    'test_claude_connection',
    'get_claude_client',
    'CLAUDE_MODEL',
    'DemandForecastingAgent',
    'InventoryOptimizationAgent',
    'SupplyChainCoordinationAgent'
]
