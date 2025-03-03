"""
test.py - Simple tests for SQL-ish engine

This module contains basic tests to verify the functionality of the SQL-ish engine.
It's not a comprehensive test suite, but it tests the core functionality.

Changes:
- Initial implementation of basic tests
- Coverage of core SQL operations
- Verification of set theory concepts
- Fixed imports to work when running from inside the sql_ish directory
"""

import unittest
from db import Database
from where import Comparison, And, Or, Not


class SQLishTests(unittest.TestCase):
    """Basic tests for the SQL-ish engine."""
    
    def setUp(self):
        """Set up a database with test tables."""
        self.db = Database()
        
        # Create Student table
        self.db.execute("CREATE TABLE Student (ids, firstname, lastname, birthday)")
        
        # Add some test data
        self.db.execute("INSERT INTO Student VALUES (1, John, Doe, 1990)")
        self.db.execute("INSERT INTO Student VALUES (2, Jane, Smith, 1995)")
        self.db.execute("INSERT INTO Student VALUES (3, Bob, Johnson, 1985)")
        
        # Create Professor table
        self.db.execute("CREATE TABLE Professor (idp, firstname, lastname, department)")
        
        # Add some test data
        self.db.execute("INSERT INTO Professor VALUES (1, Alan, Turing, ComputerScience)")
        self.db.execute("INSERT INTO Professor VALUES (2, Marie, Curie, Physics)")
    
    def test_create_table(self):
        """Test CREATE TABLE operation."""
        # Create a new table
        message, _ = self.db.execute("CREATE TABLE Course (id, name, credits)")
        self.assertIn("successfully", message)
        
        # Verify table exists
        self.assertIn("Course", self.db.tables)
        self.assertEqual(self.db.tables["Course"].columns, ("id", "name", "credits"))
    
    def test_insert(self):
        """Test INSERT operation."""
        # Insert a new row
        message, _ = self.db.execute("INSERT INTO Student VALUES (4, Mark, Wilson, 2000)")
        self.assertIn("successfully", message)
        
        # Verify row was inserted
        _, result = self.db.execute("SELECT * FROM Student WHERE ids = 4")
        columns, rows = result
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows)[0], ("4", "Mark", "Wilson", "2000"))
    
    def test_select(self):
        """Test SELECT operation."""
        # Select all students
        _, result = self.db.execute("SELECT * FROM Student")
        columns, rows = result
        self.assertEqual(len(rows), 3)  # We inserted 3 students in setUp
        
        # Select with condition
        _, result = self.db.execute("SELECT * FROM Student WHERE ids = 2")
        columns, rows = result
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows)[0][1], "Jane")  # Check firstname
    
    def test_update(self):
        """Test UPDATE operation."""
        # Update a row
        message, _ = self.db.execute("UPDATE Student SET firstname=Alice WHERE ids=2")
        self.assertIn("updated", message)
        
        # Verify update
        _, result = self.db.execute("SELECT * FROM Student WHERE ids = 2")
        columns, rows = result
        self.assertEqual(list(rows)[0][1], "Alice")  # Check updated firstname
    
    def test_delete(self):
        """Test DELETE operation."""
        # Delete a row
        message, _ = self.db.execute("DELETE FROM Student WHERE ids=3")
        self.assertIn("deleted", message)
        
        # Verify deletion
        _, result = self.db.execute("SELECT * FROM Student WHERE ids = 3")
        columns, rows = result
        self.assertEqual(len(rows), 0)  # No rows should match
        
        # Verify remaining data
        _, result = self.db.execute("SELECT * FROM Student")
        columns, rows = result
        self.assertEqual(len(rows), 2)  # Started with 3, deleted 1
    
    def test_join(self):
        """Test JOIN operation."""
        # First, create a table for the join
        self.db.execute("CREATE TABLE StudentAdvisor (ids, idp)")
        self.db.execute("INSERT INTO StudentAdvisor VALUES (1, 2)")  # John is advised by Marie
        self.db.execute("INSERT INTO StudentAdvisor VALUES (2, 1)")  # Jane is advised by Alan
        
        # Perform a join
        _, result = self.db.execute("SELECT * FROM Student JOIN StudentAdvisor ON Student.ids=StudentAdvisor.ids")
        columns, rows = result
        self.assertEqual(len(rows), 2)  # Two students have advisors
        
        # Check join result contains data from both tables
        for row in rows:
            if row[0] == "1":  # Student id 1 (John)
                self.assertEqual(row[4], "1")  # StudentAdvisor.ids
                self.assertEqual(row[5], "2")  # StudentAdvisor.idp (Marie)
            elif row[0] == "2":  # Student id 2 (Jane/Alice after update test)
                self.assertEqual(row[5], "1")  # StudentAdvisor.idp (Alan)
    
    def test_complex_where(self):
        """Test complex WHERE conditions with AND, OR, NOT."""
        # Add more test data
        self.db.execute("INSERT INTO Student VALUES (5, Mark, Johnson, 2000)")
        self.db.execute("INSERT INTO Student VALUES (6, John, Wilson, 2005)")
        
        # Test OR condition
        _, result = self.db.execute("SELECT * FROM Student WHERE ids = 1 OR ids = 2")
        columns, rows = result
        self.assertEqual(len(rows), 2)
        
        # Test AND condition
        _, result = self.db.execute("SELECT * FROM Student WHERE lastname = Johnson AND birthday = 1985")
        columns, rows = result
        self.assertEqual(len(rows), 1)
        self.assertEqual(list(rows)[0][0], "3")  # Student id 3 (Bob Johnson)
        
        # Test NOT condition
        _, result = self.db.execute("SELECT * FROM Student WHERE NOT ids = 1")
        columns, rows = result
        ids = [row[0] for row in rows]
        self.assertNotIn("1", ids)
        self.assertIn("2", ids)
        
        # Test complex condition (AND + OR)
        _, result = self.db.execute("SELECT * FROM Student WHERE (firstname = John OR firstname = Mark) AND birthday > 1990")
        columns, rows = result
        self.assertEqual(len(rows), 2)
        firstnames = [row[1] for row in rows]
        self.assertIn("Mark", firstnames)
        self.assertIn("John", firstnames)
    
    def test_set_operations(self):
        """Test that operations correspond to set theory operations."""
        # Insert overlapping data in two tables
        self.db.execute("CREATE TABLE Students1 (id, name)")
        self.db.execute("CREATE TABLE Students2 (id, name)")
        
        self.db.execute("INSERT INTO Students1 VALUES (1, Alice)")
        self.db.execute("INSERT INTO Students1 VALUES (2, Bob)")
        self.db.execute("INSERT INTO Students1 VALUES (3, Charlie)")
        
        self.db.execute("INSERT INTO Students2 VALUES (2, Bob)")
        self.db.execute("INSERT INTO Students2 VALUES (3, Charlie)")
        self.db.execute("INSERT INTO Students2 VALUES (4, Dave)")
        
        # Inner join should be like intersection
        _, result = self.db.execute("SELECT * FROM Students1 JOIN Students2 ON Students1.id=Students2.id")
        columns, rows = result
        self.assertEqual(len(rows), 2)  # Should have Bob and Charlie
        
        ids = [row[0] for row in rows]
        self.assertIn("2", ids)  # Bob
        self.assertIn("3", ids)  # Charlie
        self.assertNotIn("1", ids)  # Alice (only in Students1)
        self.assertNotIn("4", ids)  # Dave (only in Students2)


if __name__ == "__main__":
    unittest.main() 