"""
db.py - Database management module

This module handles database operations and table management.
It provides functions to create tables, execute queries, and manage the database state.

Changes:
- Initial implementation of Database class
- Functions for handling SQL operations
- Table management with set-based operations
"""

from sql_ish.table import Table
from sql_ish.where import build_condition_function
from sql_ish.parser import parse_sql


class Database:
    """
    A simple in-memory database that stores tables as sets of tuples.
    """
    
    def __init__(self):
        """Initialize an empty database with no tables."""
        self.tables = {}  # Dictionary mapping table names to Table objects
    
    def create_table(self, table_name, columns):
        """
        Create a new table with the given name and columns.
        
        Args:
            table_name (str): Name of the table
            columns (list): List of column names
            
        Returns:
            bool: True if table was created, False if it already exists
        """
        if table_name in self.tables:
            return False
        
        self.tables[table_name] = Table(table_name, columns)
        return True
    
    def insert(self, table_name, values):
        """
        Insert a new row into a table.
        
        Args:
            table_name (str): Name of the table
            values (tuple): Values to insert
            
        Returns:
            bool: True if insert was successful, False otherwise
        """
        if table_name not in self.tables:
            return False
        
        return self.tables[table_name].insert(values)
    
    def delete(self, table_name, condition=None):
        """
        Delete rows from a table that match a condition.
        
        Args:
            table_name (str): Name of the table
            condition (Condition): Condition object for WHERE clause
            
        Returns:
            int: Number of rows deleted
        """
        if table_name not in self.tables:
            return 0
        
        if condition is None:
            return self.tables[table_name].delete()
        
        condition_func = build_condition_function(condition)
        return self.tables[table_name].delete(condition_func)
    
    def update(self, table_name, updates, condition=None):
        """
        Update rows in a table that match a condition.
        
        Args:
            table_name (str): Name of the table
            updates (dict): Dictionary mapping column names to new values
            condition (Condition): Condition object for WHERE clause
            
        Returns:
            int: Number of rows updated
        """
        if table_name not in self.tables:
            return 0
        
        if condition is None:
            return self.tables[table_name].update(updates)
        
        condition_func = build_condition_function(condition)
        return self.tables[table_name].update(updates, condition_func)
    
    def select(self, table_name, columns=None, condition=None):
        """
        Select rows from a table that match a condition.
        
        Args:
            table_name (str): Name of the table
            columns (list): List of column names to select
            condition (Condition): Condition object for WHERE clause
            
        Returns:
            tuple: (column_names, rows)
        """
        if table_name not in self.tables:
            return ((), set())
        
        if condition is None:
            return self.tables[table_name].select(columns=columns)
        
        condition_func = build_condition_function(condition)
        return self.tables[table_name].select(condition_func, columns)
    
    def join(self, table1_name, table2_name, join_col1, join_col2, condition=None):
        """
        Join two tables based on matching columns.
        
        Args:
            table1_name (str): Name of the first table
            table2_name (str): Name of the second table
            join_col1 (str): Column name from first table for the join
            join_col2 (str): Column name from second table for the join
            condition (Condition): Additional condition to apply after the join
            
        Returns:
            tuple: (column_names, rows)
        """
        if table1_name not in self.tables or table2_name not in self.tables:
            return ((), set())
        
        table1 = self.tables[table1_name]
        table2 = self.tables[table2_name]
        
        # Define join condition function
        def join_condition(row1, cols1, row2, cols2):
            if join_col1 in cols1 and join_col2 in cols2:
                idx1 = cols1.index(join_col1)
                idx2 = cols2.index(join_col2)
                return row1[idx1] == row2[idx2]
            return False
        
        # Perform the join
        joined_columns, joined_rows = table1.inner_join(table2, join_condition)
        
        # Apply additional condition if provided
        if condition is not None:
            condition_func = build_condition_function(condition)
            
            # Filter the joined rows
            filtered_rows = {row for row in joined_rows if condition_func(row, joined_columns)}
            return (joined_columns, filtered_rows)
        
        return (joined_columns, joined_rows)
    
    def execute(self, sql):
        """
        Execute a SQL statement.
        
        Args:
            sql (str): SQL statement to execute
            
        Returns:
            tuple: Result of the operation, varies by command type
        """
        try:
            command_type, parsed_data = parse_sql(sql)
            
            if command_type == 'CREATE':
                table_name, columns = parsed_data
                success = self.create_table(table_name, columns)
                return ("Table created successfully" if success else "Table already exists", None)
            
            elif command_type == 'INSERT':
                table_name, values = parsed_data
                success = self.insert(table_name, values)
                return ("Row inserted successfully" if success else "Failed to insert row", None)
            
            elif command_type == 'DELETE':
                table_name, condition = parsed_data
                count = self.delete(table_name, condition)
                return (f"{count} row(s) deleted", None)
            
            elif command_type == 'UPDATE':
                table_name, updates, condition = parsed_data
                count = self.update(table_name, updates, condition)
                return (f"{count} row(s) updated", None)
            
            elif command_type == 'SELECT':
                table_name, columns, condition, join_info = parsed_data
                
                if join_info is not None:
                    join_table, join_col1, join_col2 = join_info
                    columns, rows = self.join(table_name, join_table, join_col1, join_col2, condition)
                else:
                    # Convert '*' to None for select all columns
                    if columns == ['*']:
                        columns = None
                    columns, rows = self.select(table_name, columns, condition)
                
                return ("Query executed successfully", (columns, rows))
            
            else:
                return (f"Unsupported command: {command_type}", None)
        
        except ValueError as e:
            return (f"Error: {str(e)}", None)
        except Exception as e:
            return (f"Unexpected error: {str(e)}", None)
    
    def get_table(self, table_name):
        """
        Get a table by name.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Table: Table object, or None if not found
        """
        return self.tables.get(table_name) 