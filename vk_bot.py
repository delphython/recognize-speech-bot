import logging
import os

import vk_api as vk

from dotenv import load_dotenv
from telegram import Bot
from vk_api.longpoll import VkLongPoll, VkEventType

from tg_log_handler import TelegramLogsHandler
from dialog_flow import detect_intent_texts

logger = logging.getLogger(__name__)


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
    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info("VK бот запущен!")

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    try:
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                dialogflow_query_result = detect_intent_texts(
                    project_id, sesion_id, event.text
                )
                if not dialogflow_query_result.intent.is_fallback:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=dialogflow_query_result.fulfillment_text,
                        random_id=0,
                    )
    except Exception as err:
        logger.exception(f"VK бот упал с ошибкой: {err}")


if __name__ == "__main__":
    main()
