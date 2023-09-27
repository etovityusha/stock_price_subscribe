import abc
import decimal
from typing import Any, Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from enums import SubscriptionTypeEnum
from models.domain.subscription import Subscription
from models.orm.subscription import SubscriptionORM
from repo.base import AlchemyGenericRepository


class SubscriptionRepo(abc.ABC):
    @abc.abstractmethod
    def find_by(
        self,
        id_: int | None = None,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price: decimal.Decimal | None = None,
        is_active: bool | None = None,
        price_gte: decimal.Decimal | None = None,
        price_lt: decimal.Decimal | None = None,
        crossing_disabled: bool | None = None,
        type_: SubscriptionTypeEnum | None = None,
    ) -> list[Subscription]:
        pass

    @abc.abstractmethod
    def create(
        self,
        user_id: int,
        instrument_id: int,
        price: decimal.Decimal,
        type_: SubscriptionTypeEnum,
        is_active: bool,
    ) -> None:
        pass

    @abc.abstractmethod
    def delete_by(
        self,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price_in: Iterable[decimal.Decimal] | None = None,
    ) -> int:
        pass

    @abc.abstractmethod
    def update_by(
        self,
        update_data: dict[str, Any],
        id_: int | None = None,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price: decimal.Decimal | None = None,
        price_gte: decimal.Decimal | None = None,
        price_lt: decimal.Decimal | None = None,
        is_active: bool | None = None,
        crossing_disabled: bool | None = None,
        type_: SubscriptionTypeEnum | None = None,
    ) -> int:
        pass


class SubscriptionAlchemyRepo(SubscriptionRepo, AlchemyGenericRepository[Subscription]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Subscription, SubscriptionORM)

    def find_by(
        self,
        id_: int | None = None,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price: decimal.Decimal | None = None,
        price_gte: decimal.Decimal | None = None,
        price_lt: decimal.Decimal | None = None,
        is_active: bool | None = None,
        crossing_disabled: bool | None = None,
        type_: SubscriptionTypeEnum | None = None,
    ) -> list[Subscription]:
        query = select(SubscriptionORM).options(
            joinedload(SubscriptionORM.instrument),
            joinedload(SubscriptionORM.user),
        )
        conditions = self._find_conditions(
            id_=id_,
            user_id=user_id,
            instrument_id=instrument_id,
            price=price,
            price_gte=price_gte,
            price_lt=price_lt,
            is_active=is_active,
            crossing_disabled=crossing_disabled,
            type_=type_,
        )
        result = self._session.execute(query.where(*conditions)).scalars()
        return [
            Subscription(
                id=r.id,
                user_id=r.user_id,
                user_chat_id=r.user.chat_id,
                instrument_id=r.instrument_id,
                instrument_ticker=r.instrument.ticker,
                instrument_precision=r.instrument.precision,
                crossing_disabled=r.crossing_disabled,
                is_active=r.is_active,
                price=r.price,
                type=r.type,
            )
            for r in result
        ]

    def create(
        self,
        user_id: int,
        instrument_id: int,
        price: decimal.Decimal,
        type_: SubscriptionTypeEnum,
        is_active: bool,
    ) -> None:
        new_subscription = SubscriptionORM(
            user_id=user_id,
            instrument_id=instrument_id,
            price=price,
            is_active=is_active,
            type=type_,
        )
        self._session.add(new_subscription)

    def delete_by(
        self,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price_in: Iterable[decimal.Decimal] | None = None,
    ) -> int:
        stmt = delete(SubscriptionORM)
        where_clauses = []

        if user_id is not None:
            where_clauses.append(SubscriptionORM.user_id == user_id)
        if instrument_id is not None:
            where_clauses.append(SubscriptionORM.instrument_id == instrument_id)
        if price_in is not None:
            where_clauses.append(SubscriptionORM.price.in_(price_in))
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        return self._session.execute(stmt).rowcount  # noqa

    def update_by(
        self,
        update_data: dict[str, Any],
        id_: int | None = None,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price: decimal.Decimal | None = None,
        price_gte: decimal.Decimal | None = None,
        price_lt: decimal.Decimal | None = None,
        is_active: bool | None = None,
        crossing_disabled: bool | None = None,
        type_: SubscriptionTypeEnum | None = None,
    ) -> int:
        conditions = self._find_conditions(
            id_=id_,
            user_id=user_id,
            instrument_id=instrument_id,
            price=price,
            price_gte=price_gte,
            price_lt=price_lt,
            is_active=is_active,
            crossing_disabled=crossing_disabled,
            type_=type_,
        )
        qry = self._session.query(SubscriptionORM)
        print(conditions)
        if conditions:
            qry = qry.filter(*conditions)
        return qry.update(update_data)

    def _find_conditions(
        self,
        id_: int | None = None,
        user_id: int | None = None,
        instrument_id: int | None = None,
        price: decimal.Decimal | None = None,
        price_gte: decimal.Decimal | None = None,
        price_lt: decimal.Decimal | None = None,
        is_active: bool | None = None,
        crossing_disabled: bool | None = None,
        type_: SubscriptionTypeEnum | None = None,
    ) -> list[bool]:
        conditions = []
        if id_ is not None:
            conditions.append(SubscriptionORM.id == id_)
        if user_id is not None:
            conditions.append(SubscriptionORM.user_id == user_id)
        if instrument_id is not None:
            conditions.append(SubscriptionORM.instrument_id == instrument_id)
        if price is not None:
            conditions.append(SubscriptionORM.price == price)
        if price_gte is not None:
            conditions.append(SubscriptionORM.price >= price_gte)
        if price_lt is not None:
            conditions.append(SubscriptionORM.price < price_lt)
        if is_active is not None:
            conditions.append(SubscriptionORM.is_active.is_(is_active))
        if crossing_disabled is not None:
            conditions.append(SubscriptionORM.crossing_disabled.is_(crossing_disabled))
        if type_ is not None:
            conditions.append(SubscriptionORM.type == type_)
        return conditions
