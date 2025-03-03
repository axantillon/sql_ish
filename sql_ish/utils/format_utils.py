"""
format_utils.py - Formatting utilities for SQL-ish

This module provides utilities for formatting query results in a readable way.

Changes:
- Initial implementation of the format_utils module
- Added format_result function for nicely formatting query results
- Enhanced formatting with improved table layout and value representation
- Added support for NULL values and better handling of various data types
- Added truncation for large results
"""

def format_result(result, query_type=None, max_column_width=40, max_rows=200):
    """
    Format a query result for display.
    
    Args:
        result: The query result
        query_type: Type of query (optional)
        max_column_width: Maximum width for columns before truncation
        max_rows: Maximum number of rows to display
        
    Returns:
        str: Formatted result string
    """
    if hasattr(result, 'rows') and hasattr(result, 'columns'):
        # Table result (likely from SELECT)
        if not result.rows:
            return "No rows returned"
        
        # Extract data
        columns = result.columns
        rows = result.rows
        
        # Limit rows for display
        show_truncated = False
        if len(rows) > max_rows:
            rows = rows[:max_rows]
            show_truncated = True
            
        # Format columns and rows
        formatted_rows = []
        for row in rows:
            formatted_row = []
            for val in row:
                if val is None:
                    formatted_row.append("NULL")
                else:
                    val_str = str(val)
                    # Truncate long values
                    if len(val_str) > max_column_width:
                        val_str = val_str[:max_column_width - 3] + "..."
                    formatted_row.append(val_str)
            formatted_rows.append(formatted_row)
            
        # Find column widths
        col_widths = []
        for i, col in enumerate(columns):
            # Start with column name width
            width = len(str(col))
            # Check all row values
            for row in formatted_rows:
                if i < len(row):
                    width = max(width, len(str(row[i])))
            col_widths.append(min(width + 2, max_column_width + 2))  # Add padding
        
        # Build header
        header = "| " + " | ".join(str(col).ljust(width-2) for col, width in zip(columns, col_widths)) + " |"
        separator = "+" + "+".join("-" * width for width in col_widths) + "+"
        
        # Build rows
        row_strings = []
        for row in formatted_rows:
            row_str = "| " + " | ".join(str(val).ljust(width-2) for val, width in zip(row, col_widths)) + " |"
            row_strings.append(row_str)
        
        # Combine everything
        result_str = "\n".join([separator, header, separator] + row_strings + [separator])
        
        # Add truncation notice if needed
        if show_truncated:
            result_str += f"\nShowing {max_rows} of {len(result.rows)} rows."
            
        return result_str
    
    # For INSERT results (typically number of rows affected)
    if query_type == 'INSERT' and isinstance(result, int):
        if result == 1:
            return "Row inserted successfully"
        else:
            return f"{result} rows inserted successfully"
    
    # For CREATE TABLE results
    if query_type == 'CREATE' and (result is None or result == True):
        return "Table created successfully"
    
    # For other types of results
    return str(result)

def format_error(error_msg):
    """
    Format an error message for display.
    
    Args:
        error_msg (str): The error message
        
    Returns:
        str: Formatted error message
    """
    return f"ERROR: {error_msg}" 