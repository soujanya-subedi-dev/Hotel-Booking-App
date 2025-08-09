from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('full_name', sa.Text, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('phone', sa.Text),
        sa.Column('role', sa.String(length=10), nullable=False, server_default='user'),
        sa.Column('password_hash', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Optional: convert email to CITEXT for case-insensitive unique (Postgres-only)
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE CITEXT;")


def downgrade():
    op.drop_table('users')