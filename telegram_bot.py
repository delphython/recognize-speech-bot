import logging
import os

from dotenv import load_dotenv
from telegram import Update, ForceReply, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from helper import TelegramLogsHandler, detect_intent_texts


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Здравствуйте {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


def responds_to_messages(update: Update, context: CallbackContext):
    reply_message = detect_intent_texts(
        context.bot_data["project_id"],
        context.bot_data["sesion_id"],
        update.message.text,
    )
    update.message.reply_text(
        "Бот не смог распознать фразу."
    ) if not reply_message else update.message.reply_text(reply_message)


def main():
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    sesion_id = os.getenv("SESSION_ID")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    bot_data = {
        "project_id": project_id,
        "sesion_id": sesion_id,
    }

    bot = Bot(token=telegram_token)

    logging.basicConfig(format="%(levelname)s %(message)s")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info("Telegram бот запущен!")

    try:
        updater = Updater(telegram_token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))

        dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command, responds_to_messages
            )
        )

        dispatcher.bot_data = bot_data

        updater.start_polling()

        updater.idle()
    except Exception as err:
        logger.exception(f"Telegram бот упал с ошибкой: {err}")


if __name__ == "__main__":
    main()
