from . import db
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # use CITEXT in DB layer if available
    phone = db.Column(db.Text)
    role = db.Column(db.String(10), nullable=False, default="user")  # 'user' | 'admin'
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Hotel(db.Model):
    __tablename__ = "hotels"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    amenities = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class HotelImage(db.Model):
    __tablename__ = "hotel_images"
    id = db.Column(db.BigInteger, primary_key=True)
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    url = db.Column(db.Text, nullable=False)
    alt_text = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))

class RoomType(db.Model):
    __tablename__ = "room_types"
    id = db.Column(db.BigInteger, primary_key=True)
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Numeric(12,2), nullable=False)
    description = db.Column(db.Text)
    amenities = db.Column(db.JSON, nullable=False, default=dict)
    active = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.BigInteger, primary_key=True)
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    room_type_id = db.Column(db.BigInteger, db.ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False)
    room_number = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, server_default=db.text("'available'"))
    active = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.BigInteger, primary_key=True)
    booked_by_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    guest_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"))
    guest_name = db.Column(db.Text)
    hotel_id = db.Column(db.BigInteger, db.ForeignKey("hotels.id", ondelete="RESTRICT"), nullable=False)
    room_type_id = db.Column(db.BigInteger, db.ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False)
    check_in = db.Column(db.DateTime(timezone=True), nullable=False)
    check_out = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.Text, nullable=False, server_default=db.text("'pending'"))  # pending|confirmed|cancelled
    num_guests = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(12,2), nullable=False)
    currency = db.Column(db.Text, nullable=False, server_default=db.text("'USD'"))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BookingStatusLog(db.Model):
    __tablename__ = "booking_status_log"
    id = db.Column(db.BigInteger, primary_key=True)
    booking_id = db.Column(db.BigInteger, db.ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    changed_by_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    from_status = db.Column(db.Text)
    to_status = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)
    changed_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
