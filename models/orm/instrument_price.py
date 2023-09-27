import decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.orm.base import BaseORM


class InstrumentPriceORM(BaseORM):
    __tablename__ = "instrument_price"

    instrument_id: Mapped[int] = mapped_column(ForeignKey("instrument.id"))
    instrument: Mapped["InstrumentORM"] = relationship(back_populates="instrument_price")

    price: Mapped[decimal.Decimal]
