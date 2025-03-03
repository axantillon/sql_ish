"""
sql_ish.engine - SQL engine module for SQL-ish

This module provides the database engine for SQL-ish.
It exposes the Database class for creating and interacting with databases.

Changes:
- Initial implementation of the engine module
- Expose the Database class and join functions
- Updated as part of package restructuring
"""

from modules.engine.db import Database
from modules.engine.join import (
    inner_join,
    left_join,
    right_join,
    full_join
)

__all__ = [
    'Database',
    'inner_join',
    'left_join',
    'right_join',
    'full_join'
] 