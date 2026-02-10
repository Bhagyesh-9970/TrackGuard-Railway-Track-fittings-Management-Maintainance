from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db

auth_api = Blueprint("auth_api", __name__)


@auth_api.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = data["password"]
    role = data.get("role", "inspector")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return {"error": "User already exists"}, 400

    hashed = generate_password_hash(password)

    cursor.execute(
        "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
        (email, hashed, role),
    )
    db.commit()

    return {"message": "User registered successfully"}


@auth_api.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user or not check_password_hash(user["password"], password):
        return {"error": "Invalid email or password"}, 401

    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    return {"message": "Login successful", "role": user["role"]}


@auth_api.route("/logout")
def logout():
    session.clear()
    return {"message": "Logged out"}


@auth_api.route("/check")
def check():
    if "user_id" in session:
        return {"logged_in": True, "email": session["email"], "role": session["role"]}
    return {"logged_in": False}
 
