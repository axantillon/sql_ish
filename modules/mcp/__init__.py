"""
MCP implementation for SQL-ish engine

This module provides an implementation of the Model Context Protocol (MCP) for the SQL-ish engine.
It allows AI assistants to interact with SQL-ish databases through the MCP standard.

Changes:
- Initial implementation of MCP server for SQL-ish
"""

from modules.mcp.server import SqlishMcpServer

__all__ = ["SqlishMcpServer"] 