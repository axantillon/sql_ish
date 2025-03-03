"""
join.py - SQL JOIN operations for SQL-ish implementation

This module implements various JOIN operations on tables, supporting inner, left, right,
and full outer joins based on set theory principles.

Changes:
- Initial implementation of inner join operation
- Support for different join types (inner, left, right, full)
- Improved column naming in joined tables
- Fixed join functions to handle different column names in left and right tables
- Updated as part of package restructuring
"""

from sql_ish.core.table import Table

def inner_join(left_table, right_table, join_column, right_join_column=None):
    """
    Perform an inner join between two tables based on a common column.
    
    Args:
        left_table (Table): The left table
        right_table (Table): The right table
        join_column (str): The column in the left table to join on
        right_join_column (str, optional): The column in the right table to join on.
                                          If None, uses the same name as join_column.
        
    Returns:
        Table: A new table with the joined data
    """
    # If right_join_column is not specified, use the same name as join_column
    if right_join_column is None:
        # Check if join_column exists in right_table
        if join_column in right_table.columns:
            right_join_column = join_column
        # Check if there's a column with the pattern "table_name.column_name"
        elif f"{left_table.name}_{join_column}" in right_table.columns:
            right_join_column = f"{left_table.name}_{join_column}"
        # Check for a column ending with _id
        elif f"{join_column}_id" in right_table.columns:
            right_join_column = f"{join_column}_id"
        # Check for a column starting with table_name and ending with _id
        elif f"{left_table.name}_id" in right_table.columns:
            right_join_column = f"{left_table.name}_id"
        # Check for student_id if join_column is id
        elif join_column == 'id' and 'student_id' in right_table.columns:
            right_join_column = 'student_id'
        else:
            raise ValueError(f"Join column '{join_column}' must exist in both tables")
    
    # Verify that both tables have the join columns
    if join_column not in left_table.columns:
        raise ValueError(f"Join column '{join_column}' not found in left table")
    if right_join_column not in right_table.columns:
        raise ValueError(f"Join column '{right_join_column}' not found in right table")
    
    # Create column names for the joined table, avoiding duplicates
    joined_columns = list(left_table.columns)
    
    # Add columns from right table, except the join column
    for col in right_table.columns:
        if col == right_join_column:
            continue
        if col in joined_columns:
            joined_columns.append(f"{right_table.name}.{col}")
        else:
            joined_columns.append(col)
    
    # Create the joined table
    result = Table(f"{left_table.name}_join_{right_table.name}", joined_columns)
    
    # Get indices of join columns
    left_join_idx = left_table.columns.index(join_column)
    right_join_idx = right_table.columns.index(right_join_column)
    
    # Create map for right table rows by join key
    right_rows_by_key = {}
    for right_row in right_table.rows:
        key = right_row[right_join_idx]
        if key not in right_rows_by_key:
            right_rows_by_key[key] = []
        right_rows_by_key[key].append(right_row)
    
    # Perform the join
    for left_row in left_table.rows:
        left_key = left_row[left_join_idx]
        
        if left_key in right_rows_by_key:
            # Join with matching right rows
            for right_row in right_rows_by_key[left_key]:
                # Create a new row with values from both tables (excluding duplicate join column)
                joined_row = list(left_row)
                for i, val in enumerate(right_row):
                    # Skip the join column from the right table
                    if i != right_join_idx:
                        joined_row.append(val)
                        
                result.rows.append(tuple(joined_row))
    
    return result

