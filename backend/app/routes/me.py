from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from .. import db

bp = Blueprint("me", __name__)

def _me_id() -> int:
    return int(get_jwt_identity())

@bp.get("/me")
@jwt_required()
def me_get():
    uid = _me_id()
    row = db.session.execute(text("""
        SELECT id, full_name, email, phone, role, created_at, updated_at
        FROM users WHERE id=:id
    """), {"id": uid}).mappings().first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    out = dict(row)
    out["created_at"] = out["created_at"].isoformat() if out.get("created_at") else None
    out["updated_at"] = out["updated_at"].isoformat() if out.get("updated_at") else None
    return jsonify(out)

@bp.patch("/me")
@jwt_required()
def me_update():
    uid = _me_id()
    data = request.get_json() or {}
    fields = []
    params = {"id": uid}
    for f in ("full_name", "phone"):
        if f in data:
            fields.append(f"{f}=:{f}")
            params[f] = data[f]
    if not fields:
        return jsonify({"error": "Nothing to update"}), 400
    db.session.execute(text(f"UPDATE users SET {', '.join(fields)} WHERE id=:id"), params)
    db.session.commit()
    return jsonify({"ok": True})

@bp.patch("/me/password")
@jwt_required()
def me_change_password():
    from werkzeug.security import check_password_hash, generate_password_hash
    uid = _me_id()
    data = request.get_json() or {}
    cur = data.get("current_password") or ""
    new = data.get("new_password") or ""
    if len(new) < 6:
        return jsonify({"error": "New password too short"}), 400

    row = db.session.execute(text("SELECT password_hash FROM users WHERE id=:id"), {"id": uid}).first()
    if not row or not check_password_hash(row[0], cur):
        return jsonify({"error": "Current password invalid"}), 400

    new_hash = generate_password_hash(new)
    db.session.execute(text("UPDATE users SET password_hash=:ph WHERE id=:id"), {"ph": new_hash, "id": uid})
    db.session.commit()
    return jsonify({"ok": True})

@bp.get("/me/reports/hotel/<int:hotel_id>/count")
@jwt_required()
def me_hotel_count(hotel_id: int):
    uid = _me_id()
    n = db.session.execute(text("""
        SELECT COUNT(*)::int
        FROM bookings
        WHERE hotel_id=:hid AND guest_user_id=:uid AND status <> 'cancelled'
    """), {"hid": hotel_id, "uid": uid}).scalar_one()
    return jsonify({"user_id": uid, "hotel_id": hotel_id, "count": n})
