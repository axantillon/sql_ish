"""
server.py - MCP Server implementation for SQL-ish

This module implements an MCP server that exposes SQL-ish functionality to AI assistants.
It provides capabilities for executing SQL queries, exploring database schema, and managing tables.

Changes:
- Fixed get_logger call by providing the required name parameter
- Previous changes:
  - Implemented WebSocket transport instead of SSE for more stable connections
  - Added reconnection handling and keepalive mechanisms
  - Added error handling to improve stability
  - Improved resource handling to prevent connection issues
  - Made sure original SQL-ish functionality is preserved
  - Updated to use the correct FastMCP run method with SSE transport
  - Fixed FastMCP resource decorator parameters
  - Updated to use FastMCP instead of low-level Server
  - Fixed Server initialization with required parameters
  - Updated to use URI instead of Location for resources
  - Completed implementation with proper async functions and error handling
  - Updated imports to use the correct class names from the MCP types module
  - Fixed imports to match the actual MCP package structure
  - Fixed import paths to use the correct MCP package name
  - Updated import paths to use the correct MCP Python SDK package
  - Initial implementation of the MCP server for SQL-ish
"""

import asyncio
import json
import logging
import anyio
import traceback
import uvicorn
from typing import Dict, List, Optional, Any, Union, Annotated
from enum import Enum, auto
from urllib.parse import urljoin

# Import pydantic for type definitions
from pydantic import BaseModel, AnyUrl, Field

# Import the correct MCP components
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.resources import TextResource
from mcp.types import TextContent

from modules.engine.db import Database
from modules.utils import format_result

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sqlish-mcp")