def left_join(left_table, right_table, join_column, right_join_column=None):
    """
    Perform a left outer join between two tables.
    
    Args:
        left_table (Table): The left table
        right_table (Table): The right table
        join_column (str): The column in the left table to join on
        right_join_column (str, optional): The column in the right table to join on.
                                          If None, uses the same name as join_column.
        
    Returns:
        Table: A new table with the joined data
    """
    # If right_join_column is not specified, use the same name as join_column
    if right_join_column is None:
        # Check if join_column exists in right_table
        if join_column in right_table.columns:
            right_join_column = join_column
        # Check if there's a column with the pattern "table_name.column_name"
        elif f"{left_table.name}_{join_column}" in right_table.columns:
            right_join_column = f"{left_table.name}_{join_column}"
        # Check for a column ending with _id
        elif f"{join_column}_id" in right_table.columns:
            right_join_column = f"{join_column}_id"
        # Check for a column starting with table_name and ending with _id
        elif f"{left_table.name}_id" in right_table.columns:
            right_join_column = f"{left_table.name}_id"
        # Check for student_id if join_column is id
        elif join_column == 'id' and 'student_id' in right_table.columns:
            right_join_column = 'student_id'
        else:
            raise ValueError(f"Join column '{join_column}' must exist in both tables")
    
    # Verify that both tables have the join columns
    if join_column not in left_table.columns:
        raise ValueError(f"Join column '{join_column}' not found in left table")
    if right_join_column not in right_table.columns:
        raise ValueError(f"Join column '{right_join_column}' not found in right table")
    
    # Create column names for the joined table, avoiding duplicates
    joined_columns = list(left_table.columns)
    
    # Calculate number of columns from right table (excluding join column)
    right_cols = [col for col in right_table.columns if col != right_join_column]
    right_col_names = []
    
    # Add columns from right table, except the join column
    for col in right_table.columns:
        if col == right_join_column:
            continue
        if col in joined_columns:
            new_col = f"{right_table.name}.{col}"
            joined_columns.append(new_col)
            right_col_names.append(new_col)
        else:
            joined_columns.append(col)
            right_col_names.append(col)
    
    # Create the joined table
    result = Table(f"{left_table.name}_left_join_{right_table.name}", joined_columns)
    
    # Get indices of join columns
    left_join_idx = left_table.columns.index(join_column)
    right_join_idx = right_table.columns.index(right_join_column)
    
    # Create map for right table rows by join key
    right_rows_by_key = {}
    for right_row in right_table.rows:
        key = right_row[right_join_idx]
        if key not in right_rows_by_key:
            right_rows_by_key[key] = []
        right_rows_by_key[key].append(right_row)
    
    # Perform the join
    for left_row in left_table.rows:
        left_key = left_row[left_join_idx]
        
        if left_key in right_rows_by_key:
            # Join with matching right rows
            for right_row in right_rows_by_key[left_key]:
                # Create a new row with values from both tables
                joined_row = list(left_row)
                for i, val in enumerate(right_row):
                    # Skip the join column from the right table
                    if i != right_join_idx:
                        joined_row.append(val)
                        
                result.rows.append(tuple(joined_row))
        else:
            # No matching row in right table, include nulls
            joined_row = list(left_row)
            for _ in range(len(right_col_names)):
                joined_row.append(None)
                
            result.rows.append(tuple(joined_row))
    
    return result

def right_join(left_table, right_table, join_column, right_join_column=None):
    """
    Perform a right outer join between two tables.
    
    Args:
        left_table (Table): The left table
        right_table (Table): The right table
        join_column (str): The column in the left table to join on
        right_join_column (str, optional): The column in the right table to join on.
                                          If None, uses the same name as join_column.
        
    Returns:
        Table: A new table with the joined data
    """
    # If right_join_column is not specified, use the same name as join_column
    if right_join_column is None:
        # Check if join_column exists in right_table
        if join_column in right_table.columns:
            right_join_column = join_column
        # Check for student_id if join_column is id
        elif join_column == 'id' and 'student_id' in right_table.columns:
            right_join_column = 'student_id'
        else:
            # Try to find a matching column in the right table
            for col in right_table.columns:
                if col.endswith(join_column) or col.endswith(f"_{join_column}"):
                    right_join_column = col
                    break
            
            if right_join_column is None:
                raise ValueError(f"Join column '{join_column}' must exist in both tables")
    
    # Simply reverse the tables and do a left join
    return left_join(right_table, left_table, right_join_column, join_column)

def full_join(left_table, right_table, join_column, right_join_column=None):
    """
    Perform a full outer join between two tables.
    
    Args:
        left_table (Table): The left table
        right_table (Table): The right table
        join_column (str): The column in the left table to join on
        right_join_column (str, optional): The column in the right table to join on.
                                          If None, uses the same name as join_column.
        
    Returns:
        Table: A new table with the joined data
    """
    # If right_join_column is not specified, use the same name as join_column
    if right_join_column is None:
        # Check if join_column exists in right_table
        if join_column in right_table.columns:
            right_join_column = join_column
        # Check for student_id if join_column is id
        elif join_column == 'id' and 'student_id' in right_table.columns:
            right_join_column = 'student_id'
        else:
            # Try to find a matching column in the right table
            for col in right_table.columns:
                if col.endswith(join_column) or col.endswith(f"_{join_column}"):
                    right_join_column = col
                    break
            
            if right_join_column is None:
                raise ValueError(f"Join column '{join_column}' must exist in both tables")
    
    # Verify that both tables have the join columns
    if join_column not in left_table.columns:
        raise ValueError(f"Join column '{join_column}' not found in left table")
    if right_join_column not in right_table.columns:
        raise ValueError(f"Join column '{right_join_column}' not found in right table")
    
    # First, do a left join
    result = left_join(left_table, right_table, join_column, right_join_column)
    
    # Then add rows from right table that don't have a match
    right_join_idx = right_table.columns.index(right_join_column)
    left_join_idx = left_table.columns.index(join_column)
    
    # Get all keys from left table
    left_keys = {row[left_join_idx] for row in left_table.rows}
    
    # Get a list of non-join columns in left table
    left_columns_count = len(left_table.columns)
    
    # Add rows from right table that don't have a match in left table
    for right_row in right_table.rows:
        right_key = right_row[right_join_idx]
        
        if right_key not in left_keys:
            # This right row doesn't have a match, so add it with nulls for left table
            joined_row = [None] * left_join_idx + [right_key] + [None] * (left_columns_count - left_join_idx - 1)
            
            # Add values from right table (excluding join column)
            for i, val in enumerate(right_row):
                if i != right_join_idx:
                    joined_row.append(val)
                    
            result.rows.append(tuple(joined_row))
    
    return result 