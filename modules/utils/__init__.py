"""
utils package - Utility functions for SQL-ish

This package contains utility modules for the SQL-ish package.

Changes:
- Initial implementation of the utils package
- Added sql_utils module with SQL parsing utilities
- Added format_utils module with result formatting utilities
"""

from modules.utils.sql_utils import smart_split_sql
from modules.utils.format_utils import format_result

__all__ = ['smart_split_sql', 'format_result'] 