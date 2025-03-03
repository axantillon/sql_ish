"""
__main__.py - Test runner for SQL-ish tests

This module serves as the entry point for running all SQL-ish tests.
It discovers and runs all tests in the tests directory.

Changes:
- Initial implementation of the test runner
- Auto-discovery of test modules in the tests directory
- Added as part of package restructuring
"""

import unittest
import sys
import os

def main():
    """Run all tests in the tests directory."""
    # Start from the directory containing this script
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover and run all tests
    suite = unittest.defaultTestLoader.discover(start_dir)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main()) 