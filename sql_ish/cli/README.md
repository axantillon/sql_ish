# SQL-ish CLI

The SQL-ish Command Line Interface provides an interactive way to work with SQL-ish databases.

## Features

- Interactive REPL for SQL-ish queries
- SQL script file execution with error handling
- Command-line arguments for non-interactive use
- Improved error handling and reporting
- Table management commands
- Support for comments in SQL scripts

## Usage

### Interactive Mode

```bash
python3 -m sql_ish
```

This launches the SQL-ish CLI in interactive mode, where you can enter SQL-ish queries directly.

### Run a SQL Script

```bash
python3 -m sql_ish --script path/to/script.sql
```

This launches the CLI and runs the specified script file at startup.

### Execute a Single Query

```bash
python3 -m sql_ish --execute "CREATE TABLE users (id, name, email)"
```

This executes a single query and exits without launching the interactive CLI.

### Direct Script Execution

```bash
python3 -m sql_ish.main --script path/to/script.sql
```

This executes the script and exits without launching the interactive CLI.

### Script Execution Options

By default, script execution will continue even if errors are encountered. You can change this behavior with the `--stop-on-error` flag:

```bash
python3 -m sql_ish.main --script path/to/script.sql --stop-on-error
```

## CLI Commands

Inside the interactive CLI, you can use the following commands:

- `exit`, `quit` - Exit the CLI
- `tables` - List all tables in the database
- `run <filepath>` - Execute SQL commands from a file
- `help` - Show help message

## SQL-ish Script Files

SQL-ish script files should contain SQL commands separated by semicolons.

Example:

```sql
-- Create a users table
CREATE TABLE users (id, name, email, age);

-- Insert some user data
INSERT INTO users VALUES (1, "John Doe", "john@example.com", 30);
INSERT INTO users VALUES (2, "Jane Smith", "jane@example.com", 25);

-- Query the data
SELECT * FROM users;
```

### Comments

SQL-ish script files support single-line comments using the double-dash (`--`) notation. Comments are ignored during script execution.

## Error Handling

When executing script files, the CLI provides detailed error messages and allows you to choose whether to continue after encountering an error. In non-interactive mode, scripts will continue executing after errors by default, unless the `--stop-on-error` flag is specified.

## Example

```
$ python3 -m sql_ish
sql-ish> CREATE TABLE users (id, name, email)
Query executed successfully
sql-ish> INSERT INTO users VALUES (1, "John", "john@example.com")
Query executed successfully
sql-ish> SELECT * FROM users
Table: users
| id | name | email            |
|----|------|------------------|
| 1  | John | john@example.com |
sql-ish> exit
Goodbye!
```
