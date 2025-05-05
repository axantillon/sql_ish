-- Sample database for SQL-ish MCP server example
-- This script creates tables for users, products, and orders with sample data

-- Create users table
CREATE TABLE users (
    id INTEGER,
    name TEXT,
    email TEXT,
    age INTEGER
);

-- Insert sample users
INSERT INTO users VALUES (1, 'John Doe', 'john@example.com', 28);
INSERT INTO users VALUES (2, 'Jane Smith', 'jane@example.com', 35);
INSERT INTO users VALUES (3, 'Alice Brown', 'alice@example.com', 22);
INSERT INTO users VALUES (4, 'Michael Johnson', 'michael@example.com', 42);
INSERT INTO users VALUES (5, 'Sarah Williams', 'sarah@example.com', 31);

-- Create products table
CREATE TABLE products (
    id INTEGER,
    name TEXT,
    price DECIMAL,
    category TEXT
);

-- Insert sample products
INSERT INTO products VALUES (101, 'Laptop', 899.99, 'Electronics');
INSERT INTO products VALUES (102, 'Smartphone', 499.99, 'Electronics');
INSERT INTO products VALUES (103, 'Headphones', 89.99, 'Electronics');
INSERT INTO products VALUES (104, 'T-shirt', 19.99, 'Clothing');
INSERT INTO products VALUES (105, 'Jeans', 49.99, 'Clothing');
INSERT INTO products VALUES (106, 'Dress Shirt', 39.99, 'Clothing');
INSERT INTO products VALUES (107, 'Novel', 12.99, 'Books');
INSERT INTO products VALUES (108, 'Cookbook', 24.99, 'Books');
INSERT INTO products VALUES (109, 'Coffee Maker', 79.99, 'Home');
INSERT INTO products VALUES (110, 'Blender', 59.99, 'Home');

-- Create orders table
CREATE TABLE orders (
    id INTEGER,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date TEXT
);

-- Insert sample orders
INSERT INTO orders VALUES (1001, 1, 101, 1, '2024-01-15');
INSERT INTO orders VALUES (1002, 1, 104, 2, '2024-01-15');
INSERT INTO orders VALUES (1003, 2, 102, 1, '2024-01-18');
INSERT INTO orders VALUES (1004, 3, 103, 1, '2024-01-20');
INSERT INTO orders VALUES (1005, 3, 105, 1, '2024-01-20');
INSERT INTO orders VALUES (1006, 4, 110, 2, '2024-01-22');
INSERT INTO orders VALUES (1007, 5, 107, 3, '2024-01-25');
INSERT INTO orders VALUES (1008, 2, 109, 1, '2024-01-28');
INSERT INTO orders VALUES (1009, 4, 108, 1, '2024-02-01');
INSERT INTO orders VALUES (1010, 1, 106, 1, '2024-02-05');
INSERT INTO orders VALUES (1011, 5, 103, 1, '2024-02-08');
INSERT INTO orders VALUES (1012, 3, 101, 1, '2024-02-10');
INSERT INTO orders VALUES (1013, 2, 104, 3, '2024-02-12');
INSERT INTO orders VALUES (1014, 4, 102, 1, '2024-02-15');
INSERT INTO orders VALUES (1015, 5, 110, 1, '2024-02-18'); 