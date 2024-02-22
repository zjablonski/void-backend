from enum import Enum
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

from models import Thing, Transcription
from schemas import ThingSchema
from utils.extensions import db
from utils.prompts import VOID_BIG_BRAIN_PROMPT, VOID_SMOL_BRAIN_PROMPT

load_dotenv()


openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPEN_API_KEY"),
)


class ModelTypes(Enum):
    GPT3_5_TURBO = "gpt-3.5-turbo-1106"
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"


def run_inference(model_version, system_message, user_message):
    chat_completion = openai_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        model=model_version,
        response_format={ "type": "json_object" }
    )
    events = json.loads(chat_completion.choices[0].message.content)
    return events


def run_shallow_analysis(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    all_things = Thing.query.all()
    events = run_inference(ModelTypes.GPT4_TURBO.value, VOID_SMOL_BRAIN_PROMPT, json.dumps({
        "things": ThingSchema(many=True).dump(all_things),
        "text": transcription.text
    }))

    transcription.shallow_analysis = events
    db.session.commit()

def run_deep_analysis(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    all_things = Thing.query.all()
    events = run_inference(ModelTypes.GPT4_TURBO.value, VOID_BIG_BRAIN_PROMPT, json.dumps({
        "things": ThingSchema(many=True).dump(all_things),
        "text": transcription.text
    }))

    transcription.deep_analysis = events
    db.session.commit()



