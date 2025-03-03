"""
cli package - Command Line Interface for SQL-ish

This package contains modules for the SQL-ish command-line interface.

Changes:
- Updated to expose enhanced CLI functionality
- Added support for script execution in CLI
"""

from sql_ish.cli.cli import SQLishCLI, run_cli

__all__ = ['SQLishCLI', 'run_cli'] 