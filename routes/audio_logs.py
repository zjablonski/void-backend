from flask import Blueprint, jsonify, request
import assemblyai as aai
import os

from utils.s3_utils import generate_presigned_fetch_url
from utils.extensions import db
from models import AudioLog, Thing, Thought, Event
from schemas import AudioLogSchema, EventSchema, ThoughtsSchema
from utils.tasks import run_shallow_analysis, run_deep_analysis
from dotenv import load_dotenv

# Configuration
load_dotenv()
audio_log_bp = Blueprint('audio_log_bp', __name__)
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


@audio_log_bp.route('/<int:log_id>', methods=['GET'])
def get_audio_log(log_id):
    audio_log = AudioLog.query.get_or_404(log_id)
    return AudioLogSchema().dump(audio_log)


@audio_log_bp.route('/', methods=['POST'])
def create_audio_log():  # put application's code here
    file_name = request.json['file_name']
    audio_url = generate_presigned_fetch_url(file_name)

    config = aai.TranscriptionConfig().set_webhook(f"{os.getenv('API_URL')}/api/audio_logs/update_transcription")
    aai_result = aai.Transcriber().submit(audio_url, config)
    audio_log = AudioLog(file_name=file_name,
                         status="processing",
                         assemblyai_id=aai_result.id)
    db.session.add(audio_log)
    db.session.commit()

    return jsonify(AudioLogSchema().dump(audio_log)), 201


@audio_log_bp.route('/update_transcription', methods=['POST'])
def finalize_audio_log():  # put application's code here
    transcription_id = request.json['transcript_id']
    aai_result = aai.Transcript.get_by_id(transcription_id)

    # TODO: make status an enum
    # TODO: pass assemblyai our id directly. Validate that the transcription was a success.
    audio_log = AudioLog.query.filter_by(assemblyai_id=transcription_id).first()
    audio_log.status = "transcribed"
    audio_log.text = aai_result.text
    db.session.commit()

    if audio_log.text:
        run_deep_analysis.delay(audio_log.id)
        run_shallow_analysis.delay(audio_log.id)

    return "Success", 200


@audio_log_bp.route('/<int:log_id>/bulk_create_events', methods=['POST'])
def bulk_create_events(log_id):
    audio_log = AudioLog.query.get_or_404(log_id)
    thoughts_data = request.json['thoughts']
    events_data = request.json['events']

    thoughts = [Thought(audio_log_id=audio_log.id, text=thought) for thought in thoughts_data]
    events = []

    for event in events_data:
        if event["thing_id"] is None:
            thing = Thing.query.filter_by(name=event["suggested_thing_name"]).first()
            if not thing:
                thing = Thing(name=event["suggested_thing_name"],
                              unit=event["suggested_unit"],
                              category=event["suggested_category"])
                db.session.add(thing)
                db.session.commit()
            event["thing_id"] = thing.id
            events.append(Event(audio_log_id=audio_log.id,
                                thing_id=thing.id,
                                amount=event["amount"],
                                note=event["note"]))


    db.session.add_all(events + thoughts)
    db.session.commit()

    return "Success", 201