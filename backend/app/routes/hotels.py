# app/routes/hotels.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date, time, timezone
from sqlalchemy import text
from .. import db

bp = Blueprint("hotels", __name__)

# ---------- helpers ----------
def _parse_dt(value: str):
    """
    Accepts 'YYYY-MM-DD' or ISO8601 datetime. Returns timezone-aware UTC datetime.
    """
    if not value:
        return None
    try:
        # date-only
        if len(value) == 10 and value[4] == "-" and value[7] == "-":
            d = date.fromisoformat(value)
            # pick a neutral time so '[)' ranges behave consistently
            return datetime.combine(d, time(15, 0, tzinfo=timezone.utc))
        # datetime
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


# ---------- routes ----------

@bp.get("/hotels")
def list_hotels():
    """
    Returns hotels with occupancy summary and a primary image (if any).
    Optional filters: ?q=search&city=City
    """
    q = (request.args.get("q") or "").strip()
    city = (request.args.get("city") or "").strip()

    sql = text("""
        SELECT h.id, h.name, h.city, h.country, h.star_rating,
               COALESCE(hi.url, '') AS primary_image,
               o.total_available_rooms, o.total_rooms, o.hotel_status
        FROM hotels h
        LEFT JOIN LATERAL (
            SELECT url FROM hotel_images
            WHERE hotel_id = h.id
            ORDER BY is_primary DESC, id DESC
            LIMIT 1
        ) hi ON TRUE
        LEFT JOIN v_hotel_occupancy o ON o.hotel_id = h.id
        WHERE (:q = '' OR h.name ILIKE :qq OR h.city ILIKE :qq)
          AND (:city = '' OR h.city ILIKE :cityq)
        ORDER BY h.id ASC;
    """)

    rows = db.session.execute(sql, {
        "q": q, "qq": f"%{q}%",
        "city": city, "cityq": f"%{city}%"
    }).mappings().all()

    # Include up to 3 sample room types per hotel for homepage cards
    hotel_ids = [r["id"] for r in rows]
    rtypes_by_hotel = {}

    if hotel_ids:
        rtypes = db.session.execute(text("""
            SELECT rt.id, rt.hotel_id, rt.name, rt.capacity, rt.base_price
            FROM room_types rt
            WHERE rt.active = TRUE
              AND rt.hotel_id = ANY(:ids)
            ORDER BY rt.hotel_id, rt.base_price ASC, rt.id
        """), {"ids": hotel_ids}).mappings().all()

        for rt in rtypes:
            rtypes_by_hotel.setdefault(rt["hotel_id"], []).append({
                "id": rt["id"],
                "hotel_id": rt["hotel_id"],
                "name": rt["name"],
                "capacity": rt["capacity"],
                "base_price": float(rt["base_price"]),  # Decimal -> float for JSON
            })

    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "city": r["city"],
            "country": r["country"],
            "star_rating": r["star_rating"],
            "primary_image": r["primary_image"],
            "occupancy": {
                "total_available_rooms": r["total_available_rooms"] or 0,
                "total_rooms": r["total_rooms"] or 0,
                "hotel_status": r["hotel_status"] or "Available",
            },
            "sample_room_types": (rtypes_by_hotel.get(r["id"], [])[:3])
        })

    return jsonify(out)


