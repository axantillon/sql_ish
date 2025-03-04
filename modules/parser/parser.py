"""
parser.py - SQL-ish parser for simple SQL-like statements

This module implements a parser for a simplified SQL-like language.
It supports basic SQL operations like SELECT, INSERT, CREATE TABLE, etc.

Changes:
- Initial implementation of SQL-ish parser
- Support for SELECT, INSERT, CREATE TABLE statements
- WHERE clause parsing and condition building
- Fixed parse_query to handle CREATE TABLE correctly
- Fixed parse_insert to handle INSERT queries correctly
- Updated as part of package restructuring
- Fixed parse_select to parse WHERE clause into a Condition object
- Added parse_update function to support UPDATE commands
"""

import re
from modules.core.where import Condition, Comparison, And, Or, Not

def parse_create_table(query):
    """
    Parse a CREATE TABLE statement.
    
    Format: CREATE TABLE table_name (col1, col2, ...)
    
    Args:
        query (str): The CREATE TABLE query
        
    Returns:
        tuple: (table_name, columns)
    """
    # Extract table name and column definitions
    match = re.search(r'CREATE\s+TABLE\s+(\w+)\s*\((.*)\)', query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid CREATE TABLE syntax")
    
    table_name = match.group(1)
    columns_str = match.group(2)
    
    # Parse columns
    columns = [col.strip() for col in columns_str.split(',')]
    
    return (table_name, columns)

def parse_insert(query):
    """
    Parse an INSERT statement.
    
    Format: INSERT INTO table_name VALUES (val1, val2, ...)
    
    Args:
        query (str): The INSERT query
        
    Returns:
        tuple: (table_name, values)
    """
    # Extract table name and values
    match = re.search(r'INSERT\s+INTO\s+(\w+)\s+VALUES\s*\((.*)\)', query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid INSERT syntax")
    
    table_name = match.group(1)
    values_str = match.group(2)
    
    # Parse values, handling quoted strings
    values = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in values_str:
        if char in ['"', "'"] and (not current or current[-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
                current += char
            elif quote_char == char:
                in_quotes = False
                quote_char = None
                current += char
            else:
                # Different quote character inside a string
                current += char
        elif char == ',' and not in_quotes:
            values.append(current.strip())
            current = ""
        else:
            current += char
    
    if current:
        values.append(current.strip())
    
    # Clean up values
    cleaned_values = []
    for val in values:
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            # String value - remove quotes
            cleaned_values.append(val[1:-1])
        elif val.lower() == 'null':
            # NULL value
            cleaned_values.append(None)
        else:
            # Try to convert to numeric
            try:
                if '.' in val:
                    cleaned_values.append(float(val))
                else:
                    cleaned_values.append(int(val))
            except ValueError:
                # Keep as string if not numeric
                cleaned_values.append(val)
                
    return (table_name, cleaned_values)

def parse_select(query):
    """
    Parse a SELECT statement.
    
    Format: SELECT col1, col2, ... FROM table_name WHERE condition
    
    Args:
        query (str): The SELECT query
        
    Returns:
        tuple: (table_name, columns, condition)
    """
    # Extract columns and table name
    match = re.search(r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?', query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid SELECT syntax")
    
    columns_str = match.group(1)
    table_name = match.group(2)
    condition_str = match.group(3) if match.group(3) else None
    
    # Parse columns
    if columns_str.strip() == '*':
        columns = None  # All columns
    else:
        columns = [col.strip() for col in columns_str.split(',')]
    
    # Parse WHERE clause if present
    condition = None
    if condition_str:
        condition = parse_where_clause(condition_str)
    
    return (table_name, columns, condition)

def parse_where_clause(where_clause):
    """
    Parse a WHERE clause into a condition tree.
    
    Args:
        where_clause (str): The WHERE clause to parse
        
    Returns:
        Condition: The parsed condition tree
    """
    # TODO: Implement a proper parser for WHERE clauses
    # For now, we'll just handle simple conditions
    
    # Check for AND/OR
    if ' AND ' in where_clause.upper():
        left, right = where_clause.split(' AND ', 1)
        return And(parse_where_clause(left), parse_where_clause(right))
    
    if ' OR ' in where_clause.upper():
        left, right = where_clause.split(' OR ', 1)
        return Or(parse_where_clause(left), parse_where_clause(right))
    
    # Check for NOT
    if where_clause.upper().startswith('NOT '):
        return Not(parse_where_clause(where_clause[4:]))
    
    # Simple comparison
    for op in ['=', '<>', '!=', '>', '<', '>=', '<=']:
        if op in where_clause:
            col, val = where_clause.split(op, 1)
            col = col.strip()
            val = val.strip()
            
            # Handle quoted values
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]  # Remove the quotes
            elif val.lower() == 'null':
                val = None
            else:
                # Try to convert to numeric if possible
                try:
                    if '.' in val:
                        val = float(val)
                    else:
                        val = int(val)
                except ValueError:
                    # Keep as string if not numeric
                    pass
                    
            return Comparison(col, op, val)
    
    raise ValueError(f"Invalid WHERE clause: {where_clause}")

def parse_update(query):
    """
    Parse an UPDATE statement.
    
    Format: UPDATE table_name SET col1 = val1, col2 = val2, ... WHERE condition
    
    Args:
        query (str): The UPDATE query
        
    Returns:
        tuple: (table_name, updates, condition)
    """
    # Extract table name, SET clause, and WHERE clause
    match = re.search(r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?$', query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid UPDATE syntax")
    
    table_name = match.group(1)
    set_clause = match.group(2)
    condition_str = match.group(3) if match.group(3) else None
    
    # Parse SET clause
    updates = {}
    set_items = set_clause.split(',')
    for item in set_items:
        if '=' not in item:
            raise ValueError(f"Invalid SET clause: {item}")
        
        col, val = item.split('=', 1)
        col = col.strip()
        val = val.strip()
        
        # Handle quoted strings
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]  # Remove quotes
        elif val.lower() == 'null':
            val = None
        else:
            # Try to convert to numeric
            try:
                if '.' in val:
                    val = float(val)
                else:
                    val = int(val)
            except ValueError:
                # Keep as string if not numeric
                pass
                
        updates[col] = val
    
    # Parse WHERE clause if present
    condition = None
    if condition_str:
        condition = parse_where_clause(condition_str)
    
    return (table_name, updates, condition)

def parse_delete(query):
    """
    Parse a DELETE statement.
    
    Format: DELETE FROM table_name WHERE condition
    
    Args:
        query (str): The DELETE query
        
    Returns:
        tuple: (table_name, condition)
    """
    # Extract table name and WHERE clause
    match = re.search(r'DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*))?$', query, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid DELETE syntax")
    
    table_name = match.group(1)
    condition_str = match.group(2) if match.group(2) else None
    
    # Parse WHERE clause if present
    condition = None
    if condition_str:
        condition = parse_where_clause(condition_str)
    
    return (table_name, condition)

def parse_query(query):
    """
    Parse a SQL-ish query and determine its type.
    
    Args:
        query (str): The SQL-ish query
        
    Returns:
        tuple: (query_type, parsed_data)
    """
    query = query.strip()
    
    if query.upper().startswith('CREATE TABLE'):
        return ('CREATE', parse_create_table(query))
    
    elif query.upper().startswith('INSERT INTO'):
        return ('INSERT', parse_insert(query))
    
    elif query.upper().startswith('SELECT'):
        return ('SELECT', parse_select(query))
    
    elif query.upper().startswith('UPDATE'):
        return ('UPDATE', parse_update(query))
        
    elif query.upper().startswith('DELETE FROM'):
        return ('DELETE', parse_delete(query))
    
    else:
        raise ValueError(f"Unsupported query type: {query}") 