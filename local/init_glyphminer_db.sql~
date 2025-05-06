-- Create the glyphminer database if it doesn't exist
CREATE DATABASE IF NOT EXISTS glyphminer;

-- Create the user glyphminer@localhost with password 'glyphminer'
CREATE USER IF NOT EXISTS 'glyphminer'@'localhost' IDENTIFIED BY 'glyphminer';

-- Grant privileges to the user on the glyphminer database
GRANT ALL PRIVILEGES ON glyphminer.* TO 'glyphminer'@'localhost';

-- Ensure privilege changes are loaded
FLUSH PRIVILEGES;
