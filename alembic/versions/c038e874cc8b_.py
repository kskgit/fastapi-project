"""empty message

Revision ID: c038e874cc8b
Revises: a806b45bf417
Create Date: 2025-11-24 10:19:16.902655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c038e874cc8b'
down_revision: Union[str, None] = 'a806b45bf417'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = postgresql.ENUM('ADMIN', 'MEMBER', 'VIEWER', name='userrole')


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)

    op.add_column(
        'users',
        sa.Column(
            'role',
            user_role_enum,
            nullable=False,
            server_default='MEMBER',
        ),
    )
    op.alter_column('users', 'role', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
    bind = op.get_bind()
    user_role_enum.drop(bind, checkfirst=True)
