"""currency instrument

Revision ID: 059bde73b635
Revises: 1c5264d2e0cb
Create Date: 2023-11-19 13:53:35.536836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "059bde73b635"
down_revision: Union[str, None] = "1c5264d2e0cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE instrumenttypeenum ADD VALUE 'CURRENCY'")


def downgrade() -> None:
    pass
