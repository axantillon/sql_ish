"""
table_utils.py - Utility functions for working with tables in SQL-ish

This module provides utility functions for working with tables in SQL-ish.

Changes:
- Initial implementation of the table_utils module
- Added normalize_table_name function for consistent table name handling
"""

def normalize_table_name(name):
    """
    Normalize table name to ensure consistent access.
    
    Args:
        name: Table name to normalize
        
    Returns:
        str: Normalized table name
    """
    if name is None:
        return None
    return str(name).strip().lower() 