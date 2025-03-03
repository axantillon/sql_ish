"""
where.py - WHERE clause evaluation using propositional logic

This module implements propositional logic evaluation for WHERE clauses.
It supports basic logical operators (AND, OR, NOT) and comparison operators.

Changes:
- Initial implementation of WHERE clause condition evaluation
- Support for AND, OR, NOT logical operators
- Support for =, <, >, <=, >=, != comparison operators
- Updated as part of package restructuring
"""

class Condition:
    """Base class for all condition types."""
    def evaluate(self, row, columns):
        """
        Evaluate the condition for a given row.
        
        Args:
            row (tuple): The row to evaluate
            columns (tuple): The column names
            
        Returns:
            bool: True if condition is satisfied, False otherwise
        """
        raise NotImplementedError("Subclasses must implement evaluate()")


class Comparison(Condition):
    """
    Represents a comparison between a column value and a constant.
    e.g., age > '18'
    """
    def __init__(self, column, operator, value):
        """
        Initialize a comparison condition.
        
        Args:
            column (str): Column name
            operator (str): One of '=', '<', '>', '<=', '>=', '!='
            value (str): Value to compare against
        """
        self.column = column
        self.operator = operator
        self.value = value
        
    def evaluate(self, row, columns):
        """
        Evaluate the comparison for a given row.
        
        Args:
            row (tuple): The row to evaluate
            columns (tuple): The column names
            
        Returns:
            bool: True if comparison is satisfied, False otherwise
        """
        if self.column not in columns:
            return False
        
        col_idx = columns.index(self.column)
        row_value = row[col_idx]
        
        # All values are stored as strings, so convert if comparing numerically
        try:
            # Try to convert both to float for numeric comparison
            row_val_numeric = float(row_value)
            comp_val_numeric = float(self.value)
            
            # Use numeric comparison
            if self.operator == '=':
                return row_val_numeric == comp_val_numeric
            elif self.operator == '<':
                return row_val_numeric < comp_val_numeric
            elif self.operator == '>':
                return row_val_numeric > comp_val_numeric
            elif self.operator == '<=':
                return row_val_numeric <= comp_val_numeric
            elif self.operator == '>=':
                return row_val_numeric >= comp_val_numeric
            elif self.operator == '!=':
                return row_val_numeric != comp_val_numeric
        except (ValueError, TypeError):
            # Fall back to string comparison
            if self.operator == '=':
                return row_value == self.value
            elif self.operator == '<':
                return row_value < self.value
            elif self.operator == '>':
                return row_value > self.value
            elif self.operator == '<=':
                return row_value <= self.value
            elif self.operator == '>=':
                return row_value >= self.value
            elif self.operator == '!=':
                return row_value != self.value
                
        return False


class And(Condition):
    """
    Represents a logical AND of two conditions.
    e.g., age > '18' AND grade = 'A'
    
    In set theory, this is equivalent to the intersection of two sets.
    """
    def __init__(self, left, right):
        """
        Initialize an AND condition.
        
        Args:
            left (Condition): Left condition
            right (Condition): Right condition
        """
        self.left = left
        self.right = right
        
    def evaluate(self, row, columns):
        """
        Evaluate the AND condition for a given row.
        
        Args:
            row (tuple): The row to evaluate
            columns (tuple): The column names
            
        Returns:
            bool: True if both conditions are satisfied, False otherwise
        """
        # Logical AND (∧) - both conditions must be true
        return self.left.evaluate(row, columns) and self.right.evaluate(row, columns)


class Or(Condition):
    """
    Represents a logical OR of two conditions.
    e.g., age > '18' OR grade = 'A'
    
    In set theory, this is equivalent to the union of two sets.
    """
    def __init__(self, left, right):
        """
        Initialize an OR condition.
        
        Args:
            left (Condition): Left condition
            right (Condition): Right condition
        """
        self.left = left
        self.right = right
        
    def evaluate(self, row, columns):
        """
        Evaluate the OR condition for a given row.
        
        Args:
            row (tuple): The row to evaluate
            columns (tuple): The column names
            
        Returns:
            bool: True if either condition is satisfied, False otherwise
        """
        # Logical OR (∨) - at least one condition must be true
        return self.left.evaluate(row, columns) or self.right.evaluate(row, columns)


class Not(Condition):
    """
    Represents a logical NOT of a condition.
    e.g., NOT (age > '18')
    
    In set theory, this is equivalent to the complement of a set.
    """
    def __init__(self, condition):
        """
        Initialize a NOT condition.
        
        Args:
            condition (Condition): The condition to negate
        """
        self.condition = condition
        
    def evaluate(self, row, columns):
        """
        Evaluate the NOT condition for a given row.
        
        Args:
            row (tuple): The row to evaluate
            columns (tuple): The column names
            
        Returns:
            bool: True if the condition is not satisfied, False otherwise
        """
        # Logical NOT (¬) - negation of the condition
        return not self.condition.evaluate(row, columns)


def build_condition_function(condition):
    """
    Build a function that evaluates a condition for a row.
    
    Args:
        condition (Condition): The condition to evaluate
        
    Returns:
        callable: Function that takes (row, columns) and returns bool
    """
    def condition_func(row, columns):
        return condition.evaluate(row, columns)
    
    return condition_func 