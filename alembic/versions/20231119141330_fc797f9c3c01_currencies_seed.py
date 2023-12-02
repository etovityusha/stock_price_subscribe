"""currencies seed

Revision ID: fc797f9c3c01
Revises: 059bde73b635
Create Date: 2023-11-19 14:13:30.235721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fc797f9c3c01"
down_revision: Union[str, None] = "059bde73b635"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


currencies = [
    {
        "ticker": "AMDRUB",
        "isin": "",
        "figi": "BBG0013J7V24",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "KZTRUB",
        "isin": "",
        "figi": "BBG0013HG026",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "KGSRUB",
        "isin": "",
        "figi": "BBG0013J7Y00",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "UZSRUB",
        "isin": "",
        "figi": "BBG0013HQ310",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "USDRUB",
        "isin": "",
        "figi": "BBG0013HGFT4",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "CNYRUB",
        "isin": "",
        "figi": "BBG0013HRTL0",
        "type": "CURRENCY",
        "precision": 3,
    },
    {
        "ticker": "TJSRUB",
        "isin": "",
        "figi": "BBG0013J11P1",
        "type": "CURRENCY",
        "precision": 0,
    },
    {
        "ticker": "BYNRUB",
        "isin": "",
        "figi": "BBG00D87WQY7",
        "type": "CURRENCY",
        "precision": 4,
    },
    {
        "ticker": "HKDRUB",
        "isin": "",
        "figi": "BBG0013HSW87",
        "type": "CURRENCY",
        "precision": 3,
    },
    {
        "ticker": "GLDRUB",
        "isin": "",
        "figi": "BBG000VJ5YR4",
        "type": "CURRENCY",
        "precision": 2,
    },
    {
        "ticker": "TRYRUB",
        "isin": "",
        "figi": "BBG0013J12N1",
        "type": "CURRENCY",
        "precision": 3,
    },
    {
        "ticker": "SLVRUB",
        "isin": "",
        "figi": "BBG000VHQTD1",
        "type": "CURRENCY",
        "precision": 2,
    },
]


def upgrade() -> None:
    values = ", ".join(
        f"('{c['ticker']}', '{c['figi']}', '{c['isin']}', '{c['type']}', {c['precision']})" for c in currencies
    )
    op.execute(f"INSERT INTO instrument (ticker, figi, isin, type, precision) VALUES {values}")


def downgrade() -> None:
    pass
