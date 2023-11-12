from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import LocaleEnum
from models.orm.base import BaseORM


class UserORM(BaseORM):
    __tablename__ = "user"

    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None]
    phone: Mapped[str | None]

    subscriptions: Mapped["SubscriptionORM"] = relationship(back_populates="user")
    locale: Mapped[LocaleEnum] = mapped_column(default=LocaleEnum.RU, server_default="RU")
