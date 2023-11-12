"""empty message

Revision ID: 6cc64ec8e1b2
Revises: 0161d7eac197
Create Date: 2023-11-11 13:57:13.147297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6cc64ec8e1b2"
down_revision: Union[str, None] = "0161d7eac197"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE instrumenttypeenum ADD VALUE 'FUTURES'")


def downgrade() -> None:
    pass
