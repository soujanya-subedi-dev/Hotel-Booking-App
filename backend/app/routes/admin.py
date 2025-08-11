# app/routes/admin.py
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt
from .. import db
from decimal import Decimal
from functools import wraps

bp = Blueprint("admin", __name__)

# ---- helpers -------------------------------------------------
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt() or {}
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper

def to_float(x):
    return float(x) if isinstance(x, Decimal) else x

def _page_params():
    try:
        page  = max(1, int(request.args.get("page", 1)))
    except Exception:
        page = 1
    try:
        limit = min(100, max(1, int(request.args.get("limit", 20))))
    except Exception:
        limit = 20
    return page, limit, (page - 1) * limit

# ---- Admin LISTS (for dashboards) ----------------------------

@bp.get("/admin/hotels")
@admin_required
def admin_list_hotels():
    q = (request.args.get("search") or "").strip()
    city = (request.args.get("city") or "").strip()
    page, limit, offset = _page_params()

    where = "WHERE 1=1"
    params = {}
    if q:
        where += " AND (h.name ILIKE :q OR h.city ILIKE :q)"
        params["q"] = f"%{q}%"
    if city:
        where += " AND h.city ILIKE :city"
        params["city"] = f"%{city}%"

    count = db.session.execute(text(f"SELECT COUNT(*) FROM hotels h {where}"), params).scalar_one()

    rows = db.session.execute(text(f"""
        SELECT h.id, h.name, h.city, h.country, h.address, h.description, h.star_rating,
               o.total_available_rooms, o.total_rooms, o.hotel_status,
               COALESCE(hi.url,'') AS primary_image
        FROM hotels h
        LEFT JOIN v_hotel_occupancy o ON o.hotel_id = h.id
        LEFT JOIN LATERAL (
            SELECT url FROM hotel_images WHERE hotel_id = h.id
            ORDER BY is_primary DESC, id DESC LIMIT 1
        ) hi ON TRUE
        {where}
        ORDER BY h.id DESC
        LIMIT :limit OFFSET :offset
    """), {**params, "limit": limit, "offset": offset}).mappings().all()

    return jsonify({
        "page": page, "limit": limit, "total": count,
        "items": [dict(r) for r in rows]
    })

@bp.get("/admin/hotels/<int:hid>")
@admin_required
def admin_get_hotel(hid: int):
    hotel = db.session.execute(text("""
        SELECT h.*, o.total_available_rooms, o.total_rooms, o.hotel_status
        FROM hotels h
        LEFT JOIN v_hotel_occupancy o ON o.hotel_id = h.id
        WHERE h.id=:id
    """), {"id": hid}).mappings().first()
    if not hotel: return jsonify({"error":"Not found"}), 404

    images = db.session.execute(text("""
        SELECT id, url, alt_text, is_primary
        FROM hotel_images WHERE hotel_id=:id ORDER BY is_primary DESC, id
    """), {"id": hid}).mappings().all()

    room_types = db.session.execute(text("""
        SELECT id, name, capacity, base_price, active
        FROM room_types WHERE hotel_id=:id ORDER BY id
    """), {"id": hid}).mappings().all()
    for rt in room_types: rt["base_price"] = to_float(rt["base_price"])

    rooms = db.session.execute(text("""
        SELECT r.id, r.room_type_id, r.room_number, r.status, r.active
        FROM rooms r WHERE r.hotel_id=:id ORDER BY r.id
    """), {"id": hid}).mappings().all()

    return jsonify({
        "hotel": dict(hotel),
        "images": [dict(x) for x in images],
        "room_types": [dict(x) for x in room_types],
        "rooms": [dict(x) for x in rooms],
    })

