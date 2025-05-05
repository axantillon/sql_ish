# SQL-ish MCP Server Example

This example demonstrates how to use the SQL-ish MCP server with an AI assistant like Claude.

## Starting the Server

First, start the SQL-ish MCP server with a sample database:

```bash
# Initialize a sample database with users and orders
sqlish-mcp --init-script examples/sample_database.sql
```

## Sample Conversations with Claude

Here are some example conversations you could have with Claude when it's connected to your SQL-ish database through MCP:

### Exploring the Database

**User:** What tables are in the database?

**Claude:** I'll check what tables are in the database.

_Claude uses the MCP server to list the tables_

I found the following tables in the SQL-ish database:

- users
- orders
- products

Let me show you the schema for each:

**Users table:**

- id (integer)
- name (text)
- email (text)
- age (integer)

**Orders table:**

- id (integer)
- user_id (integer)
- product_id (integer)
- quantity (integer)
- order_date (text)

**Products table:**

- id (integer)
- name (text)
- price (decimal)
- category (text)

### Running Queries

**User:** Show me all users older than 30.

**Claude:** I'll query the database for users older than 30.

_Claude executes a query through the MCP server_

Here are the users older than 30:

| id  | name            | email               | age |
| --- | --------------- | ------------------- | --- |
| 2   | Jane Smith      | jane@example.com    | 35  |
| 4   | Michael Johnson | michael@example.com | 42  |
| 5   | Sarah Williams  | sarah@example.com   | 31  |

The query I executed was:

```sql
SELECT * FROM users WHERE age > 30
```

### Data Analysis

**User:** What's the average order value by product category?

**Claude:** I'll calculate the average order value by product category.

_Claude executes multiple queries through the MCP server_

Here's the average order value by product category:

| category    | average_order_value |
| ----------- | ------------------- |
| Electronics | $425.75             |
| Clothing    | $68.33              |
| Books       | $32.50              |
| Home        | $127.99             |

To calculate this, I:

1. Joined the orders and products tables
2. Calculated the value of each order (price \* quantity)
3. Grouped the results by category
4. Calculated the average order value for each group

The main query I executed was:

```sql
SELECT p.category, AVG(p.price * o.quantity) AS average_order_value
FROM orders o
JOIN products p ON o.product_id = p.id
GROUP BY p.category
```

### Creating New Data

**User:** Create a new table for customer reviews.

**Claude:** I'll create a new table for customer reviews.

_Claude executes a query through the MCP server_

I've created a new table called `reviews` with the following structure:

```sql
CREATE TABLE reviews (
  id INTEGER,
  order_id INTEGER,
  rating INTEGER,
  comment TEXT
)
```

The table was created successfully. Now you can add reviews for orders in your database.

Would you like me to insert some sample review data into this table?

## More Complex Example: Analyzing Sales Trends

**User:** Can you analyze our sales trends over time and recommend which product categories we should focus on?

**Claude:** I'll analyze the sales trends over time and provide recommendations on product categories to focus on.

_Claude executes multiple queries through the MCP server_

Based on my analysis of your sales data, here are the key findings:

1. **Overall Sales Trends**:

   - Total sales have increased by 15% over the past quarter
   - Electronics is your highest-grossing category ($25,350)
   - Books have the highest profit margin (68%)

2. **Growth by Category**:

   - Electronics: +8% (steady growth)
   - Clothing: +42% (rapid growth)
   - Books: -3% (slight decline)
   - Home: +22% (moderate growth)

3. **Customer Demographics**:
   - Clothing purchases are popular among younger customers (18-30)
   - Electronics have the highest repeat purchase rate

**Recommendations**:

1. **Primary Focus**: Clothing - This category shows the highest growth rate and appeals to a growing demographic
2. **Secondary Focus**: Home goods - Good profit margins and steady growth
3. **Maintenance Focus**: Electronics - Still your highest revenue generator
4. **Consider Revamping**: Books - Despite high margins, the category is declining

Would you like me to dig deeper into any specific aspect of these trends?