@bp.get("/hotels/<int:hotel_id>")
def hotel_detail(hotel_id: int):
    """
    Detailed hotel info with images and room types.
    Optionally pass ?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD to include availability counts.
    """
    # core hotel
    hotel = db.session.execute(text("""
        SELECT h.id, h.name, h.city, h.country, h.address, h.description, h.star_rating,
               o.total_available_rooms, o.total_rooms, o.hotel_status
        FROM hotels h
        LEFT JOIN v_hotel_occupancy o ON o.hotel_id = h.id
        WHERE h.id = :hid
    """), {"hid": hotel_id}).mappings().first()
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    # images (coerce to plain dicts)
    images_rows = db.session.execute(text("""
        SELECT id, url, alt_text, is_primary
        FROM hotel_images WHERE hotel_id = :hid
        ORDER BY is_primary DESC, id
    """), {"hid": hotel_id}).mappings().all()
    images = [dict(x) for x in images_rows]

    # room types (coerce Decimal -> float)
    room_types_rows = db.session.execute(text("""
        SELECT id, name, capacity, base_price, description, amenities
        FROM room_types
        WHERE hotel_id = :hid AND active = TRUE
        ORDER BY base_price ASC, id
    """), {"hid": hotel_id}).mappings().all()

    room_types = [{
        "id": rt["id"],
        "name": rt["name"],
        "capacity": rt["capacity"],
        "base_price": float(rt["base_price"]),
        "description": rt["description"],
        "amenities": rt["amenities"],
    } for rt in room_types_rows]

    # optional availability
    cin = _parse_dt(request.args.get("check_in", ""))
    cout = _parse_dt(request.args.get("check_out", ""))
    availability = {}
    if cin and cout and cin < cout:
        for rt in room_types:
            count = db.session.execute(text("""
                SELECT COUNT(*)::int
                FROM rooms r
                WHERE r.hotel_id = :hid
                  AND r.room_type_id = :rtid
                  AND r.active = TRUE AND r.status = 'available'
                  AND NOT EXISTS (
                      SELECT 1 FROM bookings b
                      WHERE b.room_id = r.id
                        AND b.status IN ('pending','confirmed','checked_in')
                        AND tstzrange(b.check_in,b.check_out,'[)') && tstzrange(:cin,:cout,'[)')
                  );
            """), {"hid": hotel_id, "rtid": rt["id"], "cin": cin, "cout": cout}).scalar_one()
            availability[str(rt["id"])] = {"available_count": count, "any_available": count > 0}

    return jsonify({
        "hotel": {
            "id": hotel["id"],
            "name": hotel["name"],
            "city": hotel["city"],
            "country": hotel["country"],
            "address": hotel["address"],
            "description": hotel["description"],
            "star_rating": hotel["star_rating"],
            "occupancy": {
                "total_available_rooms": hotel["total_available_rooms"] or 0,
                "total_rooms": hotel["total_rooms"] or 0,
                "hotel_status": hotel["hotel_status"] or "Available",
            },
            "images": images,
        },
        "room_types": room_types,
        "availability": availability,  # empty if dates not provided/invalid
    })


@bp.get("/availability")
def availability():
    """
    Quick availability check for a room_type in a hotel.
    Params: hotel_id, room_type_id, check_in, check_out (YYYY-MM-DD or ISO)
    """
    try:
        hotel_id = int(request.args.get("hotel_id", "0"))
        room_type_id = int(request.args.get("room_type_id", "0"))
    except ValueError:
        return jsonify({"error": "hotel_id and room_type_id must be integers"}), 400

    cin = _parse_dt(request.args.get("check_in", ""))
    cout = _parse_dt(request.args.get("check_out", ""))

    if not (hotel_id and room_type_id and cin and cout and cin < cout):
        return jsonify({"error": "Invalid params. Provide hotel_id, room_type_id, check_in, check_out."}), 400

    count = db.session.execute(text("""
        SELECT COUNT(*)::int
        FROM rooms r
        WHERE r.hotel_id = :hid
          AND r.room_type_id = :rtid
          AND r.active = TRUE AND r.status = 'available'
          AND NOT EXISTS (
              SELECT 1 FROM bookings b
              WHERE b.room_id = r.id
                AND b.status IN ('pending','confirmed','checked_in')
                AND tstzrange(b.check_in,b.check_out,'[)') && tstzrange(:cin,:cout,'[)')
          );
    """), {"hid": hotel_id, "rtid": room_type_id, "cin": cin, "cout": cout}).scalar_one()

    return jsonify({"available_count": count, "any_available": count > 0})
