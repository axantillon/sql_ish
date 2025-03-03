# SQL-ish: A Lightweight SQL Implementation in Python

SQL-ish is an educational SQL database engine written in Python that demonstrates relational database concepts using set theory and discrete mathematics principles. It provides a command-line interface for executing SQL queries and running SQL scripts.

## Features

- **Interactive CLI** with professional box-drawing characters and rich color-coding
- **SQL Query Execution** supporting essential SQL operations:
  - CREATE TABLE: Define table structures
  - INSERT: Add data to tables
  - SELECT: Query data with filtering and joins
  - UPDATE: Modify existing data
  - DELETE: Remove records based on conditions
- **Syntax Highlighting** for SQL keywords, identifiers, and literals
- **Error Handling** with helpful syntax correction suggestions
- **Script Execution** for running SQL files
- **Command History** and query logging
- **Tab Completion** for SQL keywords and table names
- **Example-Based Learning** with built-in SQL examples
- **Terminal UI** with box drawing characters for clean, readable output

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sql-ish.git
cd sql-ish
```

### Virtual Environment Setup (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other Python packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
## On Windows
venv\Scripts\activate
## On macOS/Linux
source venv/bin/activate

# Verify activation (should show the virtual environment path)
which python  # On macOS/Linux
where python  # On Windows
```

### Installing Dependencies

Once your virtual environment is activated, you have two options:

#### Option 1: Install for development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI directly from the source
python main.py
# OR (assuming your current directory is named 'sql_ish')
python -m sql_ish
```

#### Option 2: Install as a package (recommended)

```bash
# Install the package in development mode
pip install -e .

# Now you can run using either of these commands:
python -m sql_ish
# OR use the command-line tool
sqlish
```

## Usage

### Command-Line Interface

```bash
# Start the interactive CLI
python -m sql_ish

# Execute a single SQL command
python -m sql_ish --execute "CREATE TABLE users (id, name, email)"

# Run a SQL script file
python -m sql_ish --script examples/01_blog_platform.sql

# Disable colored output (if needed)
python -m sql_ish --no-color

# Enable debug output
python -m sql_ish --debug

# Show help
python -m sql_ish --help
```

### Example SQL Commands

```sql
-- Create a table
CREATE TABLE users (id, username, email);

-- Insert data
INSERT INTO users VALUES (1, "johndoe", "john@example.com");

-- Query data
SELECT * FROM users WHERE id = 1;

-- Join tables
SELECT users.username, posts.title
FROM users JOIN posts ON users.id = posts.user_id;
```

## CLI Commands

| Command         | Description                         |
| --------------- | ----------------------------------- | ----------------------------------- |
| `help`          | Show available commands             |
| `tables`        | List all tables in the database     |
| `run <file>`    | Execute SQL commands from a file    |
| `example [num]` | Show and run example SQL queries    |
| `syntax [cmd]`  | Show proper syntax for SQL commands |
| `log [n         | clear]`                             | View or clear the query history log |
| `history`       | Show command history                |
| `clear`         | Clear the screen                    |
| `exit`, `quit`  | Exit the CLI                        |

## Example SQL Scripts

The project includes several example SQL scripts:

- `01_blog_platform.sql`: Blog with users, posts, and comments
- `02_employee_management.sql`: HR database with employees and departments
- `03_online_store.sql`: E-commerce with products, orders, and customers
- `04_library_management.sql`: Library with books, authors, and loans

## CLI UI Features

SQL-ish features a polished terminal UI with:

- **Box Drawing Characters**: Clean, structured output with proper borders
- **Syntax Highlighting**: SQL keywords in magenta, strings in green, numbers in blue
- **Alternating Row Colors**: Improved readability for table data
- **Context-Sensitive Help**: Detailed help screens with examples for each command
- **Interactive Examples**: Ready-to-run SQL examples with explanations
- **Query Logging**: Colorful display of query history with timestamps
- **Table Structures**: Visual display of tables with column counts

## Educational Concepts

SQL-ish illustrates several computer science concepts:

- **Set Theory**: Tables as sets of tuples
- **Discrete Mathematics**: Propositional logic for query conditions
- **Data Structures**: Efficient table and index representations
- **Algorithms**: Query planning and execution
- **Human-Computer Interaction**: CLI design with helpful feedback

## Project Structure

```
sql_ish/
├── cli/       # Command-line interface components
├── engine/    # Core database engine
├── parser/    # SQL parsing and execution
├── utils/     # Utility functions
├── main.py    # Main entry point
└── __main__.py # Package execution script
```

## Requirements

- Python 3.6+
- colorama (for colored CLI output)
- readline (used automatically on Unix/macOS)
- pyreadline3 (for Windows platforms only)

## Configuration

SQL-ish automatically adapts to your terminal:

- Detects terminal dimensions for proper formatting
- Forces color output when supported, falls back gracefully when not
- Stores command history and query logs in your home directory
- Adapts to platform-specific requirements (Windows/macOS/Linux)

## License

This project is created for educational purposes.

```

```
