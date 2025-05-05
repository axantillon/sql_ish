"""
cli.py - Command-line interface for running the SQL-ish MCP server

This module provides a command-line interface for running the SQL-ish MCP server.
It allows users to start an MCP server that exposes SQL-ish functionality to AI assistants.

Changes:
- Updated to use WebSocket transport instead of SSE for more stable connections
- Previous changes:
  - Added improved config instructions for successful Cursor connection
  - Added robust error handling without disrupting original SQL-ish functionality 
  - Added robust error handling to prevent server crashes
  - Added signal handling for graceful shutdown
  - Improved logging for debugging connection issues
  - Updated to handle the FastMCP server implementation
  - Initial implementation of the CLI for the MCP server
"""

import argparse
import logging
import os
import signal
import sys
import time
import traceback

from modules.engine.db import Database
from modules.mcp.server import SqlishMcpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sqlish-mcp-cli")

# Global flag for shutdown
shutdown_requested = False

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="SQL-ish MCP Server")
    
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind the server to (default: localhost)",
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8765,
        help="Port to listen on (default: 8765)",
    )
    
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true",
        help="Enable verbose logging",
    )
    
    parser.add_argument(
        "--init-script",
        type=str,
        help="SQL script to initialize the database with",
    )
    
    return parser.parse_args()

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global shutdown_requested
    sig_name = signal.Signals(sig).name
    logger.info(f"Received {sig_name} signal")
    shutdown_requested = True
    # In case server keeps running, exit after a timeout
    time.sleep(3)
    logger.info("Forced exit due to timeout")
    sys.exit(0)

def show_cursor_instructions(host, port):
    """Show instructions for configuring Cursor."""
    print("\n" + "="*80)
    print(f"SQL-ish MCP Server is running at http://{host}:{port}")
    print(f"WebSocket endpoint available at ws://{host}:{port}/ws")
    print("\nTo configure Cursor with this MCP server:")
    print("1. Open Cursor IDE")
    print("2. Go to Settings > MCP")
    print("3. Click 'Add new MCP server'")
    print("4. Enter the following details:")
    print("   - Name: SQL-ish")
    print(f"   - URL: ws://{host}:{port}/ws")
    print("   - Authentication: None")
    print("5. Click Save")
    print("\nThe SQL-ish tools will be available in the Cursor AI assistant.")
    print("="*80 + "\n")

def main():
    """Main entry point for the SQL-ish MCP server CLI."""
    global shutdown_requested
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    args = parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # Create database
        db = Database()
        logger.info("Created new SQL-ish database")
        
        # Initialize database if script provided
        if args.init_script:
            if not os.path.exists(args.init_script):
                logger.error(f"Init script not found: {args.init_script}")
                sys.exit(1)
                
            try:
                with open(args.init_script, "r") as f:
                    script = f.read()
                    
                logger.info(f"Initializing database with script: {args.init_script}")
                for statement in script.split(";"):
                    statement = statement.strip()
                    if statement:
                        logger.debug(f"Executing: {statement}")
                        db.query(statement)
                        
                logger.info("Database initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                sys.exit(1)
        
        # Create MCP server
        server = SqlishMcpServer(database=db)
        
        # Configure server settings
        server.server.settings.host = args.host
        server.server.settings.port = args.port
        
        # Enable debug logging for MCP
        logging.getLogger("mcp").setLevel(logging.DEBUG if args.verbose else logging.INFO)
        
        logger.info(f"Starting SQL-ish MCP server at {args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop the server")
        
        # Display Cursor configuration instructions
        show_cursor_instructions(args.host, args.port)
        
        # Run the server with custom WebSocket implementation
        try:
            # Directly call the run_server method which handles WebSocket connections
            server.run_server(host=args.host, port=args.port)
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            logger.debug(traceback.format_exc())
            
            # Try to restart the server a few times if it crashes
            retries = 3
            while retries > 0 and not shutdown_requested:
                try:
                    logger.info(f"Attempting to restart server ({retries} retries left)")
                    time.sleep(2)  # Wait before retrying
                    server = SqlishMcpServer(database=db)
                    server.server.settings.host = args.host
                    server.server.settings.port = args.port
                    show_cursor_instructions(args.host, args.port)  # Show instructions again
                    server.run_server(host=args.host, port=args.port)
                    break
                except Exception as e:
                    logger.error(f"Restart failed: {e}")
                    retries -= 1
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.debug(traceback.format_exc())
    finally:
        logger.info("Server stopped")

def run():
    """Run the CLI."""
    try:
        main()
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(run()) 