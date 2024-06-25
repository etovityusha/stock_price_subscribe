"""empty message

Revision ID: 97127c8d3d1b
Revises: fc797f9c3c01
Create Date: 2024-06-24 17:47:42.736781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "97127c8d3d1b"
down_revision: Union[str, None] = "fc797f9c3c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE instrumenttypeenum ADD VALUE 'ETF'")


def downgrade() -> None:
    pass
