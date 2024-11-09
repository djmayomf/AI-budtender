from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('oauth_provider', sa.String(50)),
        sa.Column('oauth_id', sa.String(255)),
        sa.Column('two_factor_secret', sa.String(32)),
        sa.Column('two_factor_enabled', sa.Boolean(), default=False),
        sa.Column('role', sa.String(20), default='user'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('permissions', sa.String(512)),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_oauth', 'users', ['oauth_provider', 'oauth_id']) 