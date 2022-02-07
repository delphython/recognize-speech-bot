import json
import os

from dotenv import load_dotenv
from google.cloud import dialogflow


os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "C:\\PythonProjects\\recognize-speech-bot\\pelagic-berm-340508-a69ce9c87cda.json"


def create_intent(
    project_id, display_name, training_phrases_parts, message_texts
):
    """Create an intent of the given intent type."""

    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        # Here we create a new training phrase for each provided part.
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

    project_id = os.getenv("PROJECT_ID")

    training_phrases_file = "training_phrases.json"
    # intent_name = "Как устроиться к вам на работу"

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