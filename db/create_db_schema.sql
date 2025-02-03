CREATE SCHEMA my_schema;

CREATE TABLE my_schema.User(
	id SERIAL PRIMARY KEY, 
	name VARCHAR(100),
	username VARCHAR(100),
	password VARCHAR(100)
);

CREATE TABLE my_schema.Client(
	client_id SERIAL PRIMARY KEY,
	first_name VARCHAR(100),
	last_name VARCHAR(100),
	address VARCHAR(200),
	status VARCHAR(50),
	email VARCHAR(100) UNIQUE,
	phone VARCHAR(20),
	age INT,
	thumbnail TEXT,
	photo TEXT
);

CREATE TABLE my_schema.Task (
    id SERIAL PRIMARY KEY,
	client_id INTEGER NOT NULL,
    reminder_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    date_time TIMESTAMP NOT NULL,
    repeat_days TEXT, -- Stores comma-separated values like 'Sun,Mon,Wed'
    notes TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (client_id) REFERENCES my_schema.client(client_id) ON DELETE CASCADE
);

