"""
Database Module
Data loading and management for pharmaceutical inventory
"""

from .data_loader import (
    SyntheticDataLoader,
    get_data_loader
)

__all__ = [
    'SyntheticDataLoader',
    'get_data_loader'
]
