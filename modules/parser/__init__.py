"""
sql_ish.parser - SQL parsing module for SQL-ish

This module provides SQL parsing functionality for the SQL-ish package.
It exposes functions for parsing SQL-ish queries.

Changes:
- Initial implementation of the parser module
- Expose the parse_query function for external use
- Updated as part of package restructuring
- Added parse_update and parse_delete functions
"""

from modules.parser.parser import (
    parse_query,
    parse_create_table,
    parse_insert,
    parse_select,
    parse_where_clause,
    parse_update,
    parse_delete
)

__all__ = [
    'parse_query',
    'parse_create_table', 
    'parse_insert',
    'parse_select',
    'parse_where_clause',
    'parse_update',
    'parse_delete'
] 