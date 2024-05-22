import json

from db.models import AudioLog, Category, Event, Thing, Thought
from db.schemas import ThingListSchema
from utils.extensions import celery, db
from utils.inference import ModelTypes, run_inference
from utils.prompts import VOID_BIG_BRAIN_PROMPT, VOID_SMOL_BRAIN_PROMPT


@celery.task
def run_shallow_analysis(log_id):
    audio_log = AudioLog.query.get(log_id)
    user_id = str(audio_log.user_id)
    all_things = Thing.query.filter_by(user_id=user_id).all()

    try:
        raw_analysis = run_inference(
            ModelTypes.GPT4_TURBO.value,
            VOID_SMOL_BRAIN_PROMPT,
            json.dumps(
                {
                    "things": ThingListSchema(many=True).dump(all_things),
                    "text": audio_log.text,
                }
            ),
        )
        audio_log.raw_shallow_analysis = raw_analysis
        audio_log.identified_things = raw_analysis["identified_things"]
    except Exception as ex:
        audio_log.system_notes += f"\nError parsing identified_things: {ex}"

    db.session.commit()


@celery.task
def run_deep_analysis(log_id):
    audio_log = AudioLog.query.get(log_id)
    user_id = str(audio_log.user_id)
    all_things = Thing.query.filter_by(user_id=user_id).all()
    thing_ids = [thing.id for thing in all_things]
    thing_names = [thing.name.lower().strip() for thing in all_things]

    try:
        raw_analysis = run_inference(
            ModelTypes.GPT4_TURBO.value,
            VOID_BIG_BRAIN_PROMPT,
            json.dumps(
                {
                    "things": ThingListSchema(many=True).dump(all_things),
                    "text": audio_log.text,
                }
            ),
        )

        audio_log.raw_deep_analysis = raw_analysis
        db.session.commit()

        thoughts = []
        for thought in raw_analysis.get("thoughts", []):
            thoughts.append(
                Thought(
                    audio_log_id=audio_log.id, text=thought, user_id=audio_log.user_id
                )
            )

        db.session.add_all(thoughts)

        events = []
        for event in raw_analysis.get("events", []):
            thing_id = event.get("thing_id")
            thing = None
            if thing_id is None:
                # Suggested Thing by AI
                suggested_thing_name = event.get("suggested_thing_name")
                suggested_unit = event.get("suggested_unit")
                suggested_category = event.get("suggested_category")

                if suggested_category not in Category.list():
                    suggested_category = Category.Other.value

                if suggested_thing_name:
                    if suggested_thing_name.lower().strip() not in thing_names:
                        thing = Thing(
                            name=suggested_thing_name,
                            unit=suggested_unit,
                            user_id=user_id,
                            category=suggested_category,
                        )
                        db.session.add(thing)
                        db.session.commit()
                    else:
                        thing = Thing.query.filter_by(
                            name=suggested_thing_name, user_id=user_id
                        ).first()
            else:
                # Thing already exists
                if thing_id in thing_ids:
                    thing = Thing.query.get(thing_id)
            if thing:
                # if processing for thing went wrong, ignore event
                events.append(
                    Event(
                        audio_log_id=audio_log.id,
                        amount=event.get("amount"),
                        note=event.get("note"),
                        thing_id=thing.id,
                        user_id=audio_log.user_id,
                    )
                )

            db.session.add_all(events)

    except Exception as ex:
        audio_log.system_notes += f"\nError parsing events: {ex}"

    audio_log.is_processing_complete = True
    db.session.commit()
