"""
sql_utils.py - SQL-ish utility functions

This module provides utility functions for working with SQL-ish queries.

Changes:
- Initial implementation of SQL utility functions
- Added smart_split_sql function for parsing SQL scripts
"""

def smart_split_sql(content):
    """
    Split SQL content by semicolons, respecting string literals.
    
    Args:
        content (str): SQL content to split
        
    Returns:
        list: SQL queries split by semicolons
    """
    queries = []
    current_query = ""
    in_string = False
    string_char = None
    
    i = 0
    while i < len(content):
        char = content[i]
        
        # Handle string literals
        if char in ['"', "'"]:
            if not in_string:
                in_string = True
                string_char = char
            elif string_char == char:
                # Check for escaped quotes
                if i > 0 and content[i-1] == '\\':
                    pass  # This is an escaped quote
                else:
                    in_string = False
        
        # Only treat semicolons as separators if not in a string
        elif char == ';' and not in_string:
            if current_query.strip():
                queries.append(current_query.strip())
            current_query = ""
            i += 1
            continue
        
        current_query += char
        i += 1
    
    # Add the last query if there is one
    if current_query.strip():
        queries.append(current_query.strip())
    
    return queries 