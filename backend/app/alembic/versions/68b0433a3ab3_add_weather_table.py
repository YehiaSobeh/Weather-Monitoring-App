"""add weather table

Revision ID: 68b0433a3ab3
Revises: 5d4b8f61497b
Create Date: 2025-04-26 17:08:30.519993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68b0433a3ab3"
down_revision: Union[str, None] = "5d4b8f61497b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "weather",
        sa.Column(
            "id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Integer(), nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("pressure", sa.Integer(), nullable=True),
        sa.Column(
            "fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weather_city"), "weather", ["city"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_weather_city"), table_name="weather")
    op.drop_table("weather")
