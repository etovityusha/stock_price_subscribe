from sqlalchemy.orm import Mapped, relationship

from enums import InstrumentTypeEnum
from models.orm.base import BaseORM


class InstrumentORM(BaseORM):
    __tablename__ = "instrument"

    ticker: Mapped[str]
    figi: Mapped[str]
    isin: Mapped[str]
    type: Mapped[InstrumentTypeEnum]
    precision: Mapped[int]

    subscriptions: Mapped["SubscriptionORM"] = relationship(back_populates="instrument")
    instrument_price = relationship("InstrumentPriceORM", back_populates="instrument")
