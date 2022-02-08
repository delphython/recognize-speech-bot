import json
import os

from dotenv import load_dotenv
from google.cloud import dialogflow


def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def main():
    load_dotenv()

    google_app_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_app_credentials

    project_id = os.getenv("PROJECT_ID")

    training_phrases_file = "training_phrases.json"

    with open(training_phrases_file, "r", encoding="utf-8") as file:
        training_phrases = json.load(file)

    for intent_name, questions_and_answer in training_phrases.items():
        create_intent(
            project_id,
            intent_name,
            questions_and_answer["questions"],
            [questions_and_answer["answer"]],
        )


if __name__ == "__main__":
    main()
