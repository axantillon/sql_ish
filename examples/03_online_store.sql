-- SQL-ish Online Store Example
-- This script demonstrates using SQL-ish to manage an e-commerce store database

-- Create a table for product categories
CREATE TABLE categories (id, name, description, parent_category_id);

-- Insert category data
INSERT INTO categories VALUES (1, 'Electronics', 'Electronic devices and gadgets', NULL);
INSERT INTO categories VALUES (2, 'Smartphones', 'Mobile phones and accessories', 1);
INSERT INTO categories VALUES (3, 'Laptops', 'Portable computers', 1);
INSERT INTO categories VALUES (4, 'Clothing', 'Apparel and fashion items', NULL);
INSERT INTO categories VALUES (5, 'Men''s Clothing', 'Clothing for men', 4);
INSERT INTO categories VALUES (6, 'Women''s Clothing', 'Clothing for women', 4);
INSERT INTO categories VALUES (7, 'Home & Kitchen', 'Household items', NULL);

-- Create a table for products
CREATE TABLE products (id, name, category_id, price, stock_quantity, description);

-- Insert product data
INSERT INTO products VALUES (101, 'iPhone 14', 2, 999.99, 50, 'Latest Apple smartphone with advanced features');
INSERT INTO products VALUES (102, 'Samsung Galaxy S23', 2, 899.99, 65, 'High-end Android smartphone');
INSERT INTO products VALUES (103, 'MacBook Pro 16"', 3, 2499.99, 20, 'Powerful laptop for professionals');
INSERT INTO products VALUES (104, 'Dell XPS 15', 3, 1899.99, 30, 'Premium Windows laptop');
INSERT INTO products VALUES (105, 'Men''s Casual Shirt', 5, 39.99, 100, 'Comfortable cotton shirt for casual wear');
INSERT INTO products VALUES (106, 'Women''s Summer Dress', 6, 59.99, 75, 'Lightweight summer dress in floral pattern');
INSERT INTO products VALUES (107, 'Coffee Maker', 7, 79.99, 40, '12-cup programmable coffee maker');
INSERT INTO products VALUES (108, 'Blender', 7, 49.99, 55, 'High-speed blender for smoothies and more');
INSERT INTO products VALUES (109, 'Wireless Earbuds', 1, 129.99, 80, 'True wireless earbuds with noise cancellation');
INSERT INTO products VALUES (110, 'Smart Watch', 1, 199.99, 45, 'Fitness tracking smartwatch with heart rate monitor');

-- Create a table for customers
CREATE TABLE customers (id, first_name, last_name, email, phone, join_date);

-- Insert customer data
INSERT INTO customers VALUES (1, 'Michael', 'Johnson', 'michael.j@example.com', '555-123-4567', '2022-01-15');
INSERT INTO customers VALUES (2, 'Emily', 'Davis', 'emily.d@example.com', '555-234-5678', '2022-02-20');
INSERT INTO customers VALUES (3, 'Daniel', 'Wilson', 'daniel.w@example.com', '555-345-6789', '2022-03-10');
INSERT INTO customers VALUES (4, 'Sophia', 'Martinez', 'sophia.m@example.com', '555-456-7890', '2022-04-05');
INSERT INTO customers VALUES (5, 'James', 'Taylor', 'james.t@example.com', '555-567-8901', '2022-05-22');

-- Create a table for orders
CREATE TABLE orders (id, customer_id, order_date, total_amount, status);

-- Insert order data
INSERT INTO orders VALUES (1001, 1, '2023-03-10', 1099.98, 'Delivered');
INSERT INTO orders VALUES (1002, 2, '2023-03-15', 2499.99, 'Shipped');
INSERT INTO orders VALUES (1003, 3, '2023-03-20', 149.97, 'Processing');
INSERT INTO orders VALUES (1004, 4, '2023-03-22', 279.98, 'Delivered');
INSERT INTO orders VALUES (1005, 5, '2023-03-25', 999.99, 'Shipped');
INSERT INTO orders VALUES (1006, 1, '2023-04-05', 129.99, 'Delivered');
INSERT INTO orders VALUES (1007, 3, '2023-04-10', 1899.99, 'Delivered');

-- Create a table for order items
CREATE TABLE order_items (order_id, product_id, quantity, unit_price);

-- Insert order item data
INSERT INTO order_items VALUES (1001, 101, 1, 999.99);
INSERT INTO order_items VALUES (1001, 109, 1, 99.99);
INSERT INTO order_items VALUES (1002, 103, 1, 2499.99);
INSERT INTO order_items VALUES (1003, 105, 2, 39.99);
INSERT INTO order_items VALUES (1003, 106, 1, 69.99);
INSERT INTO order_items VALUES (1004, 107, 1, 79.99);
INSERT INTO order_items VALUES (1004, 108, 1, 49.99);
INSERT INTO order_items VALUES (1004, 109, 1, 129.99);
INSERT INTO order_items VALUES (1005, 101, 1, 999.99);
INSERT INTO order_items VALUES (1006, 109, 1, 129.99);
INSERT INTO order_items VALUES (1007, 104, 1, 1899.99);

-- Basic queries

-- List all products with prices
SELECT name, price FROM products;

-- Show products with low stock (less than 30 units)
SELECT name, stock_quantity FROM products WHERE stock_quantity < 30;

-- Find expensive electronics products
SELECT name, price FROM products WHERE category_id = 1 AND price > 150;

-- List orders for a specific customer
SELECT id, order_date, total_amount, status FROM orders WHERE customer_id = 1;

-- Show products in the Clothing category
SELECT products.name, products.price FROM products WHERE category_id = 5 OR category_id = 6; 