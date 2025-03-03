"""
test_basic.py - Basic tests for SQL-ish package

This module contains basic tests for the SQL-ish package functionality.
It tests core operations like table creation, insertion, and querying.

Changes:
- Initial implementation of basic tests
- Tests for table creation and manipulation
- Tests for SQL query parsing and execution
- Fixed test_sql_query to use direct API calls
- Added as part of package restructuring
"""

import unittest
from sql_ish.engine.db import Database
from sql_ish.core.table import Table
from sql_ish.core.where import Comparison, build_condition_function

class BasicTests(unittest.TestCase):
    """Basic tests for SQL-ish functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.db = Database()
        
    def test_create_table(self):
        """Test table creation."""
        table = self.db.create_table('test', ['id', 'name', 'age'])
        self.assertIsInstance(table, Table)
        self.assertEqual(table.name, 'test')
        self.assertEqual(table.columns, ('id', 'name', 'age'))
        self.assertEqual(len(table.rows), 0)
        
    def test_insert(self):
        """Test row insertion."""
        table = self.db.create_table('test', ['id', 'name', 'age'])
        table.insert(('1', 'Alice', '30'))
        table.insert(('2', 'Bob', '25'))
        self.assertEqual(len(table.rows), 2)
        
    def test_select_all(self):
        """Test selecting all rows."""
        table = self.db.create_table('test', ['id', 'name', 'age'])
        table.insert(('1', 'Alice', '30'))
        table.insert(('2', 'Bob', '25'))
        result = table.select()
        self.assertEqual(len(result.rows), 2)
        
    def test_select_where(self):
        """Test select with WHERE clause."""
        table = self.db.create_table('test', ['id', 'name', 'age'])
        table.insert(('1', 'Alice', '30'))
        table.insert(('2', 'Bob', '25'))
        # Select rows where age > 25
        result = table.select(lambda row, cols: int(row[cols.index('age')]) > 25)
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0][1], 'Alice')
        
    def test_project(self):
        """Test column projection."""
        table = self.db.create_table('test', ['id', 'name', 'age'])
        table.insert(('1', 'Alice', '30'))
        table.insert(('2', 'Bob', '25'))
        result = table.project('name', 'age')
        self.assertEqual(result.columns, ('name', 'age'))
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(len(result.rows[0]), 2)
        
    def test_sql_query(self):
        """Test SQL query execution."""
        # Create a table directly
        table = self.db.create_table('test', ['id', 'name', 'age'])
        
        # Insert data directly
        table.insert(('1', 'Alice', '30'))
        table.insert(('2', 'Bob', '25'))
        
        # Test SQL SELECT query
        result = self.db.query("SELECT * FROM test")
        self.assertEqual(len(result.rows), 2)
        
        # Test SQL SELECT with WHERE query
        result = self.db.query("SELECT name, age FROM test WHERE age > 25")
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0][0], 'Alice')

if __name__ == '__main__':
    unittest.main() 