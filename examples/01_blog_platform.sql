-- SQL-ish Blog Platform Example
-- This script demonstrates using SQL-ish to manage a simple blog platform database

-- Create a table for blog users
CREATE TABLE users (id, username, email, join_date, is_admin);

-- Insert some users
INSERT INTO users VALUES (1, 'johndoe', 'john@example.com', '2023-01-15', 1);
INSERT INTO users VALUES (2, 'janeblogger', 'jane@example.com', '2023-02-20', 0);
INSERT INTO users VALUES (3, 'techwriter', 'tech@example.com', '2023-03-10', 0);
INSERT INTO users VALUES (4, 'contentcreator', 'creator@example.com', '2023-04-05', 0);
INSERT INTO users VALUES (5, 'adminuser', 'admin@example.com', '2022-12-01', 1);

-- Create a table for blog posts
CREATE TABLE posts (id, user_id, title, content, publish_date, view_count);

-- Insert some blog posts
INSERT INTO posts VALUES (101, 1, 'Getting Started with SQL', 'SQL is a powerful language for managing data...', '2023-02-01', 356);
INSERT INTO posts VALUES (102, 2, 'My Travel Adventures', 'Last summer I visited these amazing places...', '2023-03-15', 127);
INSERT INTO posts VALUES (103, 3, 'Tech Trends 2023', 'The top technology trends to watch this year...', '2023-04-10', 842);
INSERT INTO posts VALUES (104, 3, 'Programming Tips', 'Here are my favorite programming tips and tricks...', '2023-05-05', 513);
INSERT INTO posts VALUES (105, 1, 'Database Design Basics', 'The fundamentals of good database design...', '2023-05-20', 295);
INSERT INTO posts VALUES (106, 4, 'Content Creation 101', 'How to create engaging content for your audience...', '2023-06-01', 741);

-- Create a table for comments
CREATE TABLE comments (id, post_id, user_id, content, comment_date);

-- Insert some comments
INSERT INTO comments VALUES (1001, 101, 2, 'Great introduction to SQL!', '2023-02-02');
INSERT INTO comments VALUES (1002, 101, 3, 'This helped me understand the basics.', '2023-02-03');
INSERT INTO comments VALUES (1003, 102, 1, 'Awesome travel photos!', '2023-03-16');
INSERT INTO comments VALUES (1004, 103, 4, 'I agree with your tech predictions.', '2023-04-11');
INSERT INTO comments VALUES (1005, 103, 5, 'Interesting perspective on AI trends.', '2023-04-12');
INSERT INTO comments VALUES (1006, 104, 1, 'These tips improved my coding!', '2023-05-06');
INSERT INTO comments VALUES (1007, 106, 2, 'Just what I needed for my blog.', '2023-06-02');
INSERT INTO comments VALUES (1008, 106, 3, 'Could you cover SEO next?', '2023-06-03');

-- Basic queries

-- Show all users
SELECT * FROM users;

-- Show all admin users
SELECT username, email FROM users WHERE is_admin = 1;

-- Show recent posts with high view counts
SELECT title, publish_date, view_count FROM posts WHERE view_count > 300;

-- Show posts by specific user
SELECT title, publish_date FROM posts WHERE user_id = 3;

-- Show comments for a specific post
SELECT user_id, content FROM comments WHERE post_id = 106; 