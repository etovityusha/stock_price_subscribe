import logging
from typing import Callable, Type

from celery import Celery
from pydantic_settings import BaseSettings
from sqlalchemy.orm import Session

from models.domain.instument import Instrument
from models.domain.user import User
from repo.instrument import InstrumentAlchemyRepo
from repo.instrument_price import InstrumentPriceAlchemyRepo
from repo.subscription import SubscriptionAlchemyRepo
from repo.user import UserRepo, UserAlchemyRepo
from services.commands.dto import (
    CommandAddData,
    CommandDeleteAllData,
    CommandDeleteData,
    CommandMyData,
    CommandPriceData,
    CommandStepData,
    TickerCommandData,
)
from services.commands.handler.add import DefaultAddCommandHandler
from services.commands.handler.delete import DefaultDeleteCommandHandler
from services.commands.handler.delete_all import DefaultDeleteAllCommandHandler
from services.commands.handler.my import DefaultMyCommandHandler
from services.commands.handler.price import DefaultPriceCommandHandler
from services.commands.handler.step import DefaultStepCommandHandler
from services.database import session_factory
from services.instrument import DefaultInstrumentService
from services.instrument_finder import TinkoffInstrumentFinderService
from services.message import get_locale_msg_builder
from services.price import TinkoffPriceService
from services.price_updater import PriceUpdaterServiceImpl
from services.subscriptions import DefaultSubscriptionsService
from services.telegram import Telegram
from services.uow import AlchemyUoW
from log import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class CeleryConfig(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    BROKER_URL: str
    TINKOFF_TOKEN: str
    BOT_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "ignore"


cfg = CeleryConfig()

app = Celery(__name__, broker=cfg.BROKER_URL)

app.conf.beat_schedule = {
    "run_all_tickers_together": {
        "task": "run_all_tickers_together",
        "schedule": 45,
    },
}
app.conf.update(
    task_soft_time_limit=180,
    task_time_limit=180,
)

tg_client = Telegram(bot_token=cfg.BOT_TOKEN)
loggger = logging.getLogger(__name__)


@app.task(name="send_message_to_tg")
def send_message_to_tg(chat_id: int, message: str) -> bool:
    return tg_client.send_message(chat_id=chat_id, message=message)


@app.task(name="run_all_tickers_together")
def run_all_tickers_together():
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        instrument_repo = InstrumentAlchemyRepo(session)
        instruments: list[Instrument] = instrument_repo.find_by()
        uow = AlchemyUoW(session)
        prices_svc = TinkoffPriceService(
            cfg.TINKOFF_TOKEN,
        )
        logger.info("Get instrument prices")
        prices_data = prices_svc.get_prices(instruments=instruments)
        logger.info("Instrument prices retrieved successfully")
        price_updater_svc = PriceUpdaterServiceImpl(
            uow=uow,
            instrument_prices_repo=InstrumentPriceAlchemyRepo(session),
        )
        prices = price_updater_svc.update_prices(prices_data)
        logger.info("Prices in database updated successfully")
        subscriptions_svc = DefaultSubscriptionsService(
            uow=uow, subscription_repo=SubscriptionAlchemyRepo(session), user_repo=UserAlchemyRepo(session)
        )
        messages = subscriptions_svc.get_messages_and_update(prices=prices)
        logger.info("The messages were built successfully", extra={"count": len(messages)})
        for msg in messages:
            send_message_to_tg.apply_async(
                kwargs=dict(
                    chat_id=msg.user_chat_id,
                    message=msg.message,
                )
            )


def get_price_cmd_handler(session: Session) -> DefaultPriceCommandHandler:
    return DefaultPriceCommandHandler(
        instrument_repo=InstrumentAlchemyRepo(session),
        instrument_price_repo=InstrumentPriceAlchemyRepo(session),
    )


def get_instrument_svc(session: Session) -> DefaultInstrumentService:
    return DefaultInstrumentService(
        finders=[TinkoffInstrumentFinderService(token=cfg.TINKOFF_TOKEN)],
        uow=AlchemyUoW(session),
        instrument_repo=InstrumentAlchemyRepo(session),
    )


def get_add_cmd_handler(session: Session) -> DefaultAddCommandHandler:
    return DefaultAddCommandHandler(
        instrument_svc=get_instrument_svc(session),
        uow=AlchemyUoW(session),
        subscription_repo=SubscriptionAlchemyRepo(session),
    )


def get_delete_cmd_handler(session: Session) -> DefaultDeleteCommandHandler:
    return DefaultDeleteCommandHandler(
        instrument_svc=get_instrument_svc(session),
        uow=AlchemyUoW(session),
        subscription_repo=SubscriptionAlchemyRepo(session),
    )


def get_step_cmd_handler(session: Session) -> DefaultStepCommandHandler:
    return DefaultStepCommandHandler(
        instrument_svc=get_instrument_svc(session),
        uow=AlchemyUoW(session),
        subscription_repo=SubscriptionAlchemyRepo(session),
    )


def get_delete_all_cmd_handler(session: Session) -> DefaultDeleteAllCommandHandler:
    return DefaultDeleteAllCommandHandler(
        uow=AlchemyUoW(session),
        subscription_repo=SubscriptionAlchemyRepo(session),
    )


def get_my_cmd_handler(session: Session) -> DefaultMyCommandHandler:
    return DefaultMyCommandHandler(
        subscription_repo=SubscriptionAlchemyRepo(session),
    )


def get_user_repo(session: Session) -> UserRepo:
    return UserAlchemyRepo(session)


def handle_cmd(
    get_cmd_handler: Callable,
    user_id: int,
    chat_id: int,
    message_id: int,
    command_model: Type[TickerCommandData],
    **kwargs,
) -> None:
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        svc = get_cmd_handler(session)
        result = svc.handle(user_id, command_model.model_validate(kwargs))
        user: User = get_user_repo(session).get_by_id(user_id)
        response = get_locale_msg_builder(user.locale).add_cmd_msg(result)
        tg_client.send_message(chat_id=chat_id, reply_to_msg_id=message_id, message=response)


@app.task(name="handle_add_cmd")
def handle_add_cmd(user_id: int, chat_id: int, message_id: int, **kwargs):
    handle_cmd(get_add_cmd_handler, user_id, chat_id, message_id, CommandAddData, **kwargs)


@app.task(name="handle_step_cmd")
def handle_step_cmd(user_id: int, chat_id: int, message_id: int, **kwargs):
    handle_cmd(get_step_cmd_handler, user_id, chat_id, message_id, CommandStepData, **kwargs)


@app.task(name="handle_delete_cmd")
def handle_delete_cmd(user_id: int, chat_id: int, message_id: int, **kwargs):
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        svc = get_delete_cmd_handler(session)
        result = svc.handle(user_id, CommandDeleteData.model_validate(kwargs))
        user: User = get_user_repo(session).get_by_id(user_id)
        return tg_client.send_message(
            chat_id=chat_id,
            reply_to_msg_id=message_id,
            message=get_locale_msg_builder(user.locale).delete_cmd_msg(result),
        )


@app.task(name="handle_price_cmd")
def handle_price_cmd(user_id: int, chat_id: int, message_id: int, **kwargs):
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        svc = get_price_cmd_handler(session)
        user: User = get_user_repo(session).get_by_id(user_id)
        msg_builder = get_locale_msg_builder(user.locale)
        try:
            result = svc.handle(user_id, CommandPriceData.model_validate(kwargs))
        except svc.InstrumentNotFoundError:
            tg_client.send_message(
                chat_id=chat_id,
                reply_to_msg_id=message_id,
                message=msg_builder.instrument_not_found_error_msg(),
            )
        tg_client.send_message(
            chat_id=chat_id,
            reply_to_msg_id=message_id,
            message=msg_builder.price_cmd_msg(result),
        )


@app.task(name="handle_delete_all_cmd")
def handle_delete_all_cmd(user_id: int, chat_id: int, message_id: int, **kwargs) -> None:
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        svc = get_delete_all_cmd_handler(session)
        result = svc.handle(user_id, CommandDeleteAllData.model_validate(kwargs))
        user: User = get_user_repo(session).get_by_id(user_id)
        tg_client.send_message(
            chat_id=chat_id,
            reply_to_msg_id=message_id,
            message=get_locale_msg_builder(user.locale).delete_cmd_msg(result),
        )


@app.task(name="handle_my_cmd")
def handle_my_cmd(user_id: int, chat_id: int, message_id: int, **kwargs) -> None:
    with session_factory(cfg.SQLALCHEMY_DATABASE_URI)() as session:
        svc = get_my_cmd_handler(session)
        result = svc.handle(user_id, CommandMyData.model_validate(kwargs))
        user: User = get_user_repo(session).get_by_id(user_id)
        tg_client.send_message(
            chat_id=chat_id,
            reply_to_msg_id=message_id,
            message=get_locale_msg_builder(user.locale).my_cmd_msg(result),
        )
