# backend/routes/admin.py
from flask import Blueprint, request, jsonify
from db import get_db

admin_api = Blueprint("admin_api", __name__)

# --- SETTINGS ---
@admin_api.route("/settings/get", methods=["GET"])
def get_settings():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, data_retention, auto_backup, inspection_interval FROM settings LIMIT 1")
    row = cur.fetchone()
    if row:
        return jsonify(dict(row))
    # default
    return jsonify({
        "id": 1,
        "data_retention": "3 years",
        "auto_backup": "Weekly",
        "inspection_interval": 6
    })

@admin_api.route("/settings/update", methods=["POST"])
def update_settings():
    data = request.json
    db = get_db()
    cur = db.cursor()
    # create table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      data_retention TEXT,
      auto_backup TEXT,
      inspection_interval INTEGER
    )
    """)
    # ensure row exists
    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO settings (data_retention, auto_backup, inspection_interval) VALUES (?, ?, ?)",
                    (data.get("data_retention","3 years"), data.get("auto_backup","Weekly"), data.get("inspection_interval",6)))
    else:
        cur.execute("UPDATE settings SET data_retention=?, auto_backup=?, inspection_interval=? WHERE id=?",
                    (data.get("data_retention","3 years"), data.get("auto_backup","Weekly"), data.get("inspection_interval",6), 1))
    db.commit()
    return jsonify({"message":"Settings updated"})


# --- VENDORS CRUD ---
@admin_api.route("/vendors/list", methods=["GET"])
def vendors_list():
    db = get_db()
    cur = db.cursor()
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
    db.commit()

    cur.execute("SELECT id, name, evaluation_date, quality_score, delivery_score, overall_rating, status FROM vendors ORDER BY overall_rating DESC")
    rows = cur.fetchall()
    # convert sqlite3.Row to dict
    return jsonify([dict(r) for r in rows])

@admin_api.route("/vendors", methods=["POST"])
def add_vendor():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("""
      INSERT INTO vendors (name, evaluation_date, quality_score, delivery_score, overall_rating, status)
      VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("evaluation_date"),
        int(data.get("quality_score",0)),
        int(data.get("delivery_score",0)),
        int(data.get("overall_rating",0)),
        data.get("status","Under Review")
    ))
    db.commit()
    vid = cur.lastrowid
    cur.execute("SELECT id, name, evaluation_date, quality_score, delivery_score, overall_rating, status FROM vendors WHERE id=?", (vid,))
    return jsonify(dict(cur.fetchone()))

@admin_api.route("/vendors/<int:vendor_id>", methods=["PUT"])
def update_vendor(vendor_id):
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("""
      UPDATE vendors SET name=?, evaluation_date=?, quality_score=?, delivery_score=?, overall_rating=?, status=? 
      WHERE id=?
    """, (
        data.get("name"),
        data.get("evaluation_date"),
        int(data.get("quality_score",0)),
        int(data.get("delivery_score",0)),
        int(data.get("overall_rating",0)),
        data.get("status","Under Review"),
        vendor_id
    ))
    db.commit()
    cur.execute("SELECT id, name, evaluation_date, quality_score, delivery_score, overall_rating, status FROM vendors WHERE id=?", (vendor_id,))
    row = cur.fetchone()
    return jsonify(dict(row)) if row else (jsonify({"error":"not found"}), 404)

@admin_api.route("/vendors/<int:vendor_id>", methods=["DELETE"])
def delete_vendor(vendor_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM vendors WHERE id=?", (vendor_id,))
    db.commit()
    return jsonify({"message":"deleted", "id": vendor_id})


# --- ANALYTICS ---
@admin_api.route("/analytics", methods=["GET"])
def analytics():
    """
    Return sample analytics:
      - monthly_inspections: list of {month, inspections_count}
      - vendor_distribution: counts per status
    We'll compute from simple tables if present (inspections/vendors).
    """
    db = get_db()
    cur = db.cursor()

    # monthly inspections (from inspections table if exists)
    try:
        cur.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as cnt
            FROM inspections
            GROUP BY month
            ORDER BY month ASC
            LIMIT 12
        """)
        rows = cur.fetchall()
        monthly = [{"month": r["month"], "count": r["cnt"]} for r in rows]
    except Exception:
        # no inspections table or error -> fallback sample
        monthly = [
            {"month":"2024-12","count":120},
            {"month":"2025-01","count":150},
            {"month":"2025-02","count":180},
            {"month":"2025-03","count":130},
            {"month":"2025-04","count":170},
            {"month":"2025-05","count":190},
            {"month":"2025-06","count":200}
        ]

    # vendor distribution by status
    cur.execute("SELECT status, COUNT(*) as cnt FROM vendors GROUP BY status")
    rows = cur.fetchall()
    distribution = [{"status": r["status"], "count": r["cnt"]} for r in rows]

    return jsonify({
        "monthly_inspections": monthly,
        "vendor_distribution": distribution
    })
