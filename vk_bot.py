import logging
import os
import random

import vk_api as vk

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Bot
from vk_api.longpoll import VkLongPoll, VkEventType


logger = logging.getLogger(__name__)


class VKLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(project_id, session_id, text, language_code="ru"):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    if response.query_result.intent.is_fallback:
        return None
    else:
        return response.query_result.fulfillment_text


def main():
    load_dotenv()

    vk_token = os.getenv("VK_TOKEN")
    project_id = os.getenv("PROJECT_ID")
    sesion_id = os.getenv("SESSION_ID")
    chat_id = os.getenv("CHAT_ID")
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    bot = Bot(token=telegram_token)

    logging.basicConfig(format="%(levelname)s %(message)s")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(VKLogsHandler(bot, chat_id))
    logger.info("VK бот запущен!")

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    try:
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                reply_message = detect_intent_texts(
                    project_id, sesion_id, event.text
                )
                vk_api.messages.send(
                    user_id=event.user_id, message=reply_message, random_id=0
                )
    except Exception as err:
        logger.exception(f"VK бот упал с ошибкой: {err}")


if __name__ == "__main__":
    main()
