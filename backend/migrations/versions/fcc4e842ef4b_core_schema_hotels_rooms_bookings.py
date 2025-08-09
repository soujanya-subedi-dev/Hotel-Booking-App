# migrations/versions/0002_core_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '0002_core_schema'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade():
    # ---- Hotels ----
    op.create_table(
        'hotels',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('city', sa.Text, nullable=False),
        sa.Column('country', sa.Text, nullable=False),
        sa.Column('address', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('star_rating', sa.Integer, sa.CheckConstraint('star_rating BETWEEN 1 AND 5'), nullable=True),
        sa.Column('amenities', postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'hotel_images',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('hotel_id', sa.BigInteger, sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.Text, nullable=False),
        sa.Column('alt_text', sa.Text),
        sa.Column('is_primary', sa.Boolean, server_default=sa.text('false'), nullable=False),
    )

    # ---- Room Types ----
    op.create_table(
        'room_types',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('hotel_id', sa.BigInteger, sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('capacity', sa.Integer, sa.CheckConstraint('capacity > 0'), nullable=False),
        sa.Column('base_price', sa.Numeric(12, 2), sa.CheckConstraint('base_price >= 0'), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('amenities', postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('active', sa.Boolean, server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # ---- Rooms ----
    op.create_table(
        'rooms',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('hotel_id', sa.BigInteger, sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('room_type_id', sa.BigInteger, sa.ForeignKey('room_types.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('room_number', sa.Text, nullable=False),
        sa.Column('status', sa.Text, sa.CheckConstraint("status IN ('available','maintenance','inactive')"),
                  server_default=sa.text("'available'"), nullable=False),
        sa.Column('active', sa.Boolean, server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('hotel_id', 'room_number', name='uq_room_per_hotel_number')
    )

    # ---- Bookings ----
    op.create_table(
        'bookings',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('booked_by_user_id', sa.BigInteger, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('guest_user_id', sa.BigInteger, sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('guest_name', sa.Text, nullable=True),
        sa.Column('hotel_id', sa.BigInteger, sa.ForeignKey('hotels.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('room_type_id', sa.BigInteger, sa.ForeignKey('room_types.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('room_id', sa.BigInteger, sa.ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('check_in', sa.DateTime(timezone=True), nullable=False),
        sa.Column('check_out', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Text, sa.CheckConstraint(
            "status IN ('pending','confirmed','checked_in','checked_out','cancelled')"
        ), server_default=sa.text("'confirmed'"), nullable=False),
        sa.Column('num_guests', sa.Integer, sa.CheckConstraint('num_guests > 0'), nullable=False),
        sa.Column('total_amount', sa.Numeric(12, 2), sa.CheckConstraint('total_amount >= 0'), nullable=False),
        sa.Column('currency', sa.Text, server_default=sa.text("'USD'"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('check_in < check_out', name='chk_time_valid'),
    )

    op.create_table(
        'booking_status_log',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('booking_id', sa.BigInteger, sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('changed_by_user_id', sa.BigInteger, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('from_status', sa.Text, nullable=True),
        sa.Column('to_status', sa.Text, nullable=False),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # ---- Indexes for performance ----
    op.create_index('idx_bookings_hotel', 'bookings', ['hotel_id'])
    op.create_index('idx_bookings_guest', 'bookings', ['guest_user_id'])

    # ---- Generated range column + exclusion constraint (no overlaps per room) ----
    # Use SQL to add generated column because Alembic support varies by PG version
    op.execute("""
        ALTER TABLE bookings
        ADD COLUMN stay tstzrange GENERATED ALWAYS AS (tstzrange(check_in, check_out, '[)')) STORED;
    """)
    op.execute("CREATE INDEX IF NOT EXISTS bookings_stay_gist_idx ON bookings USING gist (room_id, stay);")
    op.execute("""
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlap_per_room
        EXCLUDE USING gist (
            room_id WITH =,
            stay WITH &&
        )
        WHERE (status <> 'cancelled');
    """)

    # ---- Views ----
    op.execute("""
        CREATE OR REPLACE VIEW v_hotel_occupancy AS
        SELECT h.id AS hotel_id, h.name,
           SUM(CASE WHEN r.active AND r.status='available' THEN 1 ELSE 0 END) AS total_available_rooms,
           SUM(CASE WHEN r.active THEN 1 ELSE 0 END) AS total_rooms,
           CASE WHEN SUM(CASE WHEN r.active AND r.status='available' THEN 1 ELSE 0 END) = 0
                THEN 'Occupied' ELSE 'Available' END AS hotel_status
        FROM hotels h
        LEFT JOIN rooms r ON r.hotel_id = h.id
        GROUP BY h.id, h.name;
    """)

    op.execute("""
        CREATE OR REPLACE VIEW v_user_booking_counts_per_hotel AS
        SELECT b.guest_user_id AS user_id, b.hotel_id, COUNT(*) AS bookings_count
        FROM bookings b
        WHERE b.status <> 'cancelled' AND b.guest_user_id IS NOT NULL
        GROUP BY b.guest_user_id, b.hotel_id;
    """)

    # ---- Functions & Triggers ----
    # Find an available room for given window
    op.execute("""
    CREATE OR REPLACE FUNCTION fn_find_available_room(
        p_hotel_id BIGINT,
        p_room_type_id BIGINT,
        p_start TIMESTAMPTZ,
        p_end   TIMESTAMPTZ
    ) RETURNS BIGINT LANGUAGE plpgsql AS $$
    DECLARE r_id BIGINT;
    BEGIN
      SELECT r.id INTO r_id
      FROM rooms r
      WHERE r.hotel_id = p_hotel_id
        AND r.room_type_id = p_room_type_id
        AND r.active = true AND r.status = 'available'
        AND NOT EXISTS (
          SELECT 1 FROM bookings b
          WHERE b.room_id = r.id
            AND b.status IN ('pending','confirmed','checked_in')
            AND tstzrange(b.check_in, b.check_out, '[)') && tstzrange(p_start, p_end, '[)')
        )
      ORDER BY r.id
      LIMIT 1;
      RETURN r_id; -- NULL if none
    END; $$;
    """)

    # Stored procedure for booking creation (atomic), assigns room_id
    op.execute("""
    CREATE OR REPLACE FUNCTION sp_create_booking(
      p_booked_by BIGINT,
      p_guest_user BIGINT,
      p_guest_name TEXT,
      p_hotel BIGINT,
      p_room_type BIGINT,
      p_check_in TIMESTAMPTZ,
      p_check_out TIMESTAMPTZ,
      p_num_guests INT,
      p_total NUMERIC,
      p_currency TEXT DEFAULT 'USD'
    ) RETURNS BIGINT LANGUAGE plpgsql AS $$
    DECLARE v_room BIGINT; v_id BIGINT;
    BEGIN
      IF p_check_in >= p_check_out THEN RAISE EXCEPTION 'Invalid stay window'; END IF;

      SELECT fn_find_available_room(p_hotel, p_room_type, p_check_in, p_check_out) INTO v_room;
      IF v_room IS NULL THEN RAISE EXCEPTION 'No rooms available for the selected dates'; END IF;

      INSERT INTO bookings (
        booked_by_user_id, guest_user_id, guest_name,
        hotel_id, room_type_id, room_id,
        check_in, check_out, status, num_guests, total_amount, currency
      ) VALUES (
        p_booked_by, p_guest_user, p_guest_name,
        p_hotel, p_room_type, v_room,
        p_check_in, p_check_out, 'confirmed', p_num_guests, p_total, p_currency
      ) RETURNING id INTO v_id;

      RETURN v_id;
    END; $$;
    """)

    # Trigger to log status changes
    op.execute("""
    CREATE OR REPLACE FUNCTION trg_log_status() RETURNS TRIGGER AS $$
    BEGIN
      IF TG_OP = 'UPDATE' AND NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO booking_status_log(booking_id, changed_by_user_id, from_status, to_status)
        VALUES (NEW.id, NEW.booked_by_user_id, OLD.status, NEW.status);
      END IF;
      RETURN NEW;
    END; $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS bookings_log_status ON bookings;
    CREATE TRIGGER bookings_log_status
    AFTER UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION trg_log_status();
    """)

    # Helpful GIST index for time-window searches
    op.execute("CREATE INDEX IF NOT EXISTS idx_bookings_stay_gist ON bookings USING gist (stay);")


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS bookings_log_status ON bookings;")
    op.execute("DROP FUNCTION IF EXISTS trg_log_status;")
    op.execute("DROP FUNCTION IF EXISTS sp_create_booking;")
    op.execute("DROP FUNCTION IF EXISTS fn_find_available_room;")
    op.execute("DROP VIEW IF EXISTS v_user_booking_counts_per_hotel;")
    op.execute("DROP VIEW IF EXISTS v_hotel_occupancy;")
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS no_overlap_per_room;")
    op.execute("DROP INDEX IF EXISTS bookings_stay_gist_idx;")
    op.execute("DROP INDEX IF EXISTS idx_bookings_stay_gist;")
    op.drop_index('idx_bookings_guest', table_name='bookings')
    op.drop_index('idx_bookings_hotel', table_name='bookings')
    op.drop_table('booking_status_log')
    op.drop_table('bookings')
    op.drop_table('rooms')
    op.drop_table('room_types')
    op.drop_table('hotel_images')
    op.drop_table('hotels')
