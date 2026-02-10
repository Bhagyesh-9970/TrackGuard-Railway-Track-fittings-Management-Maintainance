import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS fittings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_code TEXT,
    type TEXT,
    location TEXT,
    batch_no TEXT,
    install_date TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_code TEXT,
    inspector TEXT,
    condition_report TEXT,
    remarks TEXT,
    date TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("Database Created Successfully")
 
