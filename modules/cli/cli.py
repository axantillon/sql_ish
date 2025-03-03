"""
cli.py - Command Line Interface for SQL-ish

This module implements a command-line interface for interacting with a SQL-ish database.
It provides a REPL (Read-Eval-Print Loop) for executing SQL-ish queries and the ability
to run SQL script files.

Changes:
- Completely rewrote CLI implementation to support script file execution
- Added file loading and execution of SQL scripts
- Improved error handling and reporting
- Enhanced command interface with new commands
- Better feedback and result formatting
- Added support for comments in SQL scripts
- Improved error handling during script execution
- Fixed parsing of semicolons in string literals
- Using smart_split_sql from utils package
- Enhanced result formatting for better readability
- Fixed circular imports by using format_result from utils
- Final cleanup for improved code quality
- Enhanced UX with colors, command history, and better visual feedback
- Added command completion and improved help system
- Improved status display and result formatting
- Added interactive features for better script execution experience
- Fixed color initialization for macOS compatibility
- Added better UI with box characters for improved visibility
"""

import cmd
import sys
import os
import re
import argparse
import traceback
import shutil
import readline
import atexit
from datetime import datetime
import textwrap

# Import colorama for cross-platform colored terminal text
try:
    from colorama import init, Fore, Back, Style, AnsiToWin32
    has_colors = True
    # Initialize colorama with parameters to maximize compatibility
    init(strip=False, convert=True, autoreset=False)
    
    # Force use of ANSI escape sequences for color even if terminal doesn't seem to support it
    os.environ['FORCE_COLOR'] = '1'
    
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
from modules.utils import smart_split_sql, format_result

# Constants
VERSION = "0.3.0"
HISTORY_FILE = os.path.expanduser('~/.sql_ish_history')
QUERY_LOG_FILE = os.path.expanduser('~/.sql_ish_queries.log')

