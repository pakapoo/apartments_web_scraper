USE mysql;
CREATE DATABASE IF NOT EXISTS apartment_db;

USE apartment_db;
CREATE TABLE IF NOT EXISTS unit (
    id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    tel VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(255),
    state VARCHAR(255),
    zip VARCHAR(255),
    neighborhood VARCHAR(255),
    built INT,
    units INT,
    stories INT,
    management VARCHAR(255),
    unit_no VARCHAR(255) NOT NULL,
    unit_beds INT,
    unit_baths INT,
    unit_price DECIMAL(10, 2),
    unit_sqft FLOAT,
    unit_avail DATE,
    PRIMARY KEY (id, unit_no, unit_beds, unit_baths, unit_price, unit_sqft, unit_avail)
);