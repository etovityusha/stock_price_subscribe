import enum
import logging
from contextlib import contextmanager
from typing import Callable

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from bot.keyboard import get_keyboard
from enums import LocaleEnum
from models.domain.user import User
from repo.user import UserAlchemyRepo
from services.commands.dto import (
    CommandAddData,
    CommandDeleteAllData,
    CommandDeleteData,
    CommandMyData,
    CommandPriceData,
    CommandStepData,
)
from services.commands.parser.default import DefaultCommandParserService
from services.database import session_factory
from services.message import EnLocaleMessageBuilder, get_locale_msg_builder
from services.registration import AlreadyRegisteredError, TelegramBotRegistrationService
from services.uow import AlchemyUoW
from services.user import DefaultUserService
from worker import (
    handle_add_cmd,
    handle_delete_all_cmd,
    handle_delete_cmd,
    handle_my_cmd,
    handle_price_cmd,
    handle_step_cmd,
)


class BotConfig(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    BOT_TOKEN: str
    BOT_OWNER_USERNAME: str
    BOT_OWNER_CHAT_ID: int
    TINKOFF_TOKEN: str
    BROKER_URL: str
    WEBAPP_PAGE_URL: str
    LOGGING_LEVEL: str = "INFO"

    IS_SEND_PARSING_ERROR_MESSAGES_TO_BOT_OWNER: bool

    class Config:
        env_file = ".env"
        extra = "ignore"


cfg = BotConfig()
TOKEN = cfg.BOT_TOKEN
bot = Bot(token=TOKEN)
logger = logging.getLogger(__name__)
logger.setLevel(cfg.LOGGING_LEVEL)

type_task_map = {
    CommandAddData: handle_add_cmd,
    CommandStepData: handle_step_cmd,
    CommandDeleteData: handle_delete_cmd,
    CommandPriceData: handle_price_cmd,
    CommandDeleteAllData: handle_delete_all_cmd,
    CommandMyData: handle_my_cmd,
}
KEYBOARD = get_keyboard(web_app_url=cfg.WEBAPP_PAGE_URL)


def send_parsing_error_message_to_bot_owner(config: BotConfig, message: types.Message) -> None:
    bot.send_message(
        chat_id=config.BOT_OWNER_CHAT_ID,
        text=f"INCORRECT MESSAGE FROM @{message.from_user.username}: {message.text}",
    )


def get_parsing_error_callbacks(config: BotConfig) -> list[Callable[[BotConfig, types.Message], None]]:
    result: list[Callable[[BotConfig, types.Message], None]] = []
    if config.IS_SEND_PARSING_ERROR_MESSAGES_TO_BOT_OWNER:
        result.append(send_parsing_error_message_to_bot_owner)
    return result


@contextmanager
def get_db_session():
    global cfg
    session = session_factory(cfg.SQLALCHEMY_DATABASE_URI)()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


class MessageTypeEnum(enum.Enum):
    TEXT = "TEXT"
    WEB_APP_DATA = "WEB_APP_DATA"


class MessageContext(BaseModel):
    user: User
    message: types.Message
    text: str

    class Config:
        arbitrary_types_allowed = True


def msg_context(msg_type: MessageTypeEnum = MessageTypeEnum.TEXT):
    def _decorator(func):
        async def wrapper(message: types.Message) -> None:
            text = message.web_app_data.data if msg_type == MessageTypeEnum.WEB_APP_DATA else message.text
            with get_db_session() as session:
                svc = DefaultUserService(user_repo=UserAlchemyRepo(session))
                user = svc.get_user_by_chat_id(message.from_user.id)
            await func(ctx=MessageContext(user=user, message=message, text=text))

        return wrapper

    return _decorator


async def process_start_command(message: types.Message) -> None:
    msg_builder = EnLocaleMessageBuilder()
    with get_db_session() as db_session:
        svc = TelegramBotRegistrationService(uow=AlchemyUoW(db_session), user_repo=UserAlchemyRepo(db_session))
        try:
            svc.register_user(
                chat_id=message.from_user.id,
                username=message.from_user.username,
                phone=None,
            )
            reply_text = msg_builder.welcome_new_user_msg()
        except AlreadyRegisteredError:
            reply_text = msg_builder.welcome_old_user_msg()
        await message.reply(text=reply_text, reply_markup=KEYBOARD)


@msg_context(msg_type=MessageTypeEnum.TEXT)
async def cmd_help(ctx: MessageContext) -> None:
    msg_builder = get_locale_msg_builder(ctx.user.locale)
    await ctx.message.answer(msg_builder.help_msg(), reply_markup=KEYBOARD, parse_mode="Markdown")


async def process_custom_command(
    user_id: int,
    user_locale: LocaleEnum,
    message: types.Message,
    text: str,
    type_task: dict,
) -> None:
    logger.info({"user_id": user_id, "command": text})
    message_id = message.message_id
    try:
        parser = DefaultCommandParserService()
        parser_result = parser.get_command_data(text)
    except Exception:
        msg_builder = get_locale_msg_builder(user_locale)
        await message.reply(msg_builder.parse_error_msg(cfg.BOT_OWNER_USERNAME), parse_mode="Markdown")
        logger.debug({"user_id": user_id, "command": text, "parsed": False})
        for callback in get_parsing_error_callbacks(cfg):
            try:
                callback(cfg, message)
            except:
                logger.error(f"Callback {callback.__name__} error")

        return
    logger.debug({"user_id": user_id, "command": text, "parsed": True})
    type_task[type(parser_result)].apply_async(
        kwargs={
            "user_id": user_id,
            "chat_id": message.chat.id,
            "message_id": message_id,
            **parser_result.model_dump(),
        },
    )


@msg_context(msg_type=MessageTypeEnum.WEB_APP_DATA)
async def web_app(ctx: MessageContext) -> None:
    await process_custom_command(
        user_id=ctx.user.identity,
        user_locale=ctx.user.locale,
        message=ctx.message,
        text=ctx.text,
        type_task=type_task_map,
    )


@msg_context(msg_type=MessageTypeEnum.TEXT)
async def handle_commands(ctx: MessageContext) -> None:
    await process_custom_command(
        user_id=ctx.user.identity,
        user_locale=ctx.user.locale,
        message=ctx.message,
        text=ctx.text,
        type_task=type_task_map,
    )


class TgBot:
    def __init__(self) -> None:
        self.cfg = BotConfig()  # type[call-arg]
        self.token = cfg.BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(self.bot)

    def register_handlers(self) -> None:
        self.dp.register_message_handler(process_start_command, commands="start")
        self.dp.register_message_handler(cmd_help, commands="help")
        self.dp.register_message_handler(handle_commands)
        self.dp.register_message_handler(web_app, content_types=["web_app_data"])

    def run(self) -> None:
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    bot_instance = TgBot()
    bot_instance.register_handlers()
    bot_instance.run()
