from typing import Union, Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1c5264d2e0cb"
down_revision: Union[str, None] = "6cc64ec8e1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

localeenum = sa.Enum("RU", "EN", name="localeenum")


def upgrade() -> None:
    localeenum.create(op.get_bind())
    op.add_column("user", sa.Column("locale", localeenum, nullable=False, server_default="RU"))


def downgrade() -> None:
    op.drop_column("user", "locale")
    localeenum.drop(op.get_bind())