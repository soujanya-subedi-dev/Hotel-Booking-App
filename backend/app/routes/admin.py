from flask import Blueprint, request, jsonify
from sqlalchemy import text
from flask_jwt_extended import jwt_required
from ..authz import role_required
from .. import db

bp = Blueprint("admin", __name__)

@bp.get("/admin/users")
@jwt_required()
@role_required("admin")
def users():
    rows = db.session.execute(text("""
        SELECT id, full_name, email, phone, role, created_at, updated_at
        FROM users ORDER BY id LIMIT 500
    """)).mappings().all()
    out = []
    for r in rows:
        rec = dict(r)
        rec["created_at"] = rec["created_at"].isoformat() if rec.get("created_at") else None
        rec["updated_at"] = rec["updated_at"].isoformat() if rec.get("updated_at") else None
        out.append(rec)
    return jsonify(out)

@bp.get("/admin/bookings")
@jwt_required()
@role_required("admin")
def bookings():
    rows = db.session.execute(text("""
        SELECT b.id, b.status, b.check_in, b.check_out, b.num_guests, b.total_amount, b.currency,
               u.email AS booked_by, COALESCE(gu.email,'') AS guest_email,
               h.name AS hotel_name, rt.name AS room_type_name
        FROM bookings b
        JOIN users u ON u.id = b.booked_by_user_id
        LEFT JOIN users gu ON gu.id = b.guest_user_id
        JOIN hotels h ON h.id = b.hotel_id
        JOIN room_types rt ON rt.id = b.room_type_id
        ORDER BY b.created_at DESC
        LIMIT 500
    """)).mappings().all()
    out = []
    for r in rows:
        rec = dict(r)
        for k in ("check_in","check_out"):
            rec[k] = rec[k].isoformat() if rec[k] else None
        out.append(rec)
    return jsonify(out)


@bp.patch("/admin/hotels/<int:hotel_id>")
@jwt_required()
@role_required("admin")
def update_hotel(hotel_id: int):
    """Update hotel fields. Accepts partial data."""
    data = request.get_json() or {}
    fields = []
    params = {"id": hotel_id}
    for f in ("name", "city", "country", "address", "description", "amenities"):
        if f in data:
            fields.append(f"{f}=:{f}")
            params[f] = data[f]
    if not fields:
        return jsonify({"error": "Nothing to update"}), 400
    db.session.execute(text(f"UPDATE hotels SET {', '.join(fields)} WHERE id=:id"), params)
    db.session.commit()
    return jsonify({"ok": True})
