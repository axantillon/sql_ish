"""
table.py - Core table data structure for SQL-ish

This module implements the core Table class that represents a relational table.
It provides methods for basic table operations like selection, projection, and insertion.

Changes:
- Initial implementation of the core Table class
- Support for basic table operations (create, insert, select)
- Set theory operations (union, intersection, difference, product)
- Updated as part of package restructuring
- Added __bool__ method to ensure tables are always truthy, even when empty
"""

import copy

class Table:
    """
    Represents a relational database table with columns and rows.
    
    This is the core data structure in the SQL-ish implementation.
    """
    
    def __init__(self, name, columns):
        """
        Initialize a new, empty table.
        
        Args:
            name (str): Name of the table
            columns (tuple): Column names of the table
        """
        self.name = name
        self.columns = tuple(columns)  # Immutable
        self.rows = []
        
    def insert(self, values):
        """
        Insert a row into the table.
        
        Args:
            values (tuple): Values to insert, one for each column
            
        Returns:
            Table: Self for method chaining
        """
        if len(values) != len(self.columns):
            raise ValueError(f"Expected {len(self.columns)} values, got {len(values)}")
        self.rows.append(tuple(values))  # Immutable
        return self
    
    def clone(self, name=None):
        """
        Create a deep copy of this table with optional new name.
        
        Args:
            name (str, optional): New name for the cloned table
            
        Returns:
            Table: A new table with the same schema and data
        """
        new_table = Table(name or self.name, self.columns)
        new_table.rows = copy.deepcopy(self.rows)
        return new_table
    
    def select(self, condition_func=None):
        """
        Select rows that match a condition.
        
        Args:
            condition_func: Function that takes (row, columns) and returns bool
            
        Returns:
            Table: A new table with matching rows
        """
        result = Table(self.name, self.columns)
        
        if condition_func is None:
            # Select all rows if no condition given
            result.rows = copy.deepcopy(self.rows)
        else:
            # Select rows that match the condition
            for row in self.rows:
                if condition_func(row, self.columns):
                    result.rows.append(row)
                    
        return result
    
    def project(self, *proj_columns):
        """
        Project specific columns from the table.
        
        Args:
            *proj_columns: Names of columns to include
            
        Returns:
            Table: A new table with only the specified columns
        """
        if not proj_columns:
            return self.clone()
            
        # Create a new table with the projected columns
        result = Table(self.name, proj_columns)
        
        # Create a mapping from original column indices to new column indices
        indices = [self.columns.index(col) for col in proj_columns if col in self.columns]
        
        # Project only the specified columns
        for row in self.rows:
            new_row = tuple(row[i] for i in indices)
            result.rows.append(new_row)
            
        return result
    
    def union(self, other):
        """
        Set union operation between two tables.
        
        Args:
            other (Table): Another table with the same schema
            
        Returns:
            Table: A new table with rows from both tables (no duplicates)
        """
        # Check if schemas match
        if self.columns != other.columns:
            raise ValueError("Cannot union tables with different schemas")
            
        # Create a new table with the same schema
        result = self.clone(f"{self.name}_union_{other.name}")
        
        # Add rows from other table, avoiding duplicates
        existing_rows = set(self.rows)
        for row in other.rows:
            if row not in existing_rows:
                result.rows.append(row)
                
        return result
    
    def intersection(self, other):
        """
        Set intersection operation between two tables.
        
        Args:
            other (Table): Another table with the same schema
            
        Returns:
            Table: A new table with rows that exist in both tables
        """
        # Check if schemas match
        if self.columns != other.columns:
            raise ValueError("Cannot intersect tables with different schemas")
            
        # Create a new table with the same schema
        result = Table(f"{self.name}_intersect_{other.name}", self.columns)
        
        # Add rows that exist in both tables
        other_rows = set(other.rows)
        for row in self.rows:
            if row in other_rows:
                result.rows.append(row)
                
        return result
    
    def difference(self, other):
        """
        Set difference operation between two tables.
        
        Args:
            other (Table): Another table with the same schema
            
        Returns:
            Table: A new table with rows in this table but not in the other
        """
        # Check if schemas match
        if self.columns != other.columns:
            raise ValueError("Cannot diff tables with different schemas")
            
        # Create a new table with the same schema
        result = Table(f"{self.name}_diff_{other.name}", self.columns)
        
        # Add rows that exist in this table but not in the other
        other_rows = set(other.rows)
        for row in self.rows:
            if row not in other_rows:
                result.rows.append(row)
                
        return result
    
    def cartesian_product(self, other):
        """
        Cartesian product of two tables.
        
        Args:
            other (Table): Another table
            
        Returns:
            Table: A new table with combined columns and all combinations of rows
        """
        # Create column names for the product table, avoiding duplicates
        duplicate_cols = set(self.columns) & set(other.columns)
        all_columns = list(self.columns)
        
        for col in other.columns:
            if col in duplicate_cols:
                new_col = f"{other.name}.{col}"
            else:
                new_col = col
            all_columns.append(new_col)
            
        # Create a new table for the product
        result = Table(f"{self.name}_product_{other.name}", all_columns)
        
        # Generate all combinations of rows
        for row1 in self.rows:
            for row2 in other.rows:
                result.rows.append(row1 + row2)
                
        return result
    
    def __str__(self):
        """Return a string representation of the table."""
        if not self.rows:
            return f"Table {self.name} ({', '.join(self.columns)}) [Empty]"
        
        result = [f"Table {self.name} ({', '.join(self.columns)})"]
        
        for row in self.rows:
            result.append(str(row))
            
        return "\n".join(result)
    
    def __len__(self):
        """Return the number of rows in the table."""
        return len(self.rows)
    
    def __bool__(self):
        """
        Truth value testing for Table objects.
        
        Returns True regardless of whether the table has rows or not.
        This ensures that a table is considered to exist even when empty.
        
        Returns:
            bool: Always True for valid Table objects
        """
        return True 