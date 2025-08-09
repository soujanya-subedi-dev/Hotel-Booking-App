import os
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Ensure an admin/user exist
    if not db.session.execute(db.select(User).filter_by(email='admin@example.com')).scalar():
        from werkzeug.security import generate_password_hash
        admin = User(full_name='Admin', email='admin@example.com',
                     role='admin', password_hash=generate_password_hash('admin123'))
        user = User(full_name='Test User', email='user@example.com',
                    role='user', password_hash=generate_password_hash('user123'))
        db.session.add_all([admin, user])
        db.session.commit()
        print("Seeded users.")

    # Seed hotels/room_types/rooms via raw SQL for brevity
    db.session.execute(text("""
        INSERT INTO hotels (name, city, country, address, description, amenities)
        VALUES ('Everest View Hotel', 'Kathmandu', 'Nepal', 'Thamel, KTM', 'Central boutique hotel', '{"wifi": true}')
        RETURNING id;
    """))
    hotel_id = db.session.execute(text("SELECT id FROM hotels ORDER BY id DESC LIMIT 1;")).scalar()

    db.session.execute(text(f"""
        INSERT INTO room_types (hotel_id, name, capacity, base_price, description, amenities)
        VALUES ({hotel_id}, 'Deluxe King', 2, 120.00, 'Spacious king room', '{{"ac": true, "tv": true}}'),
               ({hotel_id}, 'Twin Standard', 2, 80.00, 'Two single beds', '{{"ac": true}}')
        RETURNING id;
    """))

    rt_ids = [r[0] for r in db.session.execute(text("SELECT id FROM room_types WHERE hotel_id=:hid"), {'hid': hotel_id}).fetchall()]

    # Add a few rooms
    db.session.execute(text("""
        INSERT INTO rooms (hotel_id, room_type_id, room_number) VALUES
        (:hid, :rt1, '101'), (:hid, :rt1, '102'), (:hid, :rt2, '201');
    """), {'hid': hotel_id, 'rt1': rt_ids[0], 'rt2': rt_ids[1]})

    db.session.commit()
    print("Seeded hotel, room types, rooms.")

    # Try a booking via stored proc
    now = datetime.now(timezone.utc)
    check_in = now + timedelta(days=3)
    check_out = now + timedelta(days=5)
    # booked_by = admin(1), guest_user = user(2) depending on your ids
    uid_admin = db.session.execute(text("SELECT id FROM users WHERE email='admin@example.com'")).scalar()
    uid_user = db.session.execute(text("SELECT id FROM users WHERE email='user@example.com'")).scalar()
    rt = db.session.execute(text("SELECT id, hotel_id FROM room_types LIMIT 1")).first()
    hotel_id = rt[1]
    rt_id = rt[0]

    bid = db.session.execute(text("""
        SELECT sp_create_booking(:booked_by, :guest_user, :guest_name, :hotel, :room_type, :cin, :cout, :guests, :total, :cur);
    """), {
        'booked_by': uid_admin,
        'guest_user': uid_user,
        'guest_name': None,
        'hotel': hotel_id,
        'room_type': rt_id,
        'cin': check_in, 'cout': check_out,
        'guests': 2,
        'total': 240.00,
        'cur': 'USD'
    }).scalar()

    db.session.commit()
    print("Created booking id:", bid)