@bp.get("/admin/room-types")
@admin_required
def admin_list_room_types():
    page, limit, offset = _page_params()
    hid = request.args.get("hotel_id")
    where = "WHERE 1=1"; params = {}
    if hid:
        where += " AND rt.hotel_id=:hid"; params["hid"] = int(hid)
    count = db.session.execute(text(f"SELECT COUNT(*) FROM room_types rt {where}"), params).scalar_one()

    rows = db.session.execute(text(f"""
      SELECT rt.id, rt.hotel_id, h.name AS hotel_name, rt.name, rt.capacity, rt.base_price, rt.active
      FROM room_types rt
      JOIN hotels h ON h.id = rt.hotel_id
      {where}
      ORDER BY rt.id DESC
      LIMIT :limit OFFSET :offset
    """), {**params, "limit": limit, "offset": offset}).mappings().all()
    items = []
    for r in rows:
        d = dict(r)
        d["base_price"] = to_float(d["base_price"])
        items.append(d)
    return jsonify({"page": page, "limit": limit, "total": count, "items": items})

@bp.get("/admin/rooms")
@admin_required
def admin_list_rooms():
    page, limit, offset = _page_params()
    hid = request.args.get("hotel_id")
    rtid = request.args.get("room_type_id")
    where = "WHERE 1=1"; params = {}
    if hid:
        where += " AND r.hotel_id=:hid"; params["hid"] = int(hid)
    if rtid:
        where += " AND r.room_type_id=:rtid"; params["rtid"] = int(rtid)

    count = db.session.execute(text(f"SELECT COUNT(*) FROM rooms r {where}"), params).scalar_one()
    rows = db.session.execute(text(f"""
      SELECT r.id, r.hotel_id, h.name AS hotel_name,
             r.room_type_id, rt.name AS room_type_name,
             r.room_number, r.status, r.active
      FROM rooms r
      JOIN hotels h ON h.id = r.hotel_id
      JOIN room_types rt ON rt.id = r.room_type_id
      {where}
      ORDER BY r.id DESC
      LIMIT :limit OFFSET :offset
    """), {**params, "limit": limit, "offset": offset}).mappings().all()
    return jsonify({"page": page, "limit": limit, "total": count, "items": [dict(r) for r in rows]})

# ---- Hotels CRUD (existing) ---------------------------------

@bp.post("/admin/hotels")
@admin_required
def create_hotel():
    d = request.get_json() or {}
    req = ["name", "city", "country"]
    if any(k not in d or not d[k] for k in req):
        return jsonify({"error": f"Missing fields: {', '.join(req)}"}), 400

    row = db.session.execute(text("""
      INSERT INTO hotels (name, city, country, address, description, star_rating, amenities)
      VALUES (:name,:city,:country,:address,:description,:star_rating,:amenities)
      RETURNING id
    """), {
        "name": d["name"], "city": d["city"], "country": d["country"],
        "address": d.get("address"), "description": d.get("description"),
        "star_rating": d.get("star_rating"), "amenities": d.get("amenities") or {}
    }).first()
    db.session.commit()
    return jsonify({"id": row[0]}), 201

@bp.patch("/admin/hotels/<int:hid>")
@admin_required
def update_hotel(hid: int):
    d = request.get_json() or {}
    fields = ["name","city","country","address","description","star_rating","amenities"]
    sets = [f"{f} = :{f}" for f in fields if f in d]
    if not sets:
        return jsonify({"error": "Nothing to update"}), 400
    d["hid"] = hid
    db.session.execute(text(f"UPDATE hotels SET {', '.join(sets)} WHERE id=:hid"), d)
    db.session.commit()
    return jsonify({"ok": True})

@bp.delete("/admin/hotels/<int:hid>")
@admin_required
def delete_hotel(hid: int):
    try:
        db.session.execute(text("DELETE FROM hotels WHERE id=:id"), {"id": hid})
        db.session.commit()
        return jsonify({"ok": True})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Cannot delete (likely referenced by bookings).", "detail": str(e.orig)}), 400

# ---- Room Types CRUD (existing) ------------------------------

