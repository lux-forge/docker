-- Create a new user
CREATE USER user WITH PASSWORD 'password';

-- Create a new db
CREATE DATABASE db;

-- Give user access to db
GRANT ALL PRIVILEGES ON DATABASE db to user;
GRANT ALL ON SCHEMA db.public TO user;

-- OR change the owner
ALTER DATABASE my_database OWNER TO my_database_user;


