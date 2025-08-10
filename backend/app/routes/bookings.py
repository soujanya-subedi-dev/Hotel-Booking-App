# app/routes/bookings.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date, time, timezone
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .. import db

bp = Blueprint("bookings", __name__)

# --- helpers ---
def _parse_dt(d: str):
    if not d: return None
    try:
        if len(d) == 10 and d[4] == "-" and d[7] == "-":
            return datetime.combine(date.fromisoformat(d), time(15, 0, tzinfo=timezone.utc))
        dt = datetime.fromisoformat(d)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None

def _me():
    uid = get_jwt_identity()          # string
    claims = get_jwt()                # has role/email
    return int(uid), claims.get("role", "user")

def _is_admin(role): return role == "admin"

# --- ROUTES ---

@bp.get("/bookings")
@jwt_required()
def list_bookings():
    """User: own bookings; Admin: all (filters: user_id, hotel_id, status, from, to)"""
    me_id, role = _me()
    user_id = request.args.get("user_id")
    hotel_id = request.args.get("hotel_id")
    status = request.args.get("status")
    dfrom = _parse_dt(request.args.get("from", ""))
    dto   = _parse_dt(request.args.get("to", ""))

    sql = """
      SELECT b.id, b.booked_by_user_id, b.guest_user_id, b.guest_name,
             b.hotel_id, h.name AS hotel_name,
             b.room_type_id, rt.name AS room_type_name,
             b.room_id, b.check_in, b.check_out, b.status,
             b.num_guests, b.total_amount, b.currency, b.created_at, b.updated_at
      FROM bookings b
      JOIN hotels h ON h.id = b.hotel_id
      JOIN room_types rt ON rt.id = b.room_type_id
      WHERE 1=1
    """
    params = {}

    if not _is_admin(role):
        sql += " AND (b.guest_user_id = :me OR b.booked_by_user_id = :me)"
        params["me"] = me_id
    else:
        if user_id:
            sql += " AND (b.guest_user_id = :uid OR b.booked_by_user_id = :uid)"
            params["uid"] = int(user_id)

    if hotel_id:
        sql += " AND b.hotel_id = :hid"; params["hid"] = int(hotel_id)
    if status:
        sql += " AND b.status = :st"; params["st"] = status
    if dfrom:
        sql += " AND b.check_in >= :dfrom"; params["dfrom"] = dfrom
    if dto:
        sql += " AND b.check_out <= :dto"; params["dto"] = dto

    sql += " ORDER BY b.check_in DESC, b.id DESC"

    rows = db.session.execute(text(sql), params).mappings().all()
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "booked_by_user_id": r["booked_by_user_id"],
            "guest_user_id": r["guest_user_id"],
            "guest_name": r["guest_name"],
            "hotel": {"id": r["hotel_id"], "name": r["hotel_name"]},
            "room_type": {"id": r["room_type_id"], "name": r["room_type_name"]},
            "room_id": r["room_id"],
            "check_in": r["check_in"].isoformat(),
            "check_out": r["check_out"].isoformat(),
            "status": r["status"],
            "num_guests": r["num_guests"],
            "total_amount": float(r["total_amount"]),
            "currency": r["currency"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
        })
    return jsonify(out)


