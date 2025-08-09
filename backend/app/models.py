from . import db
from sqlalchemy.sql import func

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)  # migrated to CITEXT via Alembic
    phone = db.Column(db.Text)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'user' | 'admin'
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    