import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

# Hotels and images (Wikimedia/official gallery URLs)
HOTELS = [
    {
        "name": "Hyatt Regency Kathmandu",
        "city": "Kathmandu",
        "country": "Nepal",
        "address": "Boudha, Kathmandu",
        "description": "Upscale hotel near Boudhanath Stupa with spacious rooms and pool.",
        "amenities": {"wifi": True, "pool": True, "spa": True},
        "images": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/6/6d/Hyatt_Regency_Kathmandu_Hotel.jpg",
                "alt": "Hyatt Regency Kathmandu exterior (Wikimedia)",
                "primary": True,
            }
        ],
    },
    {
        "name": "Aloft Kathmandu Thamel",
        "city": "Kathmandu",
        "country": "Nepal",
        "address": "Chhaya Devi Complex, Thamel",
        "description": "Modern lifestyle hotel in Thamel, close to dining and nightlife.",
        "amenities": {"wifi": True, "gym": True, "rooftop": True},
        "images": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Thamel_Kathmandu_Nepal.jpg",
                "alt": "Thamel street scene near Aloft (Wikimedia)",
                "primary": True,
            }
        ],
    },
    {
        "name": "Temple Tree Resort & Spa",
        "city": "Pokhara",
        "country": "Nepal",
        "address": "Lakeside, Pokhara",
        "description": "Boutique resort near Phewa Lake with garden courtyards and spa.",
        "amenities": {"wifi": True, "spa": True},
        "images": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Phewa_Lake_of_Pokhara_city.jpg",
                "alt": "Phewa Lake, Pokhara (Wikimedia)",
                "primary": True,
            }
        ],
    },
    {
        "name": "Green Park Chitwan",
        "city": "Chitwan",
        "country": "Nepal",
        "address": "Sauraha, Chitwan",
        "description": "Jungle resort near Chitwan National Park with safari activities.",
        "amenities": {"wifi": True, "pool": True},
        "images": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Chitwan_National_Park_%282010%29-21.jpg",
                "alt": "Chitwan National Park, Rapti River (Wikimedia)",
                "primary": True,
            }
        ],
    },
    {
        "name": "Barahi Jungle Lodge",
        "city": "Chitwan",
        "country": "Nepal",
        "address": "Meghauli, Chitwan",
        "description": "Luxury riverside lodge offering wildlife experiences and nature views.",
        "amenities": {"wifi": True, "pool": True, "safari": True},
        "images": [
            {
                "url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Chitwan_National_Park_%282010%29-21.jpg",
                "alt": "Chitwan National Park (near Meghauli) (Wikimedia)",
                "primary": True,
            }
        ],
    },
]

ROOM_TYPES = [
    ("Deluxe King", 2, 120.00, "Spacious king room", {"ac": True, "tv": True}),
    ("Twin Standard", 3, 80.00, "Two single beds", {"ac": True})
]

def upsert_user(full_name, email, role, password):
    exists = db.session.execute(db.select(User).filter_by(email=email)).scalar()
    if exists:
        return exists.id
    u = User(
        full_name=full_name,
        email=email,
        role=role,
        password_hash=generate_password_hash(password),
    )
    db.session.add(u)
    db.session.commit()
    return u.id

def get_or_create_hotel(h):
    hid = db.session.execute(text("SELECT id FROM hotels WHERE name=:name"), {"name": h["name"]}).scalar()
    if hid:
        return hid
    row = db.session.execute(text("""
        INSERT INTO hotels (name, city, country, address, description, amenities)
        VALUES (:name, :city, :country, :address, :description, CAST(:amenities AS jsonb))
        RETURNING id
    """), {
        "name": h["name"],
        "city": h["city"],
        "country": h["country"],
        "address": h["address"],
        "description": h["description"],
        "amenities": json.dumps(h["amenities"]),
    }).first()
    db.session.commit()
    return row[0]

def ensure_hotel_image(hotel_id, url, alt, primary=False):
    row = db.session.execute(text("""
        SELECT id FROM hotel_images WHERE hotel_id=:hid AND url=:url
    """), {"hid": hotel_id, "url": url}).first()
    if row:
        return row[0]
    row = db.session.execute(text("""
        INSERT INTO hotel_images (hotel_id, url, alt_text, is_primary)
        VALUES (:hid, :url, :alt, :primary)
        RETURNING id
    """), {"hid": hotel_id, "url": url, "alt": alt, "primary": bool(primary)}).first()
    db.session.commit()
    return row[0]

