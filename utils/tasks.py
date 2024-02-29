import json

from models import Thing, AudioLog
from schemas import ThingSchema
from utils.extensions import db, celery
from utils.inference import run_inference, ModelTypes
from utils.prompts import VOID_BIG_BRAIN_PROMPT, VOID_SMOL_BRAIN_PROMPT


@celery.task
def run_shallow_analysis(log_id):
    audio_log = AudioLog.query.get(log_id)
    all_things = Thing.query.all()

    try:
        raw_analysis = run_inference(ModelTypes.GPT4_TURBO.value, VOID_SMOL_BRAIN_PROMPT, json.dumps({
            "things": ThingSchema(many=True).dump(all_things),
            "text": audio_log.text
        }))
        audio_log.identified_things = raw_analysis["identified_things"]
    except Exception as ex:
        audio_log.system_notes += f"\nError parsing identified_things: {ex}"

    audio_log.raw_shallow_analysis = raw_analysis
    db.session.commit()


@celery.task
def run_deep_analysis(log_id):
    audio_log = AudioLog.query.get(log_id)
    all_things = Thing.query.all()

    status = "complete"

    try:
        raw_analysis = run_inference(ModelTypes.GPT4_TURBO.value, VOID_BIG_BRAIN_PROMPT, json.dumps({
            "things": ThingSchema(many=True).dump(all_things),
            "text": audio_log.text
        }))
        audio_log.raw_deep_analysis = raw_analysis
        audio_log.raw_events = raw_analysis["events"]
        audio_log.raw_thoughts = raw_analysis["thoughts"]
    except Exception as ex:
        audio_log.system_notes += f"\nError parsing identified_things: {ex}"
        status = "failed"

    audio_log.status = status
    db.session.commit()