"""
test_set_theory.py - Tests for set theory operations in SQL-ish

This module contains tests for set theory operations implemented in SQL-ish.
It tests union, intersection, difference, and Cartesian product operations.

Changes:
- Initial implementation of set theory tests
- Tests for union, intersection, and difference operations
- Tests for Cartesian product operation
- Added as part of package restructuring
"""

import unittest
from modules.core.table import Table

class SetTheoryTests(unittest.TestCase):
    """Tests for set theory operations on tables."""
    
    def setUp(self):
        """Set up test tables."""
        # Create a table of students
        self.students = Table('students', ['id', 'name', 'major'])
        self.students.insert(('1', 'Alice', 'CS'))
        self.students.insert(('2', 'Bob', 'Math'))
        self.students.insert(('3', 'Charlie', 'CS'))
        
        # Create a table of CS students
        self.cs_students = Table('cs_students', ['id', 'name', 'major'])
        self.cs_students.insert(('1', 'Alice', 'CS'))
        self.cs_students.insert(('3', 'Charlie', 'CS'))
        self.cs_students.insert(('4', 'Dave', 'CS'))
        
        # Create a table of courses
        self.courses = Table('courses', ['code', 'title', 'credits'])
        self.courses.insert(('CS101', 'Intro to CS', '3'))
        self.courses.insert(('MATH200', 'Calculus', '4'))
        
    def test_union(self):
        """Test union operation."""
        result = self.students.union(self.cs_students)
        self.assertEqual(len(result.rows), 4)  # 1, 2, 3, 4
        
    def test_intersection(self):
        """Test intersection operation."""
        result = self.students.intersection(self.cs_students)
        self.assertEqual(len(result.rows), 2)  # 1, 3
        
    def test_difference(self):
        """Test difference operation."""
        # Students who are not CS students
        result = self.students.difference(self.cs_students)
        self.assertEqual(len(result.rows), 1)  # 2
        
        # CS students who are not in the students table
        result = self.cs_students.difference(self.students)
        self.assertEqual(len(result.rows), 1)  # 4
        
    def test_cartesian_product(self):
        """Test Cartesian product operation."""
        result = self.students.cartesian_product(self.courses)
        # 3 students × 2 courses = 6 combinations
        self.assertEqual(len(result.rows), 6)
        # Result should have columns from both tables
        self.assertEqual(len(result.columns), 6)  # id, name, major, code, title, credits

if __name__ == '__main__':
    unittest.main() 