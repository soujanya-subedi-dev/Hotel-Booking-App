from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .. import db
from ..models import User

bp = Blueprint('auth', __name__)

@bp.post('/register')
def register():
    data = request.get_json() or {}
    for field in ('full_name','email','password'):
        if field not in data:
            return jsonify({"error": f"Missing {field}"}), 400
    if db.session.execute(db.select(User).filter_by(email=data['email'].lower())).scalar():
        return jsonify({"error": "Email already registered"}), 409
    user = User(
        full_name=data['full_name'],
        email=data['email'].lower(),
        role=data.get('role','user'),
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "email": user.email})

@bp.post('/login')
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').lower()
    password = data.get('password') or ''
    user = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity={"id": user.id, "role": user.role, "email": user.email})
    return jsonify({"access_token": token})

    