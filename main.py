"""
main.py - Main entry point for SQL-ish

This module serves as the main entry point for the SQL-ish package.
It provides a simple way to create and use a SQL-ish database.

Changes:
- Restructured project to use a modules-based structure
- Updated import paths to reference new module structure
- Previous changes:
  - Updated to support enhanced CLI with script file execution
  - Added support for direct script execution from command line
  - Improved documentation and examples
  - Enhanced API for database and query operations
  - Added support for comments in SQL scripts
  - Improved error handling during script execution
  - Fixed parsing of semicolons in string literals
  - Ensured single database instance for script execution
  - Improved output formatting for better readability
  - Removed debug prints after fixing identified issues
  - Moved formatting utilities to utils package to fix circular imports
  - Enhanced --execute flag to support multiple statements
  - Final cleanup and readability improvements
  - Added --no-color flag support for consistent color handling
"""

import sys
import re
import argparse

# Import colorama for cross-platform colored terminal text
try:
    from colorama import init, Fore, Back, Style
    has_colors = True
    init()  # Initialize colorama
except ImportError:
    # Create dummy color objects if colorama is not available
    has_colors = False
    class DummyColor:
        def __getattr__(self, name):
            return ''
    Fore = DummyColor()
    Back = DummyColor()
    Style = DummyColor()

from modules.engine.db import Database
from modules.cli.cli import run_cli
from modules.utils import smart_split_sql, format_result

def create_database():
    """
    Create a new SQL-ish database.
    
    Returns:
        Database: A new, empty database
    """
    return Database()

def run_query(db, query):
    """
    Run a SQL-ish query on a database.
    
    Args:
        db (Database): The database to query
        query (str): The SQL-ish query to execute
        
    Returns:
        Various: Result depends on the query type
    """
    return db.query(query)

