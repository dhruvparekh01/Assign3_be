CREATE DATABASE final_project;
\c final_project;

GRANT CONNECT ON DATABASE final_project TO admin;

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
