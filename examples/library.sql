-- SQL-ish Library Management System Example
-- This script demonstrates using SQL-ish to manage a library database

-- Create a table for book categories/genres
CREATE TABLE genres (id, name, description);

-- Insert genre data
INSERT INTO genres VALUES (1, 'Fiction', 'Novels, short stories, and other fictional works');
INSERT INTO genres VALUES (2, 'Non-Fiction', 'Educational and informative books based on facts');
INSERT INTO genres VALUES (3, 'Science Fiction', 'Books featuring futuristic science and technology');
INSERT INTO genres VALUES (4, 'Mystery', 'Books involving solving crimes or mysteries');
INSERT INTO genres VALUES (5, 'Biography', 'Books about real people''s lives');
INSERT INTO genres VALUES (6, 'Fantasy', 'Books featuring magical or supernatural elements');
INSERT INTO genres VALUES (7, 'History', 'Books about historical events and periods');

-- Create a table for authors
CREATE TABLE authors (id, first_name, last_name, birth_year, nationality);

-- Insert author data
INSERT INTO authors VALUES (1, 'Jane', 'Austen', 1775, 'British');
INSERT INTO authors VALUES (2, 'George', 'Orwell', 1903, 'British');
INSERT INTO authors VALUES (3, 'J.K.', 'Rowling', 1965, 'British');
INSERT INTO authors VALUES (4, 'Gabriel', 'García Márquez', 1927, 'Colombian');
INSERT INTO authors VALUES (5, 'Toni', 'Morrison', 1931, 'American');
INSERT INTO authors VALUES (6, 'Haruki', 'Murakami', 1949, 'Japanese');
INSERT INTO authors VALUES (7, 'Stephen', 'Hawking', 1942, 'British');
INSERT INTO authors VALUES (8, 'Agatha', 'Christie', 1890, 'British');

-- Create a table for books
CREATE TABLE books (id, title, author_id, genre_id, publisher, publication_year, isbn, total_copies);

-- Insert book data
INSERT INTO books VALUES (101, 'Pride and Prejudice', 1, 1, 'T. Egerton', 1813, '9780141439518', 5);
INSERT INTO books VALUES (102, '1984', 2, 3, 'Secker & Warburg', 1949, '9780451524935', 7);
INSERT INTO books VALUES (103, 'Harry Potter and the Philosopher''s Stone', 3, 6, 'Bloomsbury', 1997, '9780747532699', 10);
INSERT INTO books VALUES (104, 'One Hundred Years of Solitude', 4, 1, 'Harper & Row', 1970, '9780060883287', 3);
INSERT INTO books VALUES (105, 'Beloved', 5, 1, 'Alfred A. Knopf', 1987, '9781400033416', 4);
INSERT INTO books VALUES (106, 'Norwegian Wood', 6, 1, 'Kodansha', 1987, '9780375704024', 6);
INSERT INTO books VALUES (107, 'A Brief History of Time', 7, 2, 'Bantam Books', 1988, '9780553380163', 8);
INSERT INTO books VALUES (108, 'Murder on the Orient Express', 8, 4, 'Collins Crime Club', 1934, '9780062693662', 5);
INSERT INTO books VALUES (109, 'Emma', 1, 1, 'John Murray', 1815, '9780141439587', 4);
INSERT INTO books VALUES (110, 'And Then There Were None', 8, 4, 'Collins Crime Club', 1939, '9780062073488', 6);

-- Create a table for library members
CREATE TABLE members (id, first_name, last_name, email, phone, join_date, membership_expiry);

-- Insert member data
INSERT INTO members VALUES (1, 'Robert', 'Smith', 'robert.s@example.com', '555-111-2222', '2022-01-10', '2023-01-10');
INSERT INTO members VALUES (2, 'Jennifer', 'Brown', 'jennifer.b@example.com', '555-222-3333', '2022-02-15', '2023-02-15');
INSERT INTO members VALUES (3, 'William', 'Jones', 'william.j@example.com', '555-333-4444', '2022-03-20', '2023-03-20');
INSERT INTO members VALUES (4, 'Elizabeth', 'Miller', 'elizabeth.m@example.com', '555-444-5555', '2022-04-25', '2023-04-25');
INSERT INTO members VALUES (5, 'David', 'Wilson', 'david.w@example.com', '555-555-6666', '2022-05-30', '2023-05-30');

-- Create a table for book loans
CREATE TABLE loans (id, book_id, member_id, checkout_date, due_date, return_date, fine_amount);

-- Insert loan data
INSERT INTO loans VALUES (1001, 101, 1, '2023-01-15', '2023-01-29', '2023-01-27', 0);
INSERT INTO loans VALUES (1002, 103, 2, '2023-02-10', '2023-02-24', '2023-02-22', 0);
INSERT INTO loans VALUES (1003, 105, 3, '2023-03-05', '2023-03-19', '2023-03-25', 6);
INSERT INTO loans VALUES (1004, 107, 4, '2023-04-01', '2023-04-15', NULL, NULL);
INSERT INTO loans VALUES (1005, 109, 5, '2023-04-10', '2023-04-24', '2023-04-20', 0);
INSERT INTO loans VALUES (1006, 102, 1, '2023-05-01', '2023-05-15', NULL, NULL);
INSERT INTO loans VALUES (1007, 104, 2, '2023-05-05', '2023-05-19', '2023-05-17', 0);
INSERT INTO loans VALUES (1008, 106, 3, '2023-05-10', '2023-05-24', NULL, NULL);

-- Example queries

-- List all books with their authors and genres
SELECT books.title, authors.first_name, authors.last_name, genres.name
FROM books;

-- Find currently borrowed books (not returned yet)
SELECT books.title, members.first_name, members.last_name, loans.checkout_date, loans.due_date
FROM books, loans, members
WHERE loans.return_date IS NULL;

-- List books by a specific author
SELECT title, publication_year FROM books WHERE author_id = 1;

-- Find overdue books (due date has passed but not returned)
SELECT books.title, members.first_name, members.last_name, loans.due_date
FROM books, loans, members
WHERE loans.return_date IS NULL AND loans.due_date < '2023-05-15';

-- Count books by genre
SELECT genres.name, COUNT(*) FROM books, genres GROUP BY genre_id; 

-- JOIN EXAMPLES

-- JOIN
SELECT * FROM books JOIN authors ON books.author_id = authors.id;
