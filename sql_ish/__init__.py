"""
SQL-ish - A simple SQL-like database engine in Python

This package provides a lightweight, in-memory SQL-like database engine
for educational purposes and small applications.

Changes:
- Updated to version 0.2.0
- Restructured package into modules
- Enhanced CLI with script file support
- Improved API for database operations
- Better documentation and examples
"""

from sql_ish.engine.db import Database
from sql_ish.core.table import Table
from sql_ish.cli.cli import run_cli

__version__ = '0.2.0'
__all__ = ['Database', 'Table', 'run_cli'] 