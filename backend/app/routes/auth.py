from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .. import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    data = request.get_json() or {}
    for field in ("full_name", "email", "password"):
        if not data.get(field):
            return jsonify({"error": f"Missing {field}"}), 400

    exists = db.session.execute(db.select(User).filter_by(email=data["email"])).scalar()
    if exists:
        return jsonify({"error": "Email already registered"}), 400

    u = User(
        full_name=data["full_name"],
        email=data["email"],
        role="user",
        password_hash=generate_password_hash(data["password"]),
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({"ok": True, "id": u.id})

@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    u = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if not u or not check_password_hash(u.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(u.id), additional_claims={"role": u.role, "email": u.email})
    return jsonify({"access_token": token})
