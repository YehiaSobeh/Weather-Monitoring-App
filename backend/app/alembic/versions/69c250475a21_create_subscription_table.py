"""create subscription table

Revision ID: 69c250475a21
Revises: 68b0433a3ab3
Create Date: 2025-04-27 17:31:27.407231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "69c250475a21"
down_revision: Union[str, None] = "68b0433a3ab3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("city", sa.String, nullable=False),
        sa.Column("temperature_threshold", sa.Float, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.TIMESTAMP()),
    )
    sa.ForeignKeyConstraint(
        ["user_id"],
        ["users.id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_table("subscriptions")
