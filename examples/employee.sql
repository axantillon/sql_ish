-- SQL-ish Employee Management Example
-- This script demonstrates using SQL-ish to manage a company's employee database

-- Create departments table
CREATE TABLE departments (id, name, location, budget);

-- Insert department data
INSERT INTO departments VALUES (1, 'Engineering', 'Building A', 1500000);
INSERT INTO departments VALUES (2, 'Marketing', 'Building B', 800000);
INSERT INTO departments VALUES (3, 'Human Resources', 'Building A', 500000);
INSERT INTO departments VALUES (4, 'Sales', 'Building C', 1200000);
INSERT INTO departments VALUES (5, 'Research', 'Building D', 2000000);

-- Create employees table
CREATE TABLE employees (id, first_name, last_name, department_id, position, salary, hire_date);

-- Insert employee data
INSERT INTO employees VALUES (101, 'Alice', 'Johnson', 1, 'Senior Developer', 95000, '2020-03-15');
INSERT INTO employees VALUES (102, 'Bob', 'Smith', 1, 'Software Engineer', 85000, '2021-06-10');
INSERT INTO employees VALUES (103, 'Carol', 'Williams', 2, 'Marketing Manager', 88000, '2019-11-05');
INSERT INTO employees VALUES (104, 'David', 'Brown', 2, 'Marketing Specialist', 65000, '2022-01-20');
INSERT INTO employees VALUES (105, 'Eve', 'Davis', 3, 'HR Director', 92000, '2018-05-12');
INSERT INTO employees VALUES (106, 'Frank', 'Miller', 3, 'Recruiter', 60000, '2021-09-08');
INSERT INTO employees VALUES (107, 'Grace', 'Wilson', 4, 'Sales Manager', 90000, '2019-08-14');
INSERT INTO employees VALUES (108, 'Henry', 'Moore', 4, 'Account Executive', 75000, '2020-10-22');
INSERT INTO employees VALUES (109, 'Irene', 'Taylor', 5, 'Research Scientist', 98000, '2017-04-18');
INSERT INTO employees VALUES (110, 'Jack', 'Anderson', 5, 'Lab Technician', 62000, '2022-03-01');

-- Create projects table
CREATE TABLE projects (id, name, start_date, end_date, department_id, budget);

-- Insert project data
INSERT INTO projects VALUES (201, 'Website Redesign', '2023-01-10', '2023-04-30', 1, 150000);
INSERT INTO projects VALUES (202, 'Mobile App Development', '2023-02-15', '2023-07-31', 1, 280000);
INSERT INTO projects VALUES (203, 'Summer Marketing Campaign', '2023-04-01', '2023-08-31', 2, 120000);
INSERT INTO projects VALUES (204, 'Employee Wellness Program', '2023-03-01', '2023-12-31', 3, 75000);
INSERT INTO projects VALUES (205, 'New Market Expansion', '2023-05-15', '2023-11-30', 4, 350000);
INSERT INTO projects VALUES (206, 'Product Innovation', '2023-01-20', '2023-10-15', 5, 420000);

-- Create project_assignments table
CREATE TABLE project_assignments (employee_id, project_id, role, hours_assigned);

-- Insert project assignment data
INSERT INTO project_assignments VALUES (101, 201, 'Lead Developer', 120);
INSERT INTO project_assignments VALUES (102, 201, 'Frontend Developer', 160);
INSERT INTO project_assignments VALUES (101, 202, 'Technical Advisor', 80);
INSERT INTO project_assignments VALUES (102, 202, 'Mobile Developer', 200);
INSERT INTO project_assignments VALUES (103, 203, 'Project Manager', 100);
INSERT INTO project_assignments VALUES (104, 203, 'Content Creator', 150);
INSERT INTO project_assignments VALUES (105, 204, 'Program Director', 60);
INSERT INTO project_assignments VALUES (106, 204, 'Program Coordinator', 120);
INSERT INTO project_assignments VALUES (107, 205, 'Strategy Lead', 90);
INSERT INTO project_assignments VALUES (108, 205, 'Market Analyst', 140);
INSERT INTO project_assignments VALUES (109, 206, 'Research Lead', 180);
INSERT INTO project_assignments VALUES (110, 206, 'Research Assistant', 200);

-- Basic queries

-- List all employees with their department names
SELECT employees.first_name, employees.last_name, departments.name 
FROM employees;

-- Show employees with salary above 80000
SELECT first_name, last_name, position, salary FROM employees WHERE salary > 80000;

-- List all projects with their department
SELECT projects.name, departments.name FROM projects;

-- Find employees working on specific project
SELECT employees.first_name, employees.last_name, project_assignments.role 
FROM project_assignments WHERE project_id = 202;

-- Show projects with large budgets
SELECT name, budget FROM projects WHERE budget > 200000; 