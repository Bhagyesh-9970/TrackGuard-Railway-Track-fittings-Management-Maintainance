CREATE DATABASE railway_qr;

USE railway_qr;

CREATE TABLE fittings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qr_code VARCHAR(255),
    type VARCHAR(255),
    location VARCHAR(255),
    batch_no VARCHAR(255),
    install_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    qr_code VARCHAR(255),
    inspector VARCHAR(255),
    condition_report VARCHAR(255),
    remarks TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    email TEXT,
    division TEXT,
    notifWarranty INTEGER,
    notifCritical INTEGER,
    notifDaily INTEGER,
    notifWeekly INTEGER,
    dataRetention TEXT,
    autoBackup TEXT,
    inspectionInterval INTEGER
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    quality_score INTEGER,
    delivery_score INTEGER,
    rating INTEGER,
    status TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT,
    role TEXT
);
