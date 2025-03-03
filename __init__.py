"""
SQL-ish - A lightweight SQL-like database engine in Python

This package provides a simple SQL-like database engine for educational purposes
and small applications. It demonstrates relational database concepts using
set theory and discrete mathematics principles.

Changes:
- Restructured to use a modules-based layout
- Previous changes:
  - Updated to version 0.2.0
  - Restructured package into modules
  - Enhanced CLI with script file support
  - Improved API for database operations
  - Better documentation and examples
"""

from modules.engine.db import Database
from modules.core.table import Table
from modules.cli.cli import run_cli

__version__ = '0.3.0'
__all__ = ['Database', 'Table', 'run_cli'] 