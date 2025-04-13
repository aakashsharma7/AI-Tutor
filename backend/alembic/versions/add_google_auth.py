"""add google auth fields

Revision ID: add_google_auth
Revises: 91b9e3ef9166
Create Date: 2023-06-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_google_auth'
down_revision: Union[str, None] = '91b9e3ef9166'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add Google authentication fields to users table
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('picture', sa.String(), nullable=True))
    
    # Make hashed_password nullable for Google auth
    op.alter_column('users', 'hashed_password', nullable=True)
    
    # Add unique constraint for google_id
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove Google authentication fields
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_column('users', 'picture')
    op.drop_column('users', 'google_id')
    
    # Make hashed_password non-nullable again
    op.alter_column('users', 'hashed_password', nullable=False) 