@bp.post("/admin/room-types")
@admin_required
def create_room_type():
    d = request.get_json() or {}
    req = ["hotel_id","name","capacity","base_price"]
    if any(k not in d for k in req):
        return jsonify({"error": f"Missing fields: {', '.join(req)}"}), 400

    row = db.session.execute(text("""
      INSERT INTO room_types (hotel_id, name, capacity, base_price, description, amenities, active)
      VALUES (:hotel_id,:name,:capacity,:base_price,:description,:amenities, COALESCE(:active,true))
      RETURNING id
    """), {
        "hotel_id": int(d["hotel_id"]),
        "name": d["name"],
        "capacity": int(d["capacity"]),
        "base_price": d["base_price"],
        "description": d.get("description"),
        "amenities": d.get("amenities") or {},
        "active": d.get("active")
    }).first()
    db.session.commit()
    return jsonify({"id": row[0]}), 201

@bp.patch("/admin/room-types/<int:rtid>")
@admin_required
def update_room_type(rtid: int):
    d = request.get_json() or {}
    fields = ["name","capacity","base_price","description","amenities","active"]
    sets = [f"{f} = :{f}" for f in fields if f in d]
    if not sets:
        return jsonify({"error":"Nothing to update"}), 400
    d["id"] = rtid
    db.session.execute(text(f"UPDATE room_types SET {', '.join(sets)} WHERE id=:id"), d)
    db.session.commit()
    return jsonify({"ok": True})

@bp.delete("/admin/room-types/<int:rtid>")
@admin_required
def delete_room_type(rtid: int):
    try:
        db.session.execute(text("DELETE FROM room_types WHERE id=:id"), {"id": rtid})
        db.session.commit()
        return jsonify({"ok": True})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error":"Cannot delete (referenced by rooms/bookings).","detail":str(e.orig)}), 400

# ---- Rooms CRUD (existing) ----------------------------------

@bp.post("/admin/rooms")
@admin_required
def create_room():
    d = request.get_json() or {}
    req = ["hotel_id","room_type_id","room_number"]
    if any(k not in d for k in req):
        return jsonify({"error": f"Missing fields: {', '.join(req)}"}), 400
    row = db.session.execute(text("""
      INSERT INTO rooms (hotel_id, room_type_id, room_number, status, active)
      VALUES (:hotel_id,:room_type_id,:room_number, COALESCE(:status,'available'), COALESCE(:active,true))
      RETURNING id
    """), {
        "hotel_id": int(d["hotel_id"]),
        "room_type_id": int(d["room_type_id"]),
        "room_number": str(d["room_number"]),
        "status": d.get("status"),
        "active": d.get("active")
    }).first()
    db.session.commit()
    return jsonify({"id": row[0]}), 201

@bp.patch("/admin/rooms/<int:rid>")
@admin_required
def update_room(rid: int):
    d = request.get_json() or {}
    fields = ["room_type_id","room_number","status","active"]
    sets = [f"{f} = :{f}" for f in fields if f in d]
    if not sets:
        return jsonify({"error":"Nothing to update"}), 400
    d["id"] = rid
    db.session.execute(text(f"UPDATE rooms SET {', '.join(sets)} WHERE id=:id"), d)
    db.session.commit()
    return jsonify({"ok": True})

@bp.delete("/admin/rooms/<int:rid>")
@admin_required
def delete_room(rid: int):
    try:
        db.session.execute(text("DELETE FROM rooms WHERE id=:id"), {"id": rid})
        db.session.commit()
        return jsonify({"ok": True})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error":"Cannot delete (referenced by bookings).","detail":str(e.orig)}), 400

# ---- Hotel IMAGES -------------------------------------------

@bp.post("/admin/hotels/<int:hid>/images")
@admin_required
def admin_add_hotel_image(hid: int):
    d = request.get_json() or {}
    if not d.get("url"):
        return jsonify({"error":"url is required"}), 400
    is_primary = bool(d.get("is_primary"))
    if is_primary:
        db.session.execute(text("UPDATE hotel_images SET is_primary=false WHERE hotel_id=:hid"), {"hid": hid})
    row = db.session.execute(text("""
      INSERT INTO hotel_images (hotel_id, url, alt_text, is_primary)
      VALUES (:hid, :url, :alt_text, :is_primary) RETURNING id
    """), {"hid": hid, "url": d["url"], "alt_text": d.get("alt_text"), "is_primary": is_primary}).first()
    db.session.commit()
    return jsonify({"id": row[0]}), 201

