import abc
import decimal
from typing import Generator

from pydantic import BaseModel

from repo.subscription import SubscriptionRepo
from services.commands.dto import CommandStepData
from services.instrument import InstrumentService
from services.uow import UoW


class StepCommandResult(BaseModel):
    added: list[decimal.Decimal]
    errors: list[decimal.Decimal]
    precision: int


class StepCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandStepData) -> StepCommandResult:
        pass


class DefaultStepCommandHandler(StepCommandHandler):
    def __init__(
        self,
        instrument_svc: InstrumentService,
        uow: UoW,
        subscription_repo: SubscriptionRepo,
    ) -> None:
        self._instrument_svc = instrument_svc
        self._subscription_repo = subscription_repo
        self._uow = uow

    def handle(self, user_id: int, data: CommandStepData) -> StepCommandResult:
        added, errors = [], []
        instrument = self._instrument_svc.get_or_create_by_ticker(data.ticker)
        for price in self._generate_prices(from_=data.price_from, to=data.price_to, step=data.step):
            price: decimal.Decimal = round(price, instrument.precision)  # noqa
            if not self._subscription_repo.find_by(
                user_id=user_id,
                instrument_id=instrument.identity,
                price=price,
                is_active=True,
            ):
                self._subscription_repo.create(
                    user_id=user_id,
                    instrument_id=instrument.identity,
                    price=price,
                    type_=data.type,
                    is_active=True,
                )
                added.append(price)
            else:
                errors.append(price)

        self._uow.commit()
        return StepCommandResult(added=added, errors=errors)

    @classmethod
    def _generate_prices(
        cls, from_: decimal.Decimal, to: decimal.Decimal, step: decimal.Decimal
    ) -> Generator[decimal.Decimal, None, None]:
        current_price = from_
        while current_price <= to:
            yield current_price
            current_price += step
