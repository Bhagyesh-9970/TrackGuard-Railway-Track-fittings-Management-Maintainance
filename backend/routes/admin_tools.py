# backend/routes/admin_tools.py
from flask import Blueprint, request, jsonify, send_file, current_app
from db import get_db
import io
import csv
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

admin_tools = Blueprint("admin_tools", __name__)

# -------------------------
# helper to fetch vendors
# -------------------------
def fetch_vendors():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, evaluation_date, quality_score, delivery_score, overall_rating, status FROM vendors")
    rows = cur.fetchall()
    vendors = []
    for r in rows:
        vendors.append({
            "id": r["id"],
            "name": r["name"],
            "evaluation_date": r["evaluation_date"],
            "quality_score": r["quality_score"],
            "delivery_score": r["delivery_score"],
            "overall_rating": r["overall_rating"],
            "status": r["status"]
        })
    return vendors

# -------------------------
# AI Chat endpoint (rule-based)
# -------------------------
@admin_tools.route("/api/admin/chat", methods=["POST"])
def admin_chat():
    data = request.json or {}
    message = (data.get("message") or "").strip().lower()
    if not message:
        return jsonify({"error": "Empty message"}), 400

    vendors = fetch_vendors()

    # simple rules
    if "summary" in message or "overview" in message or "status" in message:
        total = len(vendors)
        avg = round(sum(v["overall_rating"] for v in vendors) / total, 1) if total else 0
        top = max(vendors, key=lambda x: x["overall_rating"]) if vendors else None
        risks = [v for v in vendors if v["overall_rating"] < 40]
        reply = f"Overview: {total} vendors tracked. Average overall rating: {avg}%. "
        if top:
            reply += f"Top vendor is {top['name']} ({top['overall_rating']}%). "
        if risks:
            reply += f"{len(risks)} vendors flagged as at-risk (rating < 40%)."
        else:
            reply += "No vendors currently flagged as at-risk."
        return jsonify({"reply": reply})

    if "top" in message:
        top = max(vendors, key=lambda x: x["overall_rating"]) if vendors else None
        if top:
            reply = (f"Top vendor: {top['name']} — Overall {top['overall_rating']}%, "
                     f"Quality {top['quality_score']}%, Delivery {top['delivery_score']}%.")
        else:
            reply = "No vendors found."
        return jsonify({"reply": reply})

    if "risk" in message or "low" in message or "problem" in message:
        risks = [v for v in vendors if v["overall_rating"] < 40]
        if risks:
            reply_lines = [f"{v['name']} ({v['overall_rating']}%) - status:{v['status']}" for v in risks]
            reply = "Vendors at risk:\n" + "\n".join(reply_lines)
        else:
            reply = "No vendors currently under the risk threshold."
        return jsonify({"reply": reply})

    # fallback: attempt to answer numeric queries like "how many vendors above 80"
    import re
    m = re.search(r"above\s+(\d+)", message)
    if m:
        threshold = int(m.group(1))
        count = sum(1 for v in vendors if v["overall_rating"] >= threshold)
        reply = f"{count} vendors have overall rating >= {threshold}%."
        return jsonify({"reply": reply})

    # default reply - suggest queries
    help_msg = ("I can provide summaries (try 'summary'), top vendors (try 'top'), "
                "risk list (try 'risk'), or numeric queries (e.g. 'above 80').")
    return jsonify({"reply": help_msg})


# -------------------------
# Export report endpoint (CSV / Excel / PDF)
# -------------------------
@admin_tools.route("/api/admin/reports/export", methods=["GET"])
def export_report():
    typ = (request.args.get("type") or "csv").lower()
    vendors = fetch_vendors()

    # create dataframe
    df = pd.DataFrame(vendors)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"vendors_report_{timestamp}"

    if typ == "csv":
        mem = io.StringIO()
        df.to_csv(mem, index=False)
        mem.seek(0)
        return send_file(io.BytesIO(mem.getvalue().encode("utf-8")),
                         mimetype="text/csv",
                         download_name=f"{filename_base}.csv",
                         as_attachment=True)

    if typ in ("excel", "xlsx"):
        mem = io.BytesIO()
        with pd.ExcelWriter(mem, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="vendors")
            writer.save()
        mem.seek(0)
        return send_file(mem,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         download_name=f"{filename_base}.xlsx",
                         as_attachment=True)

    if typ == "pdf":
        mem = io.BytesIO()
        # create a landscape A4 PDF table
        doc = SimpleDocTemplate(mem, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []
        title = Paragraph("Vendors Audit Report", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # build table data
        cols = ["ID", "Name", "Date", "Quality", "Delivery", "Overall", "Status"]
        data = [cols]
        for v in vendors:
            data.append([
                v.get("id"), v.get("name"), v.get("evaluation_date"),
                f"{v.get('quality_score')}%", f"{v.get('delivery_score')}%",
                f"{v.get('overall_rating')}%", v.get("status")
            ])

        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d47a1')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        story.append(tbl)
        doc.build(story)
        mem.seek(0)
        return send_file(mem, mimetype="application/pdf", download_name=f"{filename_base}.pdf", as_attachment=True)

    return jsonify({"error": "unsupported type"}), 400
 
