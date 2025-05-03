"""create users table

Revision ID: 5d4b8f61497b
Revises:
Create Date: 2025-04-26 01:14:24.283896

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d4b8f61497b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(255)),
        sa.Column("surname", sa.String(255)),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column("updated_at", sa.TIMESTAMP()),
    )
    sa.UniqueConstraint("email")
    op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
