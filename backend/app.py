from flask import Flask, render_template, redirect, session, request
from flask_cors import CORS

# Create app first
app = Flask(__name__)
app.secret_key = "bmm"

CORS(app)

# NOW import blueprints
from routes.fittings import fittings_api
from routes.inspections import inspections_api
from routes.reports import reports_api
from routes.admin import admin_api
from routes.auth import auth_api
from routes.scan import scan_api
from routes.admin_tools import admin_tools

# Register blueprints
app.register_blueprint(auth_api, url_prefix="/api/auth")
app.register_blueprint(admin_api, url_prefix="/api/admin")
app.register_blueprint(scan_api, url_prefix="/api/scan")
app.register_blueprint(fittings_api, url_prefix="/api/fittings")
app.register_blueprint(inspections_api, url_prefix="/api/inspections")
app.register_blueprint(reports_api, url_prefix="/api/reports")
app.register_blueprint(admin_tools)


# -----------------------------
#     LOGIN PROTECTION
# -----------------------------
@app.before_request
def protect_pages():
    open_paths = [
        "/login",
        "/api/auth/login",
        "/api/auth/register",
        "/static/",
    ]

    # allow static files & login/register
    if any(request.path.startswith(p) for p in open_paths):
        return

    # protect all other pages
    if "user_id" not in session:
        return redirect("/login")


# -----------------------------
#        ROUTES
# -----------------------------
@app.route("/")
def root():
    return redirect("/login")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/admin")
def admin_panel():
    return render_template("admin_panel.html")


# -----------------------------
#        RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
