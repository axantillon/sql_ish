"""
sql_ish.core - Core data structures for SQL-ish

This module provides the core data structures for SQL-ish.
It includes the Table class and condition classes for WHERE clauses.

Changes:
- Initial implementation of the core module
- Expose the Table class and WHERE condition classes
- Updated as part of package restructuring
"""

from sql_ish.core.table import Table
from sql_ish.core.where import (
    Condition,
    Comparison,
    And,
    Or,
    Not,
    build_condition_function
)

__all__ = [
    'Table',
    'Condition',
    'Comparison',
    'And',
    'Or',
    'Not',
    'build_condition_function'
] 