def run_script(db, script_path, continue_on_error=True, debug=False, no_color=False):
    """
    Run a SQL script file on a database.
    
    Args:
        db (Database): The database to use
        script_path (str): Path to the SQL script file
        continue_on_error (bool): Whether to continue execution after errors
        debug (bool): Whether to show debug output
        no_color (bool): Whether to disable colored output
        
    Returns:
        bool: True if script executed successfully (all queries), False otherwise
    """
    # Disable colors if requested
    if no_color:
        global Fore, Back, Style
        Fore = DummyColor()
        Back = DummyColor()
        Style = DummyColor()
        
    total_queries = 0
    successful_queries = 0
    error_queries = 0
    
    try:
        print(f"{Fore.CYAN}Executing SQL script: {script_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Remove comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        
        # Split content into queries, respecting string literals
        queries = smart_split_sql(content)
        
        # Filter out empty queries
        queries = [q.strip() for q in queries if q.strip()]
        total_queries = len(queries)
        
        if debug:
            print(f"{Fore.YELLOW}Found {total_queries} queries to execute.{Style.RESET_ALL}")
        
        for i, query in enumerate(queries):
            try:
                query_num = i + 1
                print(f"\n{Fore.YELLOW}Query {query_num}/{total_queries}:{Style.RESET_ALL}")
                print(query)
                print(f"{Fore.CYAN}{'-' * 40}{Style.RESET_ALL}")
                
                # Execute the query
                result = db.query(query)
                successful_queries += 1
                
                # Determine query type for formatting
                query_type = None
                if query.strip().upper().startswith('SELECT'):
                    query_type = 'SELECT'
                elif query.strip().upper().startswith('INSERT'):
                    query_type = 'INSERT'
                elif query.strip().upper().startswith('CREATE'):
                    query_type = 'CREATE'
                    
                # Format and display the result
                if result is not None:
                    formatted_result = format_result(result, query_type)
                    print(f"{Fore.GREEN}Result:{Style.RESET_ALL}")
                    print(formatted_result)
                else:
                    print(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
                    
            except Exception as e:
                error_queries += 1
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                
                if not continue_on_error:
                    print(f"{Fore.RED}Stopping script execution due to error{Style.RESET_ALL}")
                    return False
        
        # Report results
        print(f"\n{Fore.CYAN}Script execution summary:{Style.RESET_ALL}")
        print(f"- Total queries: {total_queries}")
        print(f"- Successful: {successful_queries}")
        print(f"- Failed: {error_queries}")
        
        if error_queries == 0:
            print(f"\n{Fore.GREEN}All queries executed successfully!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Script completed with {error_queries} error(s){Style.RESET_ALL}")
        
        return error_queries == 0
    except Exception as e:
        print(f"{Fore.RED}Error processing script file: {e}{Style.RESET_ALL}")
        return False

def execute_statements(db, statements, debug=False, no_color=False):
    """
    Execute multiple SQL statements.
    
    Args:
        db (Database): The database to use
        statements (str): SQL statements to execute
        debug (bool): Whether to show debug output
        no_color (bool): Whether to disable colored output
        
    Returns:
        Any: Result of the last executed query
    """
    # Disable colors if requested
    if no_color:
        global Fore, Back, Style
        Fore = DummyColor()
        Back = DummyColor()
        Style = DummyColor()
        
    # Remove comments
    statements = re.sub(r'--.*$', '', statements, flags=re.MULTILINE)
    
    # Split into individual queries
    queries = smart_split_sql(statements)
    
    # Filter out empty queries
    queries = [q.strip() for q in queries if q.strip()]
    total_queries = len(queries)
    successful_queries = 0
    error_queries = 0
    last_result = None
    
    if debug:
        print(f"{Fore.YELLOW}Found {total_queries} queries to execute.{Style.RESET_ALL}")
    
    for i, query in enumerate(queries):
        try:
            if debug:
                print(f"\n{Fore.CYAN}Executing query {i+1}/{total_queries}:{Style.RESET_ALL}")
                print(query)
                
            # Execute the query
            result = db.query(query)
            successful_queries += 1
            last_result = result
            
            if debug:
                # Determine query type for formatting
                query_type = None
                if query.strip().upper().startswith('SELECT'):
                    query_type = 'SELECT'
                elif query.strip().upper().startswith('INSERT'):
                    query_type = 'INSERT'
                elif query.strip().upper().startswith('CREATE'):
                    query_type = 'CREATE'
                    
                # Format and display the result
                if result is not None:
                    formatted_result = format_result(result, query_type)
                    print(f"{Fore.GREEN}Result:{Style.RESET_ALL}")
                    print(formatted_result)
                else:
                    print(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
        except Exception as e:
            error_queries += 1
            if debug:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Error in query {i+1}: {e}{Style.RESET_ALL}")
                
    if debug:
        print(f"\n{Fore.CYAN}Execution summary:{Style.RESET_ALL}")
        print(f"- Total queries: {total_queries}")
        print(f"- Successful: {successful_queries}")
        print(f"- Failed: {error_queries}")
    
    return last_result

def main():
    """
    Main entry point for the SQL-ish package.
    
    Parses command line arguments and runs the CLI or executes scripts directly.
    """
    parser = argparse.ArgumentParser(description="SQL-ish Database Engine")
    parser.add_argument('--script', '-s', help='SQL script file to execute without CLI')
    parser.add_argument('--execute', '-e', help='Execute SQL command(s) and exit')
    parser.add_argument('--stop-on-error', action='store_true', 
                        help='Stop script execution on first error')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    
    args = parser.parse_args()
    
    # Create a single database instance for all operations
    db = create_database()
    
    # Direct script execution mode
    if args.script:
        success = run_script(db, args.script, 
                           continue_on_error=not args.stop_on_error,
                           debug=args.debug, no_color=args.no_color)
        sys.exit(0 if success else 1)
    
    # Direct command execution mode
    elif args.execute:
        try:
            result = execute_statements(db, args.execute, debug=args.debug, no_color=args.no_color)
            if result is not None:
                print(format_result(result))
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    # CLI mode (default)
    else:
        run_cli(no_color=args.no_color, script=args.script, execute=args.execute,
               stop_on_error=args.stop_on_error, debug=args.debug)

if __name__ == '__main__':
    main() 