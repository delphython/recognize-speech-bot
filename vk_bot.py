import logging
import os
import random

import vk_api as vk

from dotenv import load_dotenv
from google.cloud import dialogflow
from vk_api.longpoll import VkLongPoll, VkEventType


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

    if response.query_result.intent.is_fallback:
        return None
    else:
        return response.query_result.fulfillment_text


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
    )


def main():
    load_dotenv()

    vk_token = os.getenv("VK_TOKEN")
    project_id = os.getenv("PROJECT_ID")
    sesion_id = os.getenv("SESSION_ID")

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            reply_message = detect_intent_texts(
                project_id, sesion_id, event.text
            )
            vk_api.messages.send(
                user_id=event.user_id, message=reply_message, random_id=0
            )


if __name__ == "__main__":
    main()
