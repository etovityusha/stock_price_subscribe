import decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import SubscriptionTypeEnum
from models.orm.base import BaseORM


class SubscriptionORM(BaseORM):
    __tablename__ = "subscription"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["UserORM"] = relationship(back_populates="subscriptions")
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instrument.id"))
    instrument: Mapped["InstrumentORM"] = relationship(back_populates="subscriptions")
    price: Mapped[decimal.Decimal]
    type: Mapped[SubscriptionTypeEnum] = mapped_column(default=SubscriptionTypeEnum.ALWAYS, server_default="ALWAYS")
    crossing_disabled: Mapped[bool] = mapped_column(default=False, server_default="false")
    is_active: Mapped[bool]
