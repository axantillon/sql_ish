"""
cli.py - Command line interface for SQL-ish

This module provides a simple command-line interface for interacting with the SQL-ish database.
It handles user input, executes commands, and displays results.

Changes:
- Initial implementation of CLI
- Support for executing SQL queries from the command line
- Result formatting and display
"""

import sys
from modules.db import Database


class CLI:
    """
    Command-line interface for the SQL-ish database.
    """
    
    def __init__(self):
        """Initialize CLI with a new database."""
        self.db = Database()
        self.prompt = "sql-ish> "
        self.continue_prompt = "      -> "
        self.running = False
    
    def print_welcome(self):
        """Print welcome message."""
        print("SQL-ish Database Engine")
        print("Type SQL commands to execute them.")
        print("Type 'exit' or 'quit' to exit.")
        print("Type 'help' for more information.")
    
    def print_help(self):
        """Print help information."""
        print("\nSupported SQL commands:")
        print("  CREATE TABLE table_name (column1, column2, ...)")
        print("  INSERT INTO table_name VALUES (value1, value2, ...)")
        print("  DELETE FROM table_name WHERE condition")
        print("  UPDATE table_name SET column=value, ... WHERE condition")
        print("  SELECT [columns | * ] FROM table_name WHERE condition")
        print("  SELECT [columns | * ] FROM table1 JOIN table2 ON table1.col = table2.col WHERE condition")
        print("\nOther commands:")
        print("  help - Show this help message")
        print("  exit, quit - Exit the program")
        print("  tables - List all tables in the database")
        print("  describe table_name - Show table structure")
    
    def format_results(self, columns, rows):
        """
        Format query results for display.
        
        Args:
            columns (tuple): Column names
            rows (set): Set of tuples containing row data
            
        Returns:
            str: Formatted results
        """
        if not columns or not rows:
            return "Empty result set"
        
        # Calculate column widths
        col_widths = [len(str(col)) for col in columns]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val)))
        
        # Format header
        header = " | ".join(f"{str(col):{col_widths[i]}}" for i, col in enumerate(columns))
        separator = "-+-".join("-" * width for width in col_widths)
        
        # Format rows
        formatted_rows = []
        for row in rows:
            formatted_row = " | ".join(f"{str(val):{col_widths[i]}}" for i, val in enumerate(row))
            formatted_rows.append(formatted_row)
        
        # Combine all parts
        result = [header, separator] + formatted_rows
        return "\n".join(result)
    
    def list_tables(self):
        """List all tables in the database."""
        if not self.db.tables:
            print("No tables in database")
            return
        
        print("Tables:")
        for table_name in self.db.tables:
            print(f"  {table_name}")
    
    def describe_table(self, table_name):
        """
        Show table structure.
        
        Args:
            table_name (str): Name of the table
        """
        table = self.db.get_table(table_name)
        if table is None:
            print(f"Table '{table_name}' not found")
            return
        
        print(f"Table: {table_name}")
        print("Columns:")
        for col in table.columns:
            print(f"  {col}")
        print(f"Row count: {len(table)}")
    
    def execute_command(self, command):
        """
        Execute a command.
        
        Args:
            command (str): Command to execute
            
        Returns:
            bool: False if the program should exit, True otherwise
        """
        command = command.strip()
        
        # Check for non-SQL commands
        if command.lower() in ('exit', 'quit'):
            return False
        
        if command.lower() == 'help':
            self.print_help()
            return True
        
        if command.lower() == 'tables':
            self.list_tables()
            return True
        
        if command.lower().startswith('describe '):
            table_name = command[9:].strip()
            self.describe_table(table_name)
            return True
        
        # Execute SQL command
        message, result = self.db.execute(command)
        print(message)
        
        if result is not None:
            columns, rows = result
            if columns and rows:
                print(self.format_results(columns, rows))
                print(f"{len(rows)} row(s) returned")
        
        return True
    
    def get_input(self):
        """
        Get a complete SQL command from the user, which might span multiple lines.
        
        Returns:
            str: Complete SQL command
        """
        buffer = []
        line = input(self.prompt)
        buffer.append(line)
        
        # Continue reading input until a complete statement is entered
        # (simplistically, we check for a semicolon, but this could be improved)
        while not line.strip().endswith(';'):
            try:
                line = input(self.continue_prompt)
                buffer.append(line)
            except KeyboardInterrupt:
                print("\nCommand input cancelled")
                return ""
        
        return ' '.join(buffer).strip()
    
    def run(self):
        """Run the CLI main loop."""
        self.running = True
        self.print_welcome()
        
        while self.running:
            try:
                command = self.get_input().rstrip(';')  # Remove trailing semicolon
                
                if not command:
                    continue
                
                self.running = self.execute_command(command)
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    @classmethod
    def main(cls):
        """Main entry point for the CLI."""
        cli = cls()
        try:
            cli.run()
        except KeyboardInterrupt:
            print("\nExiting...")
        
        return 0


if __name__ == "__main__":
    sys.exit(CLI.main()) 