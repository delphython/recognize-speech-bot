import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


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

    updater = Updater(telegram_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo)
    )

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
