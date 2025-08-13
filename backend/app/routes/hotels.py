from flask import Blueprint, jsonify, request
from sqlalchemy import text
from .. import db

bp = Blueprint("hotels", __name__)

def _map_hotel(row):
    rec = dict(row)
    # Attach primary image if available
    img = db.session.execute(text("""
        SELECT url, alt_text FROM hotel_images
        WHERE hotel_id=:hid
        ORDER BY CASE WHEN is_primary THEN 0 ELSE 1 END, id
        LIMIT 1
    """), {"hid": rec["id"]}).mappings().first()
    rec["primary_image"] = img["url"] if img else None
    return rec

@bp.get("/hotels")
def list_hotels():
    q = (request.args.get("q") or "").strip()
    city = (request.args.get("city") or "").strip()
    limit = int(request.args.get("limit") or 20)
    offset = int(request.args.get("offset") or 0)

    where = []
    params = {}
    if q:
        where.append("(LOWER(name) LIKE :q OR LOWER(city) LIKE :q)")
        params["q"] = f"%{q.lower()}%"
    if city:
        where.append("LOWER(city)=:city")
        params["city"] = city.lower()
    clause = "WHERE " + " AND ".join(where) if where else ""

    rows = db.session.execute(text(f"""
        SELECT id, name, city, country, address, description, amenities
        FROM hotels {clause}
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """), dict(params, limit=limit, offset=offset)).mappings().all()

    return jsonify([_map_hotel(r) for r in rows])

@bp.get("/hotels/<int:hotel_id>")
def hotel_detail(hotel_id: int):
    row = db.session.execute(text("""
        SELECT id, name, city, country, address, description, amenities
        FROM hotels WHERE id=:id
    """), {"id": hotel_id}).mappings().first()
    if not row:
        return jsonify({"error": "Not found"}), 404
    rec = dict(row)

    images = db.session.execute(text("""
        SELECT url, alt_text, is_primary FROM hotel_images
        WHERE hotel_id=:hid ORDER BY is_primary DESC, id
    """), {"hid": hotel_id}).mappings().all()
    rec["images"] = [dict(i) for i in images]

    room_types = db.session.execute(text("""
        SELECT id, name, capacity, base_price, description, amenities
        FROM room_types WHERE hotel_id=:hid AND active = TRUE
        ORDER BY base_price
    """), {"hid": hotel_id}).mappings().all()
    rec["room_types"] = [dict(r) for r in room_types]

    return jsonify(rec)

@bp.get("/hotels/<int:hotel_id>/availability")
def hotel_availability(hotel_id: int):
    from datetime import datetime
    tzaware = lambda s: datetime.fromisoformat(s)
    ci = request.args.get("check_in")
    co = request.args.get("check_out")
    guests = int(request.args.get("guests") or 1)
    if not (ci and co):
        return jsonify({"error": "check_in and check_out (ISO8601) are required"}), 400

    ci_dt = tzaware(ci)
    co_dt = tzaware(co)

    # Available room types = capacity ok AND no overlapping bookings in range
    rows = db.session.execute(text("""
        SELECT rt.id, rt.name, rt.capacity, rt.base_price, rt.description, rt.amenities
        FROM room_types rt
        WHERE rt.hotel_id = :hid
          AND rt.active = TRUE
          AND rt.capacity >= :guests
          AND NOT EXISTS (
                SELECT 1 FROM bookings b
                WHERE b.hotel_id = rt.hotel_id
                  AND b.room_type_id = rt.id
                  AND b.status <> 'cancelled'
                  AND b.check_in < :co AND b.check_out > :ci
          )
        ORDER BY rt.base_price
    """), {"hid": hotel_id, "guests": guests, "ci": ci_dt, "co": co_dt}).mappings().all()

    return jsonify([dict(r) for r in rows])
