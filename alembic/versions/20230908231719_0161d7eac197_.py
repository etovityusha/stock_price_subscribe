"""
empty message

Revision ID: 0161d7eac197
Revises: 1b9be210ddb6
Create Date: 2023-09-08 23:17:19.262547

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0161d7eac197"
down_revision: Union[str, None] = "1b9be210ddb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column("user", "chat_id", existing_type=sa.Integer(), type_=sa.BigInteger())


def downgrade():
    op.alter_column("user", "chat_id", existing_type=sa.BigInteger(), type_=sa.Integer())
