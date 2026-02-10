from flask import Blueprint, request
from db import get_db

inspections_api = Blueprint("inspections_api", __name__)

@inspections_api.route("/add", methods=["POST"])
def add_inspection():
    data = request.json

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO inspections (qr_code, inspector, condition_report, remarks) VALUES (?, ?, ?, ?)",
        (
            data["qr_code"],
            data["inspector"],
            data["condition"],
            data["remarks"]
        )
    )

    db.commit()

    return {"status": "inspection added"}
