import logging

import requests

logger = logging.getLogger(__name__)

class Telegram:
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, bot_token: str):
        self.bot_token = bot_token

    def send_message(
        self,
        chat_id: int,
        message: str,
        disable_notification: bool = False,
        reply_to_msg_id: int | None = None,
    ) -> bool:
        messages = self._split_long_text(text=message)
        responses_oks = []
        for message_text in messages:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={chat_id}&text={message_text}"
            if disable_notification:
                url += "&disable_notification=true"
            if reply_to_msg_id is not None:
                url += f"&reply_to_message_id={reply_to_msg_id}"
            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.Timeout:
                logger.warning("Telegram send message timeout")
                return False
            responses_oks.append(response.json().get("ok", False))
        return all(responses_oks)

    def _split_long_text(self, text: str) -> list[str]:
        lines = text.split("\n")
        messages = []
        current_message = ""
        for line in lines:
            while len(line) > self.MAX_MESSAGE_LENGTH:
                messages.append(line[: self.MAX_MESSAGE_LENGTH])
                line = line[self.MAX_MESSAGE_LENGTH :]  # noqa: PLW2901 (loop variable overwritten)
            if len(current_message + line) > self.MAX_MESSAGE_LENGTH:
                messages.append(current_message)
                current_message = line + "\n"
            else:
                current_message += line + "\n"
        if current_message:
            messages.append(current_message)
        return messages
