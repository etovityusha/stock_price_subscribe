import abc
import decimal

from pydantic import BaseModel

from repo.subscription import SubscriptionRepo
from services.commands.dto import CommandAddData
from services.instrument import InstrumentService
from services.uow import UoW


class AddCommandResult(BaseModel):
    added: list[decimal.Decimal]
    errors: list[decimal.Decimal]
    precision: int


class AddCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandAddData) -> AddCommandResult:
        pass


class DefaultAddCommandHandler(AddCommandHandler):
    def __init__(
        self,
        instrument_svc: InstrumentService,
        uow: UoW,
        subscription_repo: SubscriptionRepo,
    ) -> None:
        self._instrument_svc = instrument_svc
        self._subscription_repo = subscription_repo
        self._uow = uow

    def handle(self, user_id: int, data: CommandAddData) -> AddCommandResult:
        added, errors = [], []
        instrument = self._instrument_svc.get_or_create_by_ticker(data.ticker)
        for price in data.prices:
            rouded_price: decimal.Decimal = round(price, instrument.precision)  # noqa
            if not self._subscription_repo.find_by(
                user_id=user_id,
                instrument_id=instrument.identity,
                price=rouded_price,
                is_active=True,
            ):
                self._subscription_repo.create(
                    user_id=user_id,
                    instrument_id=instrument.identity,
                    price=rouded_price,
                    type_=data.type,
                    is_active=True,
                )
                added.append(rouded_price)
            else:
                errors.append(rouded_price)
        self._uow.commit()
        return AddCommandResult(added=added, errors=errors, precision=instrument.precision)
