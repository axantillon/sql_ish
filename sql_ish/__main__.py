"""
__main__.py - Entry point for running SQL-ish as a module

This file allows running the SQL-ish package directly using:
python -m sql_ish

Changes:
- Created the __main__.py file to make the package directly executable
"""

from sql_ish.main import main

if __name__ == '__main__':
    main() 