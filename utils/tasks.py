import json

from models import Thing, Transcription
from schemas import ThingSchema
from utils.extensions import db, celery
from utils.inference import run_inference, ModelTypes
from utils.prompts import VOID_BIG_BRAIN_PROMPT, VOID_SMOL_BRAIN_PROMPT


@celery.task
def add_together(a, b):
    print("hereee")
    print(a + b)
    return a + b


@celery.task
def run_shallow_analysis(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    all_things = Thing.query.all()
    events = run_inference(ModelTypes.GPT4_TURBO.value, VOID_SMOL_BRAIN_PROMPT, json.dumps({
        "things": ThingSchema(many=True).dump(all_things),
        "text": transcription.text
    }))
    transcription.shallow_analysis = events
    db.session.commit()

@celery.task
def run_deep_analysis(transcription_id):
    transcription = Transcription.query.get(transcription_id)
    all_things = Thing.query.all()
    events = run_inference(ModelTypes.GPT4_TURBO.value, VOID_BIG_BRAIN_PROMPT, json.dumps({
        "things": ThingSchema(many=True).dump(all_things),
        "text": transcription.text
    }))
    transcription.status = "complete"
    transcription.deep_analysis = events
    db.session.commit()