"""
db.py - Database engine for SQL-ish implementation

This module implements the core Database class that manages tables and executes SQL-ish queries.
It serves as the main interface for the sql_ish package.

Changes:
- Initial implementation of the Database class
- Support for executing SQL queries via the query() method
- Table management (create, drop, list tables)
- Fixed query method to handle CREATE TABLE correctly
- Updated as part of package restructuring
- Improved error handling for table operations
- Removed debug print statements after resolving issues
"""

from modules.core.table import Table
from modules.core.where import build_condition_function
from modules.parser.parser import parse_query
from modules.engine.join import inner_join, left_join, right_join, full_join

class Database:
    """
    Represents a simple in-memory relational database.
    
    This class manages tables and executes SQL-ish queries.
    """
    
    def __init__(self):
        """Initialize an empty database."""
        self.tables = {}  # Dictionary of tables by name
        
    def create_table(self, name, columns):
        """
        Create a new table in the database.
        
        Args:
            name (str): Name of the table
            columns (list): Column names
            
        Returns:
            Table: The newly created table
        """
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
            
        table = Table(name, columns)
        self.tables[name] = table
        return table
        
    def drop_table(self, name):
        """
        Drop a table from the database.
        
        Args:
            name (str): Name of the table to drop
            
        Returns:
            bool: True if the table was dropped, False if it didn't exist
        """
        if name in self.tables:
            del self.tables[name]
            return True
        return False
        
    def list_tables(self):
        """
        List all tables in the database.
        
        Returns:
            list: Names of all tables in the database
        """
        return sorted(list(self.tables.keys()))
        
    def get_table(self, name):
        """
        Get a table by name.
        
        Args:
            name (str): Name of the table
            
        Returns:
            Table: The table with the given name, or None if not found
        """
        return self.tables.get(name)
        
    def query(self, sql_query):
        """
        Execute a SQL-ish query.
        
        Args:
            sql_query (str): SQL query to execute
            
        Returns:
            Various: Result depends on the query type
        """
        try:
            query_type, parsed_data = parse_query(sql_query)
            
            if query_type == 'CREATE':
                table_name, columns = parsed_data
                table = self.create_table(table_name, columns)
                return "Table created successfully"
                
            elif query_type == 'INSERT':
                table_name, values = parsed_data
                table = self.get_table(table_name)
                if not table:
                    raise ValueError(f"Table '{table_name}' does not exist")
                table.insert(values)
                return "Row inserted successfully"
                
            elif query_type == 'SELECT':
                table_name, columns, condition = parsed_data
                table = self.get_table(table_name)
                if not table:
                    raise ValueError(f"Table '{table_name}' does not exist")
                
                # Apply WHERE clause if present
                if condition:
                    condition_func = build_condition_function(condition)
                    result = table.select(condition_func)
                else:
                    result = table.select()
                
                # Apply projection if columns specified
                if columns:
                    result = result.project(*columns)
                
                return result
                
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
                
        except Exception as e:
            raise ValueError(f"Error executing query: {e}")
            
    def join(self, left_table_name, right_table_name, join_type, join_column):
        """
        Join two tables.
        
        Args:
            left_table_name (str): Name of the left table
            right_table_name (str): Name of the right table
            join_type (str): Type of join ('inner', 'left', 'right', 'full')
            join_column (str): Column name to join on
            
        Returns:
            Table: Result of the join operation
        """
        left_table = self.get_table(left_table_name)
        right_table = self.get_table(right_table_name)
        
        if not left_table:
            raise ValueError(f"Table '{left_table_name}' does not exist")
        if not right_table:
            raise ValueError(f"Table '{right_table_name}' does not exist")
            
        if join_type == 'inner':
            return inner_join(left_table, right_table, join_column)
        elif join_type == 'left':
            return left_join(left_table, right_table, join_column)
        elif join_type == 'right':
            return right_join(left_table, right_table, join_column)
        elif join_type == 'full':
            return full_join(left_table, right_table, join_column)
        else:
            raise ValueError(f"Unsupported join type: {join_type}")
            
    def __str__(self):
        """String representation of the database."""
        if not self.tables:
            return "Database [Empty]"
        return f"Database [Tables: {', '.join(self.tables.keys())}]" 