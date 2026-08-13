-- SelfHealSQL: Database Schema

-- CREATING DATABASE SELFHEALSQL_DB
--CREATE DATABASE SelfHealSQL_DB

-- USING DATABASE
--USE SelfHealSQL_DB

-- SelfHealSQL: Database Schema
-- Run this in SSMS against a new or existing database (e.g. SelfHealSQL_DB)

-- Optional: create a dedicated database
-- CREATE DATABASE SelfHealSQL_DB;
-- GO
-- USE SelfHealSQL_DB;
-- GO

IF OBJECT_ID('OrderDetails', 'U') IS NOT NULL DROP TABLE OrderDetails;
IF OBJECT_ID('Orders', 'U') IS NOT NULL DROP TABLE Orders;
IF OBJECT_ID('Products', 'U') IS NOT NULL DROP TABLE Products;
IF OBJECT_ID('Customers', 'U') IS NOT NULL DROP TABLE Customers;

-- CUSTOMERS TABLE--
CREATE TABLE Customers (
    CustomerID      INT IDENTITY(1,1) PRIMARY KEY,
    FirstName       VARCHAR(50)  NOT NULL,
    LastName        VARCHAR(50)  NOT NULL,
    Email           VARCHAR(100) NOT NULL,
    City            VARCHAR(50)  NOT NULL,
    State           VARCHAR(50)  NOT NULL,
    Segment         VARCHAR(20)  NOT NULL,   -- e.g. 'Regular', 'Premium', 'VIP'
    SignupDate      DATE         NOT NULL
);


-- PRODUCTS TABLE--
CREATE TABLE Products (
    ProductID       INT IDENTITY(1,1) PRIMARY KEY,
    ProductName     VARCHAR(100) NOT NULL,
    Category        VARCHAR(50)  NOT NULL,
    Price           DECIMAL(10,2) NOT NULL
);


-- ORDER TABLE--
CREATE TABLE Orders (
    OrderID         INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID      INT NOT NULL FOREIGN KEY REFERENCES Customers(CustomerID),
    OrderDate       DATE NOT NULL,
    Status          VARCHAR(20) NOT NULL,    -- 'Completed', 'Failed', 'Pending'
    TotalAmount     DECIMAL(10,2) NOT NULL
);

-- ORDERDETAILS TABLE--
CREATE TABLE OrderDetails (
    OrderDetailID   INT IDENTITY(1,1) PRIMARY KEY,
    OrderID         INT NOT NULL FOREIGN KEY REFERENCES Orders(OrderID),
    ProductID       INT NOT NULL FOREIGN KEY REFERENCES Products(ProductID),
    Quantity        INT NOT NULL,
    UnitPrice       DECIMAL(10,2) NOT NULL
);

-- Quick sanity check after seeding
 SELECT COUNT(*) AS CustomerCount FROM Customers;
 SELECT COUNT(*) AS ProductCount FROM Products;
 SELECT COUNT(*) AS OrderCount FROM Orders;
 SELECT COUNT(*) AS OrderDetailCount FROM OrderDetails;

SELECT Status, COUNT(*) AS Count FROM Orders GROUP BY Status