JOB SUGGESTION PORTAL:
SET UP DB:
1) create a database : CREATE DATABASE hackbuzz;
2)  use hackbuzz;
3)  create a table : users ->  CREATE TABLE users (
         id SERIAL PRIMARY KEY,
         fullname VARCHAR(255) NOT NULL,
         email VARCHAR(255) NOT NULL UNIQUE,
         password VARCHAR(255) NOT NULL,
         contact_number VARCHAR(20),
         address TEXT,
         city VARCHAR(100),
         zipcode VARCHAR(10),
         job_title VARCHAR(100),
         industry VARCHAR(100),
         experience INT,
         education VARCHAR(255),
         skills TEXT,
         employment_type VARCHAR(50),
         salary_range VARCHAR(50),
         resume_path VARCHAR(255)
     );
4) create a table : jobs -> CREATE TABLE job (
         id SERIAL PRIMARY KEY,
         mail VARCHAR(255) NOT NULL,
         company_name VARCHAR(255) NOT NULL,
         job_title VARCHAR(255) NOT NULL
     );
5) for email and resume prupose contact me
6) to start the program : python app.py
7) run in local host