def get_or_create_room_type(hotel_id, rt):
    rtid = db.session.execute(text("""
        SELECT id FROM room_types WHERE hotel_id=:hid AND name=:name
    """), {"hid": hotel_id, "name": rt[0]}).scalar()
    if rtid:
        return rtid
    row = db.session.execute(text("""
        INSERT INTO room_types (hotel_id, name, capacity, base_price, description, amenities, active)
        VALUES (:hid, :name, :capacity, :price, :desc, CAST(:amenities AS jsonb), TRUE)
        RETURNING id
    """), {
        "hid": hotel_id,
        "name": rt[0],
        "capacity": rt[1],
        "price": rt[2],
        "desc": rt[3],
        "amenities": json.dumps(rt[4]),
    }).first()
    db.session.commit()
    return row[0]

def ensure_room(hotel_id, room_type_id, room_number):
    rid = db.session.execute(text("""
        SELECT id FROM rooms WHERE hotel_id=:hid AND room_type_id=:rtid AND room_number=:num
    """), {"hid": hotel_id, "rtid": room_type_id, "num": str(room_number)}).scalar()
    if rid:
        return rid
    row = db.session.execute(text("""
        INSERT INTO rooms (hotel_id, room_type_id, room_number, status, active)
        VALUES (:hid, :rtid, :num, 'available', TRUE)
        RETURNING id
    """), {"hid": hotel_id, "rtid": room_type_id, "num": str(room_number)}).first()
    db.session.commit()
    return row[0]

with app.app_context():
    # 1) Users
    admin_id = upsert_user("Admin", "admin@example.com", "admin", "admin123")
    user_id  = upsert_user("Test User", "user@example.com", "user", "user123")
    print("Users ready. (admin and user)")

    # 2) Hotels, images, room types, rooms
    hotel_ids = []
    for h in HOTELS:
        hid = get_or_create_hotel(h)
        hotel_ids.append(hid)

        # images
        for idx, img in enumerate(h.get("images", [])):
            ensure_hotel_image(hid, img["url"], img.get("alt") or "", primary=bool(img.get("primary") and idx == 0))

        # two room types
        rt_ids = [get_or_create_room_type(hid, rt) for rt in ROOM_TYPES]

        # rooms: 2 for Deluxe, 1 for Twin
        if len(rt_ids) >= 2:
            ensure_room(hid, rt_ids[0], "101")
            ensure_room(hid, rt_ids[0], "102")
            ensure_room(hid, rt_ids[1], "201")

    print(f"Seeded {len(hotel_ids)} hotels with images, room types & rooms.")

    # 3) Sample booking (hotel 1, Deluxe if exists)
    if hotel_ids:
        rt_row = db.session.execute(text("""
            SELECT id FROM room_types
            WHERE hotel_id=:hid AND name='Deluxe King' ORDER BY id LIMIT 1
        """), {"hid": hotel_ids[0]}).first()

        if rt_row:
            now = datetime.now(timezone.utc)
            check_in = now + timedelta(days=7)
            check_out = now + timedelta(days=9)

            bid = db.session.execute(text("""
                INSERT INTO bookings (booked_by_user_id, guest_user_id, guest_name, hotel_id, room_type_id,
                                      check_in, check_out, status, num_guests, total_amount, currency)
                VALUES (:booked_by, :guest_user, :guest_name, :hotel, :room_type, :cin, :cout,
                        'confirmed', :guests, :total, :cur)
                RETURNING id
            """), {
                "booked_by": admin_id,
                "guest_user": user_id,
                "guest_name": None,
                "hotel": hotel_ids[0],
                "room_type": rt_row[0],
                "cin": check_in, "cout": check_out,
                "guests": 2,
                "total": 240.00,
                "cur": "USD"
            }).scalar()
            db.session.commit()
            print("Created booking id:", bid)
        else:
            print("Skipped sample booking (no Deluxe room type found).")