class SQLishCLI(cmd.Cmd):
    """
    Command-line interface for SQL-ish.
    
    Provides a REPL for interacting with a SQL-ish database and ability
    to run SQL script files.
    """
    
    intro = f"""
    {Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
    {Fore.YELLOW}Welcome to SQL-ish CLI v{VERSION}{Fore.CYAN}
    {Fore.WHITE}A lightweight SQL implementation in Python{Fore.CYAN}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
    
    {Fore.WHITE}Type SQL queries or commands:{Style.RESET_ALL}
      {Fore.GREEN}help{Style.RESET_ALL}    - Show available commands
      {Fore.GREEN}tables{Style.RESET_ALL}  - List all tables in database
      {Fore.GREEN}syntax{Style.RESET_ALL}  - Show SQL syntax help
      {Fore.GREEN}example{Style.RESET_ALL} - View example queries
      {Fore.GREEN}exit{Style.RESET_ALL}    - Exit the CLI
    """
    
    prompt = f"{Fore.CYAN}sql-ish▶{Style.RESET_ALL} "
    
    def __init__(self, init_script=None):
        """
        Initialize the CLI with a new database.
        
        Args:
            init_script (str, optional): Path to SQL script to run at startup
        """
        super().__init__()
        self.db = Database()
        self.transaction_count = 0
        self.last_command_time = None
        self.command_history = []
        self.total_queries = 0
        self.successful_queries = 0
        self.setup_history()
        
        # Get terminal size
        self.terminal_width = shutil.get_terminal_size().columns
        
        print(f"\n{Fore.CYAN}✓ {Style.BRIGHT}New SQL-ish database created.{Style.NORMAL} Ready for queries.{Style.RESET_ALL}")
        self.print_status_bar()
        
        # Run init script if provided
        if init_script:
            self.do_run(init_script)
    
    def setup_history(self):
        """Set up command history with readline."""
        # Set up command history
        try:
            if os.path.exists(HISTORY_FILE):
                readline.read_history_file(HISTORY_FILE)
            readline.set_history_length(1000)
        except (ImportError, IOError):
            pass
        atexit.register(self.save_history)
        
    def save_history(self):
        """Save command history at exit."""
        try:
            readline.write_history_file(HISTORY_FILE)
        except (ImportError, IOError):
            pass
            
    def _log_query(self, query, success=True, error=None, duration=None):
        """
        Log a query to the query log file.
        
        Args:
            query (str): The query that was executed
            success (bool): Whether the query was successful
            error (str, optional): Error message if query failed
            duration (float, optional): Execution time in seconds
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = "SUCCESS" if success else "ERROR"
            duration_str = f"{duration:.3f}s" if duration is not None else "N/A"
            
            # Format the log entry
            log_entry = f"[{timestamp}] [{status}] [{duration_str}] {query.strip()}"
            if error:
                log_entry += f"\n    ERROR: {error}"
                
            # Append to log file
            with open(QUERY_LOG_FILE, 'a') as f:
                f.write(log_entry + "\n")
                
        except Exception:
            # Silently ignore logging errors
            pass
    
    def print_status_bar(self):
        """Print a status bar with database information."""
        tables = self.db.list_tables() or []
        width = self.terminal_width
        
        status = f" Tables: {len(tables)} │ Queries: {self.total_queries} │ Success: {self.successful_queries}"
        if self.last_command_time:
            elapsed = f"Last query: {self.last_command_time:.3f}s"
            status += f" │ {elapsed}"
        
        # Create a more visually appealing status bar with gradient colors
        print(f"{Fore.BLACK}{Back.CYAN}{status.ljust(width-1)} {Style.RESET_ALL}")
    
    def get_names(self):
        """Get completable command and SQL keyword names."""
        names = super().get_names()
        
        # Add SQL keywords for better completion
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
            'CREATE', 'TABLE', 'UPDATE', 'SET', 'DELETE', 'AND', 'OR',
            'JOIN', 'GROUP', 'BY', 'ORDER', 'LIMIT', 'IS', 'NULL', 'NOT'
        ]
        
        # Add table names for completion
        tables = self.db.list_tables() or []
        
        # Complete keywords in lowercase too
        completable = (sql_keywords + [k.lower() for k in sql_keywords] + tables)
        return names + ['do_' + item for item in completable]

    def default(self, line):
        """
        Execute a SQL-ish query.
        
        Args:
            line (str): The query to execute
        """
        if line.lower() in ('exit', 'quit'):
            return self.do_exit(line)
            
        try:
            # Save the command for error handling
            self.last_command = line
            
            # Record start time for performance measurement
            start_time = datetime.now()
            
            # Detect query type for formatting
            query_type = None
            if line.strip().upper().startswith('SELECT'):
                query_type = 'SELECT'
            elif line.strip().upper().startswith('INSERT'):
                query_type = 'INSERT'
            elif line.strip().upper().startswith('CREATE'):
                query_type = 'CREATE'
                
            # Execute the query
            result = self.db.query(line)
            
            # Record end time and calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.last_command_time = duration
            self.total_queries += 1
            self.successful_queries += 1
            
            # Log the successful query
            self._log_query(line, success=True, duration=duration)
            
            # Pretty print the result
            if result is not None:
                self._format_result(result, query_type)
            else:
                print(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
                
            # Add to command history
            self.command_history.append(line)
            
            # Show status bar
            self.print_status_bar()
            
        except Exception as e:
            # Log the failed query
            self._log_query(line, success=False, error=str(e), duration=None)
            self._handle_error(e)
            
    def _format_result(self, result, query_type=None):
        """Format and display query results with improved visual presentation."""
        formatted = format_result(result, query_type)
        
        # Add some color based on query type
        if query_type == 'SELECT':
            header_color = Fore.CYAN
            border_color = Fore.BLUE
        elif query_type == 'INSERT':
            header_color = Fore.GREEN
            border_color = Fore.GREEN
        elif query_type == 'CREATE':
            header_color = Fore.YELLOW
            border_color = Fore.YELLOW
        else:
            header_color = Fore.WHITE
            border_color = Fore.CYAN
            
        # Colorize the output with minimal box drawing characters
        lines = formatted.split('\n')
        if len(lines) > 2:  # We have at least a header and separator
            # Replace basic characters with box drawing characters for better visibility
            # even without color support
            lines[0] = lines[0].replace('+', '┌').replace('-', '─').replace('+', '┬')
            if lines[0].endswith('+'):
                lines[0] = lines[0][:-1] + '┐'
            lines[0] = f"{border_color}{lines[0]}{Style.RESET_ALL}"  # Top separator
            
            # Header row with background
            lines[1] = f"{Fore.WHITE}{Back.BLUE}{lines[1].replace('|', '│')}{Style.RESET_ALL}"  # Header
            
            # Middle separator
            lines[2] = lines[2].replace('+', '├').replace('-', '─').replace('+', '┼')
            if lines[2].endswith('+'):
                lines[2] = lines[2][:-1] + '┤'
            lines[2] = f"{border_color}{lines[2]}{Style.RESET_ALL}"  # Separator below header
            
            # Data rows with alternating colors
            for i in range(3, len(lines)-1):
                if '|' in lines[i]:  # Ensure it's a data row
                    if i % 2 == 1:  # Odd rows
                        lines[i] = f"{Fore.WHITE}{lines[i].replace('|', '│')}{Style.RESET_ALL}"
                    else:  # Even rows
                        lines[i] = f"{Fore.CYAN}{lines[i].replace('|', '│')}{Style.RESET_ALL}"
                
            # Bottom separator
            if len(lines) > 3 and '+' in lines[-1]:
                lines[-1] = lines[-1].replace('+', '└').replace('-', '─').replace('+', '┴')
                if lines[-1].endswith('+'):
                    lines[-1] = lines[-1][:-1] + '┘'
                lines[-1] = f"{border_color}{lines[-1]}{Style.RESET_ALL}"
                
        print("\n" + "\n".join(lines))
                
    def _handle_error(self, error, show_trace=False):
        """Handle and display errors with improved formatting and syntax suggestions."""
        error_msg = str(error)
        print(f"\n{Fore.RED}ERROR{Style.RESET_ALL}")
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
        
        # Try to provide more context based on error type
        if "table" in error_msg.lower() and "not found" in error_msg.lower():
            # Extract table name from error message using regex
            import re
            table_match = re.search(r"table ['\"](.*?)['\"]", error_msg.lower())
            table_name = table_match.group(1) if table_match else ""
            
            tables = self.db.list_tables() or []
            if tables:
                # Try to find similar table names using fuzzy matching
                similar_tables = self._find_similar_names(table_name, tables)
                if similar_tables:
                    suggestions = ", ".join([f"'{t}'" for t in similar_tables])
                    print(f"{Fore.YELLOW}Did you mean one of these tables? {suggestions}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Available tables: {', '.join(tables)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}No tables exist yet. Use CREATE TABLE to create one.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Example: CREATE TABLE {table_name} (id, name, value);{Style.RESET_ALL}")
            
        elif "syntax" in error_msg.lower():
            # Try to suggest corrections for the last command
            if hasattr(self, 'last_command') and self.last_command:
                suggestion = self._suggest_syntax_correction(self.last_command)
                if suggestion:
                    print(f"{Fore.YELLOW}Suggested correction:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{suggestion}{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}Tip: Check your SQL syntax. Use 'help' for examples.{Style.RESET_ALL}")
            
        elif "column" in error_msg.lower() and "not found" in error_msg.lower():
            # Extract column and table info
            import re
            col_match = re.search(r"column ['\"](.*?)['\"]", error_msg.lower())
            table_match = re.search(r"table ['\"](.*?)['\"]", error_msg.lower())
            
            col_name = col_match.group(1) if col_match else ""
            table_name = table_match.group(1) if table_match else ""
            
            if table_name:
                try:
                    table = self.db.get_table(table_name)
                    if table and hasattr(table, 'columns'):
                        columns = table.columns
                        similar_cols = self._find_similar_names(col_name, columns)
                        
                        if similar_cols:
                            suggestions = ", ".join([f"'{c}'" for c in similar_cols])
                            print(f"{Fore.YELLOW}Did you mean one of these columns? {suggestions}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}Available columns in '{table_name}': {', '.join(columns)}{Style.RESET_ALL}")
                except:
                    pass
            
        elif "missing" in error_msg.lower() and "parenthesis" in error_msg.lower():
            print(f"{Fore.YELLOW}Tip: Check for balanced parentheses in your query.{Style.RESET_ALL}")
            
        if show_trace:
            print(f"\n{Fore.RED}Traceback:{Style.RESET_ALL}")
            traceback.print_exc()
            
    def _find_similar_names(self, name, candidates, threshold=0.6):
        """Find similar names using fuzzy matching."""
        if not name or not candidates:
            return []
            
        # Try simple case-insensitive matching first
        name_lower = name.lower()
        exact_matches = [c for c in candidates if c.lower() == name_lower]
        if exact_matches:
            return exact_matches
            
        # Try prefix matching
        prefix_matches = [c for c in candidates if c.lower().startswith(name_lower)]
        if prefix_matches:
            return prefix_matches
            
        # Try more advanced fuzzy matching
        try:
            # Use difflib for fuzzy matching if name is long enough
            if len(name) > 2:
                import difflib
                matches = difflib.get_close_matches(name, candidates, n=3, cutoff=threshold)
                if matches:
                    return matches
        except:
            pass
            
        # Last resort: return candidates that contain the name as substring
        return [c for c in candidates if name_lower in c.lower()]
        
    def _suggest_syntax_correction(self, query):
        """Suggest syntax corrections for common SQL errors."""
        if not query:
            return None
            
        query = query.strip()
        query_lower = query.lower()
        
        # Common SQL keyword typos and corrections
        keyword_corrections = {
            'slect': 'SELECT',
            'selectt': 'SELECT',
            'selet': 'SELECT',
            'selec': 'SELECT',
            'frmo': 'FROM',
            'frm': 'FROM',
            'fromm': 'FROM',
            'wher': 'WHERE',
            'whre': 'WHERE',
            'wheer': 'WHERE',
            'wheree': 'WHERE',
            'insrt': 'INSERT',
            'inser': 'INSERT',
            'insrt into': 'INSERT INTO',
            'insert nto': 'INSERT INTO',
            'insert int': 'INSERT INTO',
            'creat': 'CREATE',
            'creae': 'CREATE',
            'crete': 'CREATE',
            'creat table': 'CREATE TABLE',
            'create tabe': 'CREATE TABLE',
            'create tble': 'CREATE TABLE',
            'crate table': 'CREATE TABLE',
            'delte': 'DELETE',
            'delet': 'DELETE',
            'dlte': 'DELETE',
            'delte from': 'DELETE FROM',
            'delete frm': 'DELETE FROM',
            'updte': 'UPDATE',
            'updae': 'UPDATE',
            'updat': 'UPDATE',
            'grup by': 'GROUP BY',
            'group bye': 'GROUP BY',
            'oder by': 'ORDER BY',
            'orer by': 'ORDER BY',
            'order bye': 'ORDER BY',
        }
        
        # Check for missing semicolons at the end
        if not query.endswith(';') and not query.endswith(')'):
            suggested_query = query + ';'
            return suggested_query
            
        # Look for common typos at the beginning of the query
        for typo, correction in keyword_corrections.items():
            if query_lower.startswith(typo):
                # Replace only at the beginning to avoid replacing inside strings
                suggested_query = correction + query[len(typo):]
                return suggested_query
                
        # Check for missing spaces after keywords
        keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 
                   'CREATE', 'TABLE', 'UPDATE', 'SET', 'DELETE', 'GROUP', 'BY', 'ORDER']
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            pos = query_lower.find(keyword_lower)
            if pos >= 0:
                # Check if there's no space after keyword (unless it's at the end or followed by punctuation)
                end_pos = pos + len(keyword_lower)
                if end_pos < len(query_lower) and query_lower[end_pos] not in ' \t\n\r\f\v;,()':
                    # Add a space after the keyword
                    suggested_query = query[:end_pos] + ' ' + query[end_pos:]
                    return suggested_query
        
        # Check for unbalanced parentheses
        open_count = query.count('(')
        close_count = query.count(')')
        
        if open_count > close_count:
            # Missing closing parentheses
            suggested_query = query + ')' * (open_count - close_count)
            return suggested_query
        elif close_count > open_count:
            # Too many closing parentheses - harder to suggest a fix
            return None
            
        # Check for missing VALUES in INSERT
        if 'insert into' in query_lower and 'values' not in query_lower:
            # Try to insert VALUES before the first '('
            paren_pos = query.find('(')
            if paren_pos > 0:
                suggested_query = query[:paren_pos] + 'VALUES ' + query[paren_pos:]
                return suggested_query
                
        # Other common issues - WHERE clause typos
        if ' = = ' in query:
            suggested_query = query.replace(' = = ', ' = ')
            return suggested_query
            
        if ' = =' in query:
            suggested_query = query.replace(' = =', ' = ')
            return suggested_query
            
        if '= =' in query:
            suggested_query = query.replace('= =', ' = ')
            return suggested_query
            
        # No suggestion found
        return None
        
    def do_exit(self, arg):
        """Exit the CLI."""
        print(f"\n{Fore.CYAN}Goodbye! Thanks for using SQL-ish.{Style.RESET_ALL}")
        return True
        
    def do_quit(self, arg):
        """Exit the CLI."""
        return self.do_exit(arg)
        
    def do_tables(self, arg):
        """List all tables in the database."""
        tables = self.db.list_tables()
        if tables:
            header_width = self.terminal_width - 4
            print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{' Tables in database '.center(header_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
            
            # Format table info in a nice table
            headers = ["Table", "Columns", "Rows"]
            rows = []
            
            for table in tables:
                try:
                    tbl = self.db.get_table(table)
                    rows.append([table, len(tbl.columns), len(tbl.rows)])
                except:
                    rows.append([table, "?", "?"])
            
            # Find column widths
            col_widths = []
            for i, col in enumerate(headers):
                # Start with header width
                width = len(str(col))
                # Check all row values
                for row in rows:
                    width = max(width, len(str(row[i])))
                col_widths.append(width + 2)  # Add padding
            
            # Build header with box drawing characters
            total_width = sum(col_widths) + len(col_widths) + 1
            header = "│ " + " │ ".join(str(col).ljust(width-2) for col, width in zip(headers, col_widths)) + " │"
            top_separator = "┌" + "┬".join("─" * width for width in col_widths) + "┐"
            middle_separator = "├" + "┼".join("─" * width for width in col_widths) + "┤"
            bottom_separator = "└" + "┴".join("─" * width for width in col_widths) + "┘"
            
            # Print the table
            print(f"{Fore.CYAN}{top_separator}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{Back.BLUE}{header}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{middle_separator}{Style.RESET_ALL}")
            
            for i, row in enumerate(rows):
                if i % 2 == 0:  # Even rows
                    row_color = Fore.WHITE
                else:  # Odd rows
                    row_color = Fore.CYAN
                row_str = f"{row_color}│ " + f" │ ".join(str(val).ljust(width-2) for val, width in zip(row, col_widths)) + f" │{Style.RESET_ALL}"
                print(row_str)
                
            print(f"{Fore.CYAN}{bottom_separator}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠ No tables defined. Use CREATE TABLE to create one.{Style.RESET_ALL}")
    
    def do_run(self, filepath):
        """
        Run SQL commands from a file.
        
        Args:
            filepath (str): Path to the SQL script file
        """
        if not filepath:
            print(f"{Fore.RED}Error: Missing filepath. Usage: run <filepath>{Style.RESET_ALL}")
            return
            
        # Support for relative paths
        filepath = os.path.expanduser(filepath)
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(filepath)
            
        if not os.path.exists(filepath):
            print(f"{Fore.RED}Error: File not found: {filepath}{Style.RESET_ALL}")
            return
            
        try:
            header_width = self.terminal_width - 4
            print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{Back.BLUE} Executing SQL script {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{filepath}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
            
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Remove comments
            content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
                
            # Split content into queries, respecting string literals
            queries = smart_split_sql(content)
            
            # Filter out empty queries
            queries = [q.strip() for q in queries if q.strip()]
            total_queries = len(queries)
            
            if total_queries == 0:
                print(f"{Fore.YELLOW}No valid SQL queries found in the file.{Style.RESET_ALL}")
                return
                
            successful_queries = 0
            error_queries = 0
            
            # Create a progress bar
            progress_width = min(50, self.terminal_width - 20)
            
            for i, query in enumerate(queries):
                try:
                    query_num = i + 1
                    
                    # Display progress
                    progress = int(query_num / total_queries * progress_width)
                    progress_bar = f"[{'=' * progress}{' ' * (progress_width - progress)}]"
                    progress_text = f"{Fore.CYAN}{progress_bar} {query_num}/{total_queries}{Style.RESET_ALL}"
                    print(f"\n{progress_text}")
                    
                    print(f"\n{Fore.YELLOW}Query {query_num}/{total_queries}:{Style.RESET_ALL}")
                    print(query)
                    print(f"{Fore.CYAN}{'-' * 40}{Style.RESET_ALL}")
                    
                    # Save query for error handling
                    self.last_command = query
                    
                    # Record start time for performance measurement
                    start_time = datetime.now()
                    
                    # Detect query type for formatting
                    query_type = None
                    if query.strip().upper().startswith('SELECT'):
                        query_type = 'SELECT'
                    elif query.strip().upper().startswith('INSERT'):
                        query_type = 'INSERT'
                    elif query.strip().upper().startswith('CREATE'):
                        query_type = 'CREATE'
                    
                    # Execute the query
                    result = self.db.query(query)
                    successful_queries += 1
                    self.total_queries += 1
                    
                    # Record end time and calculate duration
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    self.last_command_time = duration
                    
                    # Format and display the result
                    if result is not None:
                        print(f"{Fore.GREEN}Result:{Style.RESET_ALL}")
                        self._format_result(result, query_type)
                    else:
                        print(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
                        
                except Exception as e:
                    error_queries += 1
                    print(f"{Fore.RED}Error in query {query_num}:{Style.RESET_ALL}")
                    
                    # Apply enhanced error handling with syntax suggestions
                    error_msg = str(e)
                    print(f"\n{Fore.RED}ERROR: {error_msg}{Style.RESET_ALL}")
                    
                    # Try to suggest a correction
                    suggestion = self._suggest_syntax_correction(query)
                    if suggestion:
                        print(f"\n{Fore.YELLOW}Suggested correction:{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{suggestion}{Style.RESET_ALL}")
                        
                        # Offer to execute the suggested correction
                        if input(f"\n{Fore.GREEN}Execute suggested correction? (y/n):{Style.RESET_ALL} ").lower() == 'y':
                            try:
                                print(f"\n{Fore.YELLOW}Executing suggested correction:{Style.RESET_ALL}")
                                print(suggestion)
                                print(f"{Fore.CYAN}{'-' * 40}{Style.RESET_ALL}")
                                
                                # Execute the suggestion
                                result = self.db.query(suggestion)
                                successful_queries += 1
                                self.total_queries += 1
                                
                                # Format and display the result
                                if result is not None:
                                    print(f"{Fore.GREEN}Result:{Style.RESET_ALL}")
                                    self._format_result(result, query_type)
                                else:
                                    print(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
                                    
                                # Continue to next query
                                continue
                            except Exception as e2:
                                print(f"{Fore.RED}Error executing suggested correction: {str(e2)}{Style.RESET_ALL}")
                    
                    # Add options for error handling
                    print(f"\n{Fore.YELLOW}Options:{Style.RESET_ALL}")
                    print(f"  {Fore.GREEN}c{Style.RESET_ALL} - Continue to next query")
                    print(f"  {Fore.GREEN}s{Style.RESET_ALL} - Skip remaining queries")
                    print(f"  {Fore.GREEN}d{Style.RESET_ALL} - Show detailed error info")
                    print(f"  {Fore.GREEN}h{Style.RESET_ALL} - Show help for this query type")
                    print(f"  {Fore.GREEN}q{Style.RESET_ALL} - Quit script execution")
                    
                    while True:
                        choice = input(f"\n{Fore.GREEN}Choice [c/s/d/h/q]:{Style.RESET_ALL} ").lower()
                        if choice == 'c':
                            break
                        elif choice == 's':
                            print(f"\n{Fore.YELLOW}Skipping remaining queries.{Style.RESET_ALL}")
                            break
                        elif choice == 'd':
                            print(f"\n{Fore.YELLOW}Detailed error information:{Style.RESET_ALL}")
                            traceback.print_exc()
                            continue
                        elif choice == 'h':
                            # Show help specific to the query type
                            query_prefix = query.strip().split(' ')[0].upper() if query.strip() else ""
                            print(f"\n{Fore.YELLOW}Help for {query_prefix} queries:{Style.RESET_ALL}")
                            
                            if query_prefix == 'SELECT':
                                print(f"\n{Fore.CYAN}Syntax: SELECT column1, column2, ... FROM table_name [WHERE condition];{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}Example: SELECT id, name FROM users WHERE age > 18;{Style.RESET_ALL}")
                            elif query_prefix == 'INSERT':
                                print(f"\n{Fore.CYAN}Syntax: INSERT INTO table_name VALUES (value1, value2, ...);{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}Example: INSERT INTO users VALUES (1, 'John', 'john@example.com');{Style.RESET_ALL}")
                            elif query_prefix == 'CREATE':
                                print(f"\n{Fore.CYAN}Syntax: CREATE TABLE table_name (column1, column2, ...);{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}Example: CREATE TABLE users (id, name, email);{Style.RESET_ALL}")
                            elif query_prefix == 'UPDATE':
                                print(f"\n{Fore.CYAN}Syntax: UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition;{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}Example: UPDATE users SET name = 'Jane' WHERE id = 1;{Style.RESET_ALL}")
                            elif query_prefix == 'DELETE':
                                print(f"\n{Fore.CYAN}Syntax: DELETE FROM table_name WHERE condition;{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}Example: DELETE FROM users WHERE id = 1;{Style.RESET_ALL}")
                            else:
                                # Generic SQL help
                                self.do_help(None)
                            
                            continue
                        elif choice == 'q':
                            print(f"\n{Fore.YELLOW}Script execution halted by user.{Style.RESET_ALL}")
                            return
                        else:
                            print(f"{Fore.RED}Invalid choice. Please enter c, s, d, h, or q.{Style.RESET_ALL}")
                    
                    if choice == 's':
                        break
            
            # Report results
            print(f"\n{Fore.CYAN}Script execution summary:{Style.RESET_ALL}")
            print(f"- Total queries: {total_queries}")
            print(f"- Successful: {successful_queries}")
            print(f"- Failed: {error_queries}")
            
            if error_queries == 0:
                print(f"\n{Fore.GREEN}All queries executed successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}Script completed with {error_queries} error(s).{Style.RESET_ALL}")
                
            # Update the status bar
            self.print_status_bar()
                
        except Exception as e:
            print(f"\n{Fore.RED}Error reading or processing script: {e}{Style.RESET_ALL}")
    
    def do_history(self, arg):
        """Show command history."""
        if not self.command_history:
            print(f"{Fore.YELLOW}No commands in history yet.{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Command History:{Style.RESET_ALL}")
        for i, cmd in enumerate(self.command_history[-20:], 1):
            print(f"{i:2d}: {cmd}")
    
    def do_clear(self, arg):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.intro)
        self.print_status_bar()

    def do_example(self, arg):
        """Show example SQL queries with option to run them."""
        examples = [
            ("Create a table", "CREATE TABLE products (id, name, price, category);"),
            ("Insert data", "INSERT INTO products VALUES (1, \"Laptop\", 999.99, \"Electronics\");"),
            ("Simple select", "SELECT * FROM products;"),
            ("Filtered select", "SELECT name, price FROM products WHERE price > 500;"),
            ("Join tables", "SELECT products.name, categories.name FROM products, categories WHERE products.category = categories.id;")
        ]
        
        # If a number is provided, run that example
        if arg and arg.isdigit():
            example_num = int(arg)
            if 1 <= example_num <= len(examples):
                example = examples[example_num - 1]
                header_width = self.terminal_width - 4
                
                print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{f' Running Example {example_num}: {example[0]} '.center(header_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
                print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
                
                # Colorize example query
                self._colorize_sql(example[1])
                
                # Execute the example
                try:
                    self.default(example[1])
                except Exception as e:
                    self._handle_error(e)
                return
            else:
                print(f"{Fore.RED}Invalid example number. Choose 1-{len(examples)}.{Style.RESET_ALL}")
                
        # Display all examples
        header_width = self.terminal_width - 4
        print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{' SQL-ish Example Queries '.center(header_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
        
        for i, (description, query) in enumerate(examples, 1):
            print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.YELLOW} Example {i}: {Fore.WHITE}{description}{' ' * (header_width - len(f' Example {i}: {description}') - 2)}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            
            # Try to show colorized SQL, but ensure it fits in the box
            print(f"{Fore.CYAN}│{Style.RESET_ALL} ", end="")
            if len(query) > header_width - 4:
                # Handle long queries by wrapping them
                wrapped_lines = textwrap.wrap(query, width=header_width-4)
                print(wrapped_lines[0] + " " * (header_width - len(wrapped_lines[0]) - 4) + f"{Fore.CYAN}│{Style.RESET_ALL}")
                for line in wrapped_lines[1:]:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL} " + line + " " * (header_width - len(line) - 4) + f"{Fore.CYAN}│{Style.RESET_ALL}")
            else:
                print(query + " " * (header_width - len(query) - 4) + f"{Fore.CYAN}│{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL} Type {Fore.GREEN}example {i}{Style.RESET_ALL} to run this example{' ' * (header_width - len(' Type example X to run this example') - 2)}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
            
    def _colorize_sql(self, query):
        """Colorize SQL keywords and other parts of the query."""
        keywords = ['SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'CREATE', 'TABLE', 'UPDATE', 'SET', 'DELETE', 'AND', 'OR']
        
        # First replace literals to protect them
        import re
        
        # Function to process each token
        def process_token(token):
            # Check if token is a keyword
            upper_token = token.upper()
            if upper_token in keywords:
                return f"{Fore.MAGENTA}{upper_token}{Style.RESET_ALL}"
            
            # Check if token is a number
            if token.replace('.', '', 1).isdigit():
                return f"{Fore.BLUE}{token}{Style.RESET_ALL}"
                
            # Check if token could be a column or table name (alphanumeric)
            if re.match(r'^[a-zA-Z0-9_\.]+$', token):
                return f"{Fore.CYAN}{token}{Style.RESET_ALL}"
                
            # Return token as is for everything else
            return token
        
        # Protect string literals to prevent colorizing their contents
        protected_query = query
        string_literals = re.finditer(r'"[^"]*"|\'[^\']*\'', query)
        replacements = {}
        
        for match in string_literals:
            placeholder = f"__STR{len(replacements)}__"
            replacements[placeholder] = match.group(0)
            protected_query = protected_query.replace(match.group(0), placeholder)
        
        # Colorize keywords and other elements
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            replacement = f"{Fore.MAGENTA}{keyword}{Style.RESET_ALL}"
            protected_query = re.sub(pattern, replacement, protected_query, flags=re.IGNORECASE)
        
        # Colorize numbers
        protected_query = re.sub(r'\b\d+\.?\d*\b', lambda m: f"{Fore.BLUE}{m.group(0)}{Style.RESET_ALL}", protected_query)
        
        # Colorize identifiers (table/column names)
        protected_query = re.sub(r'\b[a-zA-Z][a-zA-Z0-9_]*\b(?!\s*=)', 
                              lambda m: f"{Fore.CYAN}{m.group(0)}{Style.RESET_ALL}", 
                              protected_query)
        
        # Restore string literals with special color
        for placeholder, original in replacements.items():
            colored_str = f"{Fore.GREEN}{original}{Style.RESET_ALL}"
            protected_query = protected_query.replace(placeholder, colored_str)
            
        # Colorize semicolons
        protected_query = protected_query.replace(';', f"{Fore.YELLOW};{Style.RESET_ALL}")
        
        # Colorize parentheses and commas
        protected_query = protected_query.replace('(', f"{Fore.YELLOW}({Style.RESET_ALL}")
        protected_query = protected_query.replace(')', f"{Fore.YELLOW}){Style.RESET_ALL}")
        protected_query = protected_query.replace(',', f"{Fore.YELLOW},{Style.RESET_ALL}")
        
        print(f"{protected_query}")

    def do_syntax(self, arg):
        """Show proper syntax for SQL commands with examples."""
        syntax_help = {
            "select": {
                "syntax": "SELECT column1, column2, ... FROM table_name [WHERE condition];",
                "example": "SELECT id, name, email FROM users WHERE age > 18;",
                "description": "Retrieves data from one or more tables."
            },
            "insert": {
                "syntax": "INSERT INTO table_name VALUES (value1, value2, ...);",
                "example": "INSERT INTO users VALUES (1, 'John', 'john@example.com');",
                "description": "Adds new records to a table."
            },
            "create": {
                "syntax": "CREATE TABLE table_name (column1, column2, ...);",
                "example": "CREATE TABLE users (id, name, email, age);",
                "description": "Creates a new table in the database."
            },
            "update": {
                "syntax": "UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition;",
                "example": "UPDATE users SET name = 'Jane' WHERE id = 1;",
                "description": "Modifies existing records in a table."
            },
            "delete": {
                "syntax": "DELETE FROM table_name WHERE condition;",
                "example": "DELETE FROM users WHERE id = 1;",
                "description": "Removes records from a table."
            }
        }
        
        # If no argument provided, show all syntax help
        if not arg:
            header_width = self.terminal_width - 4
            print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{' SQL-ish Syntax Reference '.center(header_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
            
            for cmd, help_info in syntax_help.items():
                print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Fore.YELLOW}{cmd.upper()}{' ' * (header_width - len(cmd.upper()) - 2)}{Fore.CYAN}│{Style.RESET_ALL}")
                print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
                
                desc_wrapped = textwrap.wrap(f"Description: {help_info['description']}", width=header_width-4)
                for line in desc_wrapped:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.WHITE}{line}{' ' * (header_width - len(line) - 2)}{Fore.CYAN}│{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Fore.GREEN} Syntax:{' ' * (header_width - 9)}{Fore.CYAN}│{Style.RESET_ALL}")
                
                syntax_wrapped = textwrap.wrap(help_info['syntax'], width=header_width-4)
                for line in syntax_wrapped:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.CYAN}{line}{' ' * (header_width - len(line) - 4)}{Fore.CYAN}│{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Fore.GREEN} Example:{' ' * (header_width - 10)}{Fore.CYAN}│{Style.RESET_ALL}")
                
                example_wrapped = textwrap.wrap(help_info['example'], width=header_width-4)
                for line in example_wrapped:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.CYAN}{line}{' ' * (header_width - len(line) - 4)}{Fore.CYAN}│{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
                
            print(f"\n{Fore.YELLOW}For more details on a specific command, type: {Fore.GREEN}syntax <command>{Style.RESET_ALL}")
            return
            
        # Show syntax help for a specific command
        cmd = arg.lower()
        if cmd in syntax_help:
            help_info = syntax_help[cmd]
            header_width = self.terminal_width - 4
            
            print(f"\n{Fore.CYAN}┌{'─' * (header_width-2)}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{f' SQL-ish {cmd.upper()} Syntax '.center(header_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            
            desc_wrapped = textwrap.wrap(f"Description: {help_info['description']}", width=header_width-4)
            for line in desc_wrapped:
                print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.WHITE}{line}{' ' * (header_width - len(line) - 2)}{Fore.CYAN}│{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.GREEN} Syntax:{' ' * (header_width - 9)}{Fore.CYAN}│{Style.RESET_ALL}")
            
            syntax_wrapped = textwrap.wrap(help_info['syntax'], width=header_width-4)
            for line in syntax_wrapped:
                print(f"{Fore.CYAN}│{Style.RESET_ALL}  {line}{' ' * (header_width - len(line) - 4)}{Fore.CYAN}│{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.GREEN} Example:{' ' * (header_width - 10)}{Fore.CYAN}│{Style.RESET_ALL}")
            
            example_wrapped = textwrap.wrap(help_info['example'], width=header_width-4)
            for line in example_wrapped:
                print(f"{Fore.CYAN}│{Style.RESET_ALL}  {line}{' ' * (header_width - len(line) - 4)}{Fore.CYAN}│{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}├{'─' * (header_width-2)}┤{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Fore.YELLOW} Would you like to run this example? (y/n){' ' * (header_width - 40)}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * (header_width-2)}┘{Style.RESET_ALL}")
            
            if input(f"{Fore.GREEN}Run example? (y/n):{Style.RESET_ALL} ").lower() == 'y':
                try:
                    self.default(help_info['example'])
                except Exception as e:
                    self._handle_error(e)
        else:
            print(f"{Fore.RED}Unknown command: {cmd}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Available commands: {', '.join(syntax_help.keys())}{Style.RESET_ALL}")

    def do_help(self, arg):
        """Show help message."""
        # Handle command specific help
        if arg:
            # Check if it's a SQL command for better help
            sql_commands = ['select', 'insert', 'create', 'update', 'delete']
            if arg.lower() in sql_commands:
                return self.do_syntax(arg)
                
            # Otherwise use standard help
            super().do_help(arg)
            return
                
        # General help with better formatting
        term_width = self.terminal_width
        
        print(f"\n{Fore.CYAN}┌{'─' * (term_width-2)}┐{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.WHITE}{Back.BLUE}{' SQL-ish CLI Help '.center(term_width-2)}{Style.RESET_ALL}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}├{'─' * (term_width-2)}┤{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}│{Fore.YELLOW} Basic Commands:{' ' * (term_width-17)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}exit, quit{Style.RESET_ALL}        {Fore.CYAN}Exit the CLI{' ' * (term_width-31)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}tables{Style.RESET_ALL}            {Fore.CYAN}List all tables in the database{' ' * (term_width-46)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}run <filepath>{Style.RESET_ALL}    {Fore.CYAN}Execute SQL commands from a file{' ' * (term_width-50)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}history{Style.RESET_ALL}           {Fore.CYAN}Show command history{' ' * (term_width-37)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}log [n|clear]{Style.RESET_ALL}     {Fore.CYAN}View or clear the query log{' ' * (term_width-44)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}clear{Style.RESET_ALL}             {Fore.CYAN}Clear the screen{' ' * (term_width-33)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}example [num]{Style.RESET_ALL}     {Fore.CYAN}Show or run example queries{' ' * (term_width-44)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}syntax [cmd]{Style.RESET_ALL}      {Fore.CYAN}Show syntax help for SQL commands{' ' * (term_width-49)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.GREEN}help{Style.RESET_ALL}              {Fore.CYAN}Show this help message{' ' * (term_width-37)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}├{'─' * (term_width-2)}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.YELLOW} SQL Commands:{' ' * (term_width-15)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  Type {Fore.GREEN}syntax <command>{Style.RESET_ALL} for detailed help on:{' ' * (term_width-47)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {Fore.MAGENTA}SELECT{Style.RESET_ALL}, {Fore.MAGENTA}INSERT{Style.RESET_ALL}, {Fore.MAGENTA}CREATE{Style.RESET_ALL}, {Fore.MAGENTA}UPDATE{Style.RESET_ALL}, {Fore.MAGENTA}DELETE{Style.RESET_ALL}{' ' * (term_width-44)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}├{'─' * (term_width-2)}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.YELLOW} Quick Reference:{' ' * (term_width-18)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        # Quick reference examples with proper padding
        create_ex = "CREATE TABLE users (id, name, email);"
        insert_ex = "INSERT INTO users VALUES (1, \"John\", \"john@example.com\");"
        select_ex = "SELECT * FROM users WHERE id = 1;"
        
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {create_ex}{' ' * (term_width-len(create_ex)-4)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {insert_ex}{' ' * (term_width-len(insert_ex)-4)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  {select_ex}{' ' * (term_width-len(select_ex)-4)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}├{'─' * (term_width-2)}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Fore.YELLOW} SQL-ish Features:{' ' * (term_width-18)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Syntax error detection with {Fore.CYAN}auto-correction suggestions{' ' * (term_width-60)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Tab completion for {Fore.CYAN}SQL keywords and table names{' ' * (term_width-52)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Command history with {Fore.CYAN}Up/Down arrow navigation{' ' * (term_width-52)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Colorized output for {Fore.CYAN}better readability{' ' * (term_width-45)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Interactive examples to {Fore.CYAN}learn SQL-ish{' ' * (term_width-43)}{Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  • {Fore.WHITE}Query logging for {Fore.CYAN}future reference{' ' * (term_width-40)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}├{'─' * (term_width-2)}┤{Style.RESET_ALL}")
        print(f"{Fore.CYAN}│{Style.RESET_ALL}  Type {Fore.GREEN}example{Style.RESET_ALL} to see and run example queries{' ' * (term_width-47)}{Fore.CYAN}│{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}└{'─' * (term_width-2)}┘{Style.RESET_ALL}")

    def do_log(self, arg):
        """View or clear the query log. Usage: log [n|clear]"""
        # Check if log file exists
        if not os.path.exists(QUERY_LOG_FILE):
            print(f"{Fore.YELLOW}No query log found. Run some queries first.{Style.RESET_ALL}")
            return

        # Clear log if requested
        if arg and arg.lower() == 'clear':
            confirm = input(f"{Fore.YELLOW}Are you sure you want to clear the query log? (y/n):{Style.RESET_ALL} ")
            if confirm.lower() == 'y':
                try:
                    os.remove(QUERY_LOG_FILE)
                    print(f"{Fore.GREEN}Query log cleared.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error clearing log: {e}{Style.RESET_ALL}")
            return

        # Determine how many log entries to show
        limit = 10  # Default
        if arg and arg.isdigit():
            limit = int(arg)

        try:
            # Read log entries (most recent first)
            with open(QUERY_LOG_FILE, 'r') as f:
                log_entries = f.readlines()

            if not log_entries:
                print(f"{Fore.YELLOW}Log file exists but is empty.{Style.RESET_ALL}")
                return

            # Reverse to get most recent first and limit
            log_entries = log_entries[::-1][:limit]

            # Display log entries
            header_width = self.terminal_width - 4
            print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{Back.BLUE} Query Log (Most Recent {limit} Entries) {Style.RESET_ALL}")
            print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")

            import textwrap
            for i, entry in enumerate(log_entries, 1):
                # Parse log entry parts
                parts = entry.strip().split('] [')
                if len(parts) >= 3:
                    # Extract timestamp, status, and duration
                    timestamp = parts[0][1:]  # Remove leading '['
                    status = parts[1]
                    duration_and_query = parts[2].split('] ', 1)
                    
                    if len(duration_and_query) == 2:
                        duration = duration_and_query[0]
                        query = duration_and_query[1]
                        
                        # Apply colors based on status
                        status_color = Fore.GREEN if 'SUCCESS' in status else Fore.RED
                        
                        # Display formatted log entry
                        print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {Fore.YELLOW}[{timestamp}]{Style.RESET_ALL} {status_color}[{status}]{Style.RESET_ALL} {Fore.MAGENTA}[{duration}]{Style.RESET_ALL}")
                        
                        # Wrap long queries for better readability
                        wrapped_query = textwrap.fill(query, width=self.terminal_width-8)
                        
                        # Try to colorize the query
                        try:
                            self._colorize_sql(query)
                        except:
                            # Fall back to plain output if colorizing fails
                            for line in wrapped_query.split('\n'):
                                print(f"   {Fore.CYAN}{line}{Style.RESET_ALL}")
                        
                        # If there's an error message, display it
                        if 'ERROR' in entry and '\n' in entry:
                            error_msg = entry.split('\n')[1].strip()
                            if error_msg.startswith("    ERROR:"):
                                error_msg = error_msg[10:]  # Remove "    ERROR: "
                                print(f"   {Fore.RED}Error: {error_msg}{Style.RESET_ALL}")
                        
                        print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
                else:
                    # Just print the raw entry if parsing fails
                    print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {entry.strip()}")
                    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")

            print(f"{Fore.YELLOW}Tip: Type 'log <number>' to see more entries or 'log clear' to clear the log.{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error reading log: {e}{Style.RESET_ALL}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='SQL-ish CLI')
    parser.add_argument('--script', '-s', 
                       help='SQL script file to execute')
    parser.add_argument('--execute', '-e',
                       help='Execute a single SQL command and exit')
    parser.add_argument('--stop-on-error', action='store_true',
                       help='Stop script execution on first error')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--no-color', action='store_true',
                        help='Disable colored output')
    return parser.parse_args()

def run_cli(no_color=False, script=None, execute=None, stop_on_error=False, debug=False):
    """
    Run the SQL-ish CLI.
    
    Args:
        no_color (bool): Whether to disable colored output
        script (str, optional): Path to SQL script to execute
        execute (str, optional): SQL command to execute
        stop_on_error (bool): Whether to stop script execution on first error
        debug (bool): Whether to enable debug output
    """
    # Only parse arguments if not provided directly
    if all(arg is None for arg in [script, execute]) and not any([no_color, stop_on_error, debug]):
        args = parse_args()
        no_color = args.no_color
        script = args.script
        execute = args.execute
        stop_on_error = args.stop_on_error
        debug = args.debug
    
    # Handle color setup
    if has_colors and not no_color:
        try:
            # Re-initialize colorama
            init(strip=False, convert=True)
            # Set environment variable to force color
            os.environ['FORCE_COLOR'] = '1'
        except:
            pass
    elif no_color:
        global Fore, Back, Style
        Fore = DummyColor()
        Back = DummyColor()
        Style = DummyColor()
    
    # Handle direct command execution mode
    if execute:
        db = Database()
        try:
            start_time = datetime.now()
            result = db.query(execute)
            duration = (datetime.now() - start_time).total_seconds()
            
            print(format_result(result))
            print(f"{Fore.CYAN}Execution time: {duration:.3f}s{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            if debug:
                traceback.print_exc()
        return
    
    # Interactive mode (with optional script)
    cli = SQLishCLI(init_script=script)
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Goodbye! Thanks for using SQL-ish.{Style.RESET_ALL}")
        sys.exit(0)

if __name__ == '__main__':
    run_cli() 