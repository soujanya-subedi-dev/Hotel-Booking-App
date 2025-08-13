from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import text
from .. import db
from ..authz import role_required

bp = Blueprint("bookings", __name__)

def _uid() -> int:
    return int(get_jwt_identity())

@bp.get("/bookings")
@jwt_required()
def my_bookings():
    claims = get_jwt()
    is_admin = (claims or {}).get("role") == "admin"
    uid = _uid()
    params = {"uid": uid}
    where = "WHERE b.guest_user_id = :uid OR b.booked_by_user_id = :uid"
    if is_admin and request.args.get("all") == "1":
        where = "WHERE 1=1"
        params = {}
    rows = db.session.execute(text(f"""
        SELECT b.id, b.status, b.check_in, b.check_out, b.num_guests, b.total_amount, b.currency,
               h.name AS hotel_name, rt.name AS room_type_name
        FROM bookings b
        JOIN hotels h ON h.id = b.hotel_id
        JOIN room_types rt ON rt.id = b.room_type_id
        {where}
        ORDER BY b.created_at DESC
        LIMIT 100
    """), params).mappings().all()
    out = []
    for r in rows:
        rec = dict(r)
        for k in ("check_in","check_out"):
            rec[k] = rec[k].isoformat() if rec[k] else None
        out.append(rec)
    return jsonify(out)

@bp.post("/bookings")
@jwt_required()
def create_booking():
    data = request.get_json() or {}
    required = ("hotel_id","room_type_id","check_in","check_out","num_guests","total_amount","currency")
    for f in required:
        if data.get(f) in (None, ""):
            return jsonify({"error": f"Missing {f}"}), 400
    from datetime import datetime
    ci = datetime.fromisoformat(data["check_in"])
    co = datetime.fromisoformat(data["check_out"])
    if co <= ci:
        return jsonify({"error": "check_out must be after check_in"}), 400

    # Ensure availability
    overlap = db.session.execute(text("""
        SELECT 1 FROM bookings
        WHERE hotel_id=:hid AND room_type_id=:rtid AND status <> 'cancelled'
          AND check_in < :co AND check_out > :ci
        LIMIT 1
    """), {"hid": data["hotel_id"], "rtid": data["room_type_id"], "ci": ci, "co": co}).first()
    if overlap:
        return jsonify({"error": "Selected room type is not available for the given dates"}), 409

    uid = _uid()
    row = db.session.execute(text("""
        INSERT INTO bookings (booked_by_user_id, guest_user_id, guest_name, hotel_id, room_type_id,
                              check_in, check_out, status, num_guests, total_amount, currency)
        VALUES (:booked_by, :guest_user, :guest_name, :hid, :rtid, :ci, :co, 'confirmed', :guests, :total, :cur)
        RETURNING id
    """), {
        "booked_by": uid,
        "guest_user": uid,
        "guest_name": None,
        "hid": data["hotel_id"],
        "rtid": data["room_type_id"],
        "ci": ci, "co": co,
        "guests": int(data["num_guests"]),
        "total": float(data["total_amount"]),
        "cur": data.get("currency","USD")
    }).first()
    db.session.commit()
    return jsonify({"ok": True, "booking_id": row[0]})

@bp.patch("/bookings/<int:booking_id>/cancel")
@jwt_required()
def cancel_booking(booking_id: int):
    uid = _uid()
    # Allow cancel if owns booking or admin
    claims = get_jwt()
    is_admin = (claims or {}).get("role") == "admin"
    cond = "id=:id AND (booked_by_user_id=:uid OR guest_user_id=:uid)"
    params = {"id": booking_id, "uid": uid}
    if is_admin:
        cond = "id=:id"
        params = {"id": booking_id}
    row = db.session.execute(text(f"SELECT status FROM bookings WHERE {cond}"), params).first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    if row[0] == "cancelled":
        return jsonify({"ok": True, "already": True})
    db.session.execute(text("UPDATE bookings SET status='cancelled' WHERE id=:id"), {"id": booking_id})
    db.session.commit()
    return jsonify({"ok": True})
