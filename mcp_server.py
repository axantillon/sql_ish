#!/usr/bin/env python3
"""
mcp_server.py - Main entry point for the SQL-ish MCP server

This script serves as the main entry point for running the SQL-ish MCP server.
It allows users to start an MCP server that exposes SQL-ish functionality to AI assistants.

Changes:
- Initial implementation of the MCP server entry point
"""

from modules.mcp.cli import run

if __name__ == "__main__":
    run() 