@bp.patch("/admin/hotel-images/<int:image_id>")
@admin_required
def admin_update_hotel_image(image_id: int):
    d = request.get_json() or {}
    # find hotel_id for primary handling
    row = db.session.execute(text("SELECT hotel_id FROM hotel_images WHERE id=:id"), {"id": image_id}).first()
    if not row: return jsonify({"error":"Not found"}), 404
    hid = row[0]

    sets = []; params = {"id": image_id}
    if "url" in d:       sets.append("url=:url");           params["url"] = d["url"]
    if "alt_text" in d:  sets.append("alt_text=:alt_text"); params["alt_text"] = d.get("alt_text")
    if "is_primary" in d:
        is_primary = bool(d["is_primary"])
        if is_primary:
            db.session.execute(text("UPDATE hotel_images SET is_primary=false WHERE hotel_id=:hid"), {"hid": hid})
        sets.append("is_primary=:is_primary"); params["is_primary"] = is_primary

    if not sets: return jsonify({"error":"Nothing to update"}), 400
    db.session.execute(text(f"UPDATE hotel_images SET {', '.join(sets)} WHERE id=:id"), params)
    db.session.commit()
    return jsonify({"ok": True})

@bp.delete("/admin/hotel-images/<int:image_id>")
@admin_required
def admin_delete_hotel_image(image_id: int):
    db.session.execute(text("DELETE FROM hotel_images WHERE id=:id"), {"id": image_id})
    db.session.commit()
    return jsonify({"ok": True})

# ---- Reports (existing) -------------------------------------

@bp.get("/admin/reports/user/<int:user_id>/bookings")
@admin_required
def report_user_bookings(user_id: int):
    rows = db.session.execute(text("""
      SELECT b.id, b.hotel_id, h.name AS hotel_name, b.room_type_id, rt.name AS room_type_name,
             b.check_in, b.check_out, b.status, b.total_amount, b.currency
      FROM bookings b
      JOIN hotels h ON h.id=b.hotel_id
      JOIN room_types rt ON rt.id=b.room_type_id
      WHERE b.status <> 'cancelled' AND (b.guest_user_id=:uid OR b.booked_by_user_id=:uid)
      ORDER BY b.check_in DESC, b.id DESC
    """), {"uid": user_id}).mappings().all()
    return jsonify([{
        "id": r["id"],
        "hotel": {"id": r["hotel_id"], "name": r["hotel_name"]},
        "room_type": {"id": r["room_type_id"], "name": r["room_type_name"]},
        "check_in": r["check_in"].isoformat(),
        "check_out": r["check_out"].isoformat(),
        "status": r["status"],
        "total_amount": to_float(r["total_amount"]),
        "currency": r["currency"],
    } for r in rows])

@bp.get("/admin/reports/hotel/<int:hotel_id>/user-bookings")
@admin_required
def report_hotel_user_counts(hotel_id: int):
    rows = db.session.execute(text("""
      SELECT u.id as user_id, COALESCE(u.full_name, 'Guest') AS user_name, COUNT(*) AS bookings
      FROM bookings b
      LEFT JOIN users u ON u.id = b.guest_user_id
      WHERE b.hotel_id = :hid AND b.status <> 'cancelled'
      GROUP BY u.id, u.full_name
      ORDER BY bookings DESC
    """), {"hid": hotel_id}).mappings().all()
    return jsonify(rows)

@bp.get("/admin/reports/hotel/<int:hotel_id>/occupancy")
@admin_required
def report_hotel_occupancy(hotel_id: int):
    row = db.session.execute(text("SELECT * FROM v_hotel_occupancy WHERE hotel_id = :hid"), {"hid": hotel_id}).mappings().first()
    return jsonify(row or {})
