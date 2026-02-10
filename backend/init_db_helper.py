# backend/init_db_helper.py
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# users table with a default admin (password = admin123)
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")
# create default admin if not exists
cur.execute("SELECT COUNT(*) FROM users WHERE email='admin@gmail.com'")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                ('admin@gmail.com', generate_password_hash('admin123'), 'admin'))

# settings table
cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  data_retention TEXT,
  auto_backup TEXT,
  inspection_interval INTEGER
)
""")
cur.execute("SELECT COUNT(*) FROM settings")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO settings (data_retention, auto_backup, inspection_interval) VALUES ('3 years','Weekly',6)")

# vendors sample
cur.execute("""
CREATE TABLE IF NOT EXISTS vendors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  evaluation_date TEXT,
  quality_score INTEGER,
  delivery_score INTEGER,
  overall_rating INTEGER,
  status TEXT
)
""")
cur.execute("SELECT COUNT(*) FROM vendors")
if cur.fetchone()[0] == 0:
    vendors = [
      ('ABC Steel Works','2023-05-30',96,92,94,'Approved'),
      ('XYZ Polymers','2023-05-28',85,91,88,'Under Review'),
      ('National Foundry','2023-05-25',94,96,95,'Approved')
    ]
    cur.executemany("INSERT INTO vendors (name,evaluation_date,quality_score,delivery_score,overall_rating,status) VALUES (?,?,?,?,?,?)", vendors)

# inspections (optional sample)
cur.execute("""
CREATE TABLE IF NOT EXISTS inspections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fitting_id TEXT,
  status TEXT,
  comments TEXT,
  date TEXT DEFAULT (date('now'))
)
""")

conn.commit()
conn.close()
print("DB initialized (default admin: admin@gmail.com / admin123)")
 
