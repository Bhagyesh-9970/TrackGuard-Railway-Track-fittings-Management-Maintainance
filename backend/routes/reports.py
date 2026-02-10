from flask import Blueprint
from db import get_db

reports_api = Blueprint("reports_api", __name__)

@reports_api.route("/history/<qr>")
def history(qr):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM inspections WHERE qr_code=? ORDER BY date DESC",
        (qr,)
    )

    rows = cursor.fetchall()

    return {"history": [dict(row) for row in rows]}
