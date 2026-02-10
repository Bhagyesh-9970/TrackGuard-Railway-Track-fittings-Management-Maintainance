from flask import Blueprint, request
from db import get_db

scan_api = Blueprint("scan_api", __name__)

@scan_api.route("/lookup/<qr_id>")
def lookup(qr_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM fittings WHERE qr_code=?", (qr_id,))
    row = cursor.fetchone()

    if not row:
        return {"error": "QR not found"}, 404

    return dict(row)


@scan_api.route("/inspection/save", methods=["POST"])
def save_inspection():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO inspections (fitting_id, status, comments, date)
        VALUES (?, ?, ?, date('now'))
    """, (data["fitting_id"], data["status"], data["comments"]))

    db.commit()
    return {"message": "Inspection saved"}
 
