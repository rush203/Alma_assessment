
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251027_160512"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('role', sa.Enum('attorney', name='userrole'), nullable=True, server_default='attorney'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    op.create_table(
        'leads',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('resume_path', sa.String(length=512), nullable=False),
        sa.Column('state', sa.Enum('PENDING', 'REACHED_OUT', name='leadstate'), nullable=False, server_default='PENDING'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_email'), 'leads', ['email'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_leads_email'), table_name='leads')
    op.drop_table('leads')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS leadstate")
