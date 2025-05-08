"""Create Car table

Revision ID: d2c38c38fc0c
Revises:
Create Date: 2025-05-08 21:32:07.361385

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2c38c38fc0c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("price_usd", sa.Integer(), nullable=False),
        sa.Column("odometer", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=100), nullable=False),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column("images_count", sa.Integer(), nullable=False),
        sa.Column("car_number", sa.String(length=20), nullable=True),
        sa.Column("car_vin", sa.String(length=30), nullable=True),
        sa.Column(
            "datetime_found",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cars")),
        sa.UniqueConstraint("car_vin", name=op.f("uq_cars_car_vin")),
        sa.UniqueConstraint("url", name=op.f("uq_cars_url")),
    )
    op.create_index(op.f("ix_cars_title"), "cars", ["title"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_cars_title"), table_name="cars")
    op.drop_table("cars")
