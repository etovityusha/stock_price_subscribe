from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo


def get_keyboard(web_app_url: str) -> ReplyKeyboardMarkup:
    help_button = KeyboardButton("/help")
    webapp_button = KeyboardButton("Add via web", web_app=WebAppInfo(url=web_app_url))
    return ReplyKeyboardMarkup([[help_button, webapp_button]], resize_keyboard=True)
