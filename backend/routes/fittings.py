from flask import Blueprint, request
from db import get_db
import qrcode
import sqlite3

fittings_api = Blueprint("fittings_api", __name__)

@fittings_api.route("/add", methods=["POST"])
def add_fitting():
    data = request.json

    type_ = data.get("type")
    location = data.get("location")
    batch = data.get("batch")

    qr_text = f"{type_}-{batch}-{location}"

    # Generate QR Code
    qr_img = qrcode.make(qr_text)
    qr_img.save(f"static/qr_codes/{qr_text}.png")

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO fittings (qr_code, type, location, batch_no) VALUES (?, ?, ?, ?)",
        (qr_text, type_, location, batch)
    )

    db.commit()

    return {"status": "success", "qr_code": qr_text}


@fittings_api.route("/scan/<qr>", methods=["GET"])
def get_fitting(qr):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM fittings WHERE qr_code=?", (qr,))
    row = cursor.fetchone()

    if row is None:
        return {"error": "QR not found"}

    return dict(row)