@bp.get("/bookings/<int:booking_id>")
@jwt_required()
def get_booking(booking_id: int):
    me_id, role = _me()
    row = db.session.execute(text("""
      SELECT b.*, h.name AS hotel_name, rt.name AS room_type_name
      FROM bookings b
      JOIN hotels h ON h.id = b.hotel_id
      JOIN room_types rt ON rt.id = b.room_type_id
      WHERE b.id = :id
    """), {"id": booking_id}).mappings().first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    if not _is_admin(role) and me_id not in (row["guest_user_id"], row["booked_by_user_id"]):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({
        "id": row["id"],
        "hotel": {"id": row["hotel_id"], "name": row["hotel_name"]},
        "room_type": {"id": row["room_type_id"], "name": row["room_type_name"]},
        "room_id": row["room_id"],
        "check_in": row["check_in"].isoformat(),
        "check_out": row["check_out"].isoformat(),
        "status": row["status"],
        "num_guests": row["num_guests"],
        "total_amount": float(row["total_amount"]),
        "currency": row["currency"],
        "guest_user_id": row["guest_user_id"],
        "guest_name": row["guest_name"],
        "booked_by_user_id": row["booked_by_user_id"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    })


@bp.post("/bookings")
@jwt_required()
def create_booking():
    """User: book for self. Admin: can book for user or guest_name."""
    me_id, role = _me()
    data = request.get_json() or {}

    try:
        hotel_id     = int(data.get("hotel_id"))
        room_type_id = int(data.get("room_type_id"))
        num_guests   = int(data.get("num_guests", 1))
        total_amount = float(data.get("total_amount", 0))
        currency     = (data.get("currency") or "USD")[:8]
    except Exception:
        return jsonify({"error": "Invalid numeric fields"}), 400

    check_in  = _parse_dt(data.get("check_in", ""))
    check_out = _parse_dt(data.get("check_out", ""))
    if not (hotel_id and room_type_id and check_in and check_out and check_in < check_out):
        return jsonify({"error": "Required: hotel_id, room_type_id, check_in, check_out"}), 400

    # who is the guest?
    if _is_admin(role):
        guest_user_id = data.get("guest_user_id")
        guest_name = (data.get("guest_name") or None)
        if guest_user_id:
            try: guest_user_id = int(guest_user_id)
            except ValueError: return jsonify({"error": "guest_user_id must be integer"}), 400
    else:
        guest_user_id = me_id
        guest_name = None

    try:
        booking_id = db.session.execute(text("""
          SELECT sp_create_booking(
            :booked_by, :guest_user, :guest_name,
            :hotel, :room_type, :cin, :cout,
            :guests, :total, :cur
          );
        """), {
            "booked_by": me_id,
            "guest_user": guest_user_id,
            "guest_name": guest_name,
            "hotel": hotel_id,
            "room_type": room_type_id,
            "cin": check_in, "cout": check_out,
            "guests": num_guests,
            "total": total_amount,
            "cur": currency
        }).scalar_one()
        db.session.commit()
        return jsonify({"id": booking_id}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Conflict creating booking", "detail": str(e.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create booking", "detail": str(e)}), 400


@bp.patch("/bookings/<int:booking_id>")
@jwt_required()
def update_booking(booking_id: int):
    """Edit dates/guests. Finds an available room; respects ACL."""
    me_id, role = _me()
    data = request.get_json() or {}

    # Load existing for ACL + context
    row = db.session.execute(text("SELECT * FROM bookings WHERE id=:id"), {"id": booking_id}).mappings().first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    if not _is_admin(role) and me_id not in (row["guest_user_id"], row["booked_by_user_id"]):
        return jsonify({"error": "Forbidden"}), 403
    if row["status"] not in ("pending", "confirmed"):
        return jsonify({"error": "Only pending/confirmed bookings can be edited"}), 400

    check_in  = _parse_dt(data.get("check_in", "")) or row["check_in"]
    check_out = _parse_dt(data.get("check_out", "")) or row["check_out"]
    if check_in >= check_out:
        return jsonify({"error": "Invalid dates"}), 400
    num_guests = int(data.get("num_guests", row["num_guests"]))

    try:
        # Find a free room for new window (same hotel/room_type)
        v_room = db.session.execute(text("""
          SELECT fn_find_available_room(:hid, :rtid, :cin, :cout);
        """), {"hid": row["hotel_id"], "rtid": row["room_type_id"], "cin": check_in, "cout": check_out}).scalar_one()

        if v_room is None:
            return jsonify({"error": "No rooms available for the new dates"}), 409

        db.session.execute(text("""
          UPDATE bookings
          SET check_in=:cin, check_out=:cout, room_id=:rid, num_guests=:gu
          WHERE id=:id
        """), {"cin": check_in, "cout": check_out, "rid": v_room, "gu": num_guests, "id": booking_id})
        db.session.commit()
        return jsonify({"ok": True})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Conflict updating booking", "detail": str(e.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update booking", "detail": str(e)}), 400


@bp.delete("/bookings/<int:booking_id>")
@jwt_required()
def cancel_booking(booking_id: int):
    """Soft-cancel (status='cancelled')."""
    me_id, role = _me()
    row = db.session.execute(text("SELECT * FROM bookings WHERE id=:id"), {"id": booking_id}).mappings().first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    if not _is_admin(role) and me_id not in (row["guest_user_id"], row["booked_by_user_id"]):
        return jsonify({"error": "Forbidden"}), 403
    if row["status"] == "cancelled":
        return jsonify({"ok": True})  # already cancelled

    if not _is_admin(role) and datetime.now(timezone.utc) >= row["check_in"]:
        return jsonify({"error": "Cannot cancel after check-in time"}), 400

    db.session.execute(text("UPDATE bookings SET status='cancelled' WHERE id=:id"), {"id": booking_id})
    db.session.commit()
    return jsonify({"ok": True})