class SqlishMcpServer:
    """
    MCP Server implementation for SQL-ish engine.
    
    This class implements the MCP protocol to allow AI assistants to interact with
    SQL-ish databases through the Model Context Protocol.
    """
    
    def __init__(self, database: Optional[Database] = None):
        """
        Initialize the MCP server for SQL-ish.
        
        Args:
            database (Database, optional): An existing database instance to use.
                If not provided, a new database will be created.
        """
        try:
            self.db = database or Database()
            
            # Initialize FastMCP server
            self.server = FastMCP(
                name="SQL-ish",
                version="0.1.0",
                description="SQL-ish MCP server for querying and exploring SQL databases",
            )
            
            # Configure server settings with defaults
            self.server.settings.host = "localhost"
            self.server.settings.port = 8765
            self.server.settings.debug = True  # Enable debug mode for better error reporting
            
            # Register resources and tools
            self._register_resources()
            self._register_tools()
            
            logger.info("SQL-ish MCP server initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MCP server: {e}")
            logger.debug(traceback.format_exc())
            raise
        
    def _register_resources(self):
        """Register resources for the MCP server."""
        try:
            logger.debug("Registering resources...")
            
            # Register database resource
            @self.server.resource(uri="resource://sqlish/")
            def get_database_info():
                """Get information about the SQL-ish database."""
                try:
                    tables = list(self.db.tables.keys())
                    content = f"SQL-ish Database\n\nTables: {', '.join(tables) if tables else 'No tables'}"
                    return TextResource(content=content)
                except Exception as e:
                    logger.error(f"Error in get_database_info: {e}")
                    return TextResource(content=f"Error retrieving database info: {str(e)}")
            
            # Register tables resources
            @self.server.resource(uri="resource://sqlish/tables")
            def get_tables():
                """Get a list of tables in the database."""
                try:
                    tables = list(self.db.tables.keys())
                    content = "Tables in the database:\n\n"
                    if tables:
                        for table in tables:
                            content += f"- {table}\n"
                    else:
                        content += "No tables found."
                    return TextResource(content=content)
                except Exception as e:
                    logger.error(f"Error in get_tables: {e}")
                    return TextResource(content=f"Error retrieving tables: {str(e)}")
            
            # Register individual table resources
            @self.server.resource(uri="resource://sqlish/tables/{table_name}")
            def get_table(table_name: str):
                """Get information about a specific table."""
                try:
                    if table_name not in self.db.tables:
                        return TextResource(content=f"Table '{table_name}' not found")
                    
                    table = self.db.tables[table_name]
                    
                    # Format table info and sample data
                    content = f"Table: {table_name}\n"
                    content += f"Columns: {', '.join(table.columns)}\n"
                    content += f"Row count: {len(table.rows)}\n\n"
                    
                    # Add sample data (up to 10 rows)
                    content += "Sample data:\n"
                    
                    if table.rows:
                        # Format the header
                        header = " | ".join(table.columns)
                        content += header + "\n"
                        content += "-" * len(header) + "\n"
                        
                        # Format rows (up to 10)
                        for row in table.rows[:10]:
                            values = []
                            for col in table.columns:
                                values.append(str(row.get(col, "NULL")))
                            content += " | ".join(values) + "\n"
                        
                        if len(table.rows) > 10:
                            content += f"... ({len(table.rows) - 10} more rows)"
                    else:
                        content += "(no data)"
                    
                    return TextResource(content=content)
                except Exception as e:
                    logger.error(f"Error in get_table for {table_name}: {e}")
                    return TextResource(content=f"Error retrieving table {table_name}: {str(e)}")
            
            logger.debug("Resources registered successfully")
        except Exception as e:
            logger.error(f"Error registering resources: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def _register_tools(self):
        """Register tools for the MCP server."""
        try:
            logger.debug("Registering tools...")
            
            # SQL Query tool
            @self.server.tool(name="query", description="Execute an SQL-ish query on the database")
            def query(
                query: Annotated[str, Field(description="The SQL-ish query to execute")]
            ) -> List[TextContent]:
                """Execute an SQL-ish query on the database."""
                try:
                    logger.info(f"Executing query: {query}")
                    
                    # Execute the query
                    result = self.db.query(query)
                    
                    # Format the result for display
                    formatted_result = format_result(result)
                    
                    return [
                        TextContent(
                            text=formatted_result,
                            title="Query Result",
                        )
                    ]
                except Exception as e:
                    logger.error(f"Error executing query: {e}")
                    return [
                        TextContent(
                            text=f"Error: {str(e)}",
                            title="Query Error",
                        )
                    ]
            
            # Create database tool
            @self.server.tool(name="create_database", description="Create a new database")
            def create_database() -> List[TextContent]:
                """Create a new database."""
                try:
                    # Create a new database
                    self.db = Database()
                    
                    return [
                        TextContent(
                            text="New database created successfully",
                            title="Database Created",
                        )
                    ]
                except Exception as e:
                    logger.error(f"Error creating database: {e}")
                    return [
                        TextContent(
                            text=f"Error: {str(e)}",
                            title="Database Creation Error",
                        )
                    ]
            
            logger.debug("Tools registered successfully")
        except Exception as e:
            logger.error(f"Error registering tools: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def run_server(self, host: str = "localhost", port: int = 8765):
        """
        Run the MCP server with WebSocket transport.
        
        Args:
            host (str): The host to bind to
            port (int): The port to listen on
        """
        try:
            # Update server settings
            self.server.settings.host = host
            self.server.settings.port = port
            
            # Custom starlette app for websocket with better connection handling
            from starlette.applications import Starlette
            from starlette.routing import Route, WebSocketRoute
            from starlette.responses import JSONResponse
            from starlette.websockets import WebSocket
            from mcp.server.fastmcp.utilities.logging import get_logger
            
            # Create logger with a name parameter
            mcp_logger = get_logger("sqlish-mcp-websocket")
            
            # Base handler for root path
            async def root_handler(request):
                return JSONResponse({
                    "name": "SQL-ish MCP Server",
                    "version": "0.1.0",
                    "status": "running",
                    "websocket_endpoint": "/ws"
                })
            
            # Custom websocket handler with keepalive and reconnection support
            async def websocket_handler(websocket: WebSocket):
                await websocket.accept()
                mcp_logger.info(f"WebSocket connection established from {websocket.client}")
                
                # Create MCP session with the FastMCP server
                from mcp.server.session import ServerSession
                
                # Setup keepalive ping task
                async def send_keepalive():
                    try:
                        while True:
                            await asyncio.sleep(30)  # Send ping every 30 seconds
                            await websocket.send_json({"type": "ping", "time": asyncio.get_event_loop().time()})
                    except Exception as e:
                        mcp_logger.debug(f"Keepalive task ended: {e}")
                
                # Start keepalive task
                keepalive_task = asyncio.create_task(send_keepalive())
                
                try:
                    # Use FastMCP's server to handle the WebSocket connection
                    session = ServerSession(
                        self.server._mcp_server,
                        self.server._mcp_server.create_initialization_options(),
                    )
                    
                    # Process messages
                    while True:
                        data = await websocket.receive_text()
                        mcp_logger.debug(f"Received message: {data[:100]}...")
                        
                        # Process message with MCP session
                        response = await session.handle_message(data)
                        
                        if response:
                            await websocket.send_text(response)
                except Exception as e:
                    mcp_logger.error(f"WebSocket error: {e}")
                finally:
                    # Cancel keepalive task
                    keepalive_task.cancel()
                    try:
                        await keepalive_task
                    except asyncio.CancelledError:
                        pass
                    mcp_logger.info(f"WebSocket connection closed for {websocket.client}")
            
            # Create Starlette app with routes
            app = Starlette(
                debug=self.server.settings.debug,
                routes=[
                    Route("/", endpoint=root_handler),
                    WebSocketRoute("/ws", endpoint=websocket_handler),
                ]
            )
            
            # Run with uvicorn
            logger.info(f"Starting SQL-ish MCP server at {host}:{port}")
            logger.info(f"WebSocket endpoint at ws://{host}:{port}/ws")
            
            config = uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level="debug" if self.server.settings.debug else "info",
            )
            
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            logger.debug(traceback.format_exc())
            
    async def start(self, host: str = "localhost", port: int = 8765):
        """
        Start the MCP server.
        
        Args:
            host (str): The host to bind to
            port (int): The port to listen on
        """
        logger.info(f"Starting SQL-ish MCP server at {host}:{port}")
        
        # Update server settings
        self.server.settings.host = host
        self.server.settings.port = port
        
        try:
            # Run the server with custom websocket implementation
            await anyio.to_thread.run_sync(lambda: self.run_server(host, port))
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            logger.debug(traceback.format_exc())
            # Don't re-raise to ensure original functionality continues
    
    async def stop(self):
        """Stop the MCP server."""
        logger.info("Stopping SQL-ish MCP server")
        # FastMCP doesn't have a stop method, but we'll keep this for consistency 