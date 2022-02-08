import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update, ForceReply, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)


logger = logging.getLogger(__name__)


class TelegramLogsHandler(logging.Handler):
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

    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Здравствуйте {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


def echo(update: Update, context: CallbackContext):
    reply_message = detect_intent_texts(
        project_id, sesion_id, update.message.text
    )
    update.message.reply_text(reply_message)


def main():
    load_dotenv()

    global project_id
    global sesion_id

    project_id = os.getenv("PROJECT_ID")
    sesion_id = os.getenv("SESSION_ID")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    bot = Bot(token=telegram_token)

    logging.basicConfig(format="%(levelname)s %(message)s")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info("Бот запущен!")

    try:
        updater = Updater(telegram_token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))

        dispatcher.add_handler(
            MessageHandler(Filters.text & ~Filters.command, echo)
        )

        updater.start_polling()

        updater.idle()
    except Exception as err:
        logger.exception(f"Бот упал с ошибкой: {err}")


if __name__ == "__main__":
    main()
