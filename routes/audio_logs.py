from flask import Blueprint, jsonify, request, g
import assemblyai as aai
import os

from flask_jwt_extended import jwt_required, get_jwt_identity

from utils.s3_utils import generate_presigned_fetch_url
from utils.extensions import db
from models import AudioLog, Thing, Thought, Event, AudioLogStatus
from schemas import AudioLogSchema, EventSchema, ThoughtsSchema, AudioLogListSchema
from utils.tasks import run_shallow_analysis, run_deep_analysis
from dotenv import load_dotenv

# Configuration
load_dotenv()
audio_log_bp = Blueprint('audio_log_bp', __name__)
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


@audio_log_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


@audio_log_bp.route('/<int:log_id>', methods=['GET'])
def get_audio_log(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return AudioLogSchema().dump(audio_log)


@audio_log_bp.route('/', methods=['GET'])
def get_audio_logs():
    audio_log = AudioLog.all()
    return AudioLogListSchema().dump(audio_log, many=True)


@audio_log_bp.route('/', methods=['POST'])
def create_audio_log():  # put application's code here
    file_name = request.json['file_name']
    audio_url = generate_presigned_fetch_url(file_name)

    config = aai.TranscriptionConfig().set_webhook(f"{os.getenv('API_URL')}/api/audio_logs/update_transcription")
    aai_result = aai.Transcriber().submit(audio_url, config)
    audio_log = AudioLog(file_name=file_name,
                         status="processing",
                         user_id=g.user_id,
                         assemblyai_id=aai_result.id)
    db.session.add(audio_log)
    db.session.commit()

    return jsonify(AudioLogSchema().dump(audio_log)), 201


@audio_log_bp.route('/update_transcription', methods=['POST'])
def update_transcription():  # put application's code here
    transcription_id = request.json['transcript_id']
    aai_result = aai.Transcript.get_by_id(transcription_id)

    # TODO: PASS AN AUTH HEADER TO ASSEMBLYAI & LOCK THIS ROUTE DOWN
    # TODO: pass assemblyai our id directly. Validate that the transcription was a success.
    audio_log = AudioLog.query.filter_by(assemblyai_id=transcription_id).first()
    audio_log.text = aai_result.text
    db.session.commit()

    if audio_log.text:
        run_deep_analysis.delay(audio_log.id)
        run_shallow_analysis.delay(audio_log.id)

    return "Success", 200


@audio_log_bp.route('/<int:log_id>/approve', methods=['POST'])
def approve_audio_log(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    audio_log.status = AudioLogStatus.APPROVED.value

    for event in audio_log.events:
        event.thing.status = "APPROVED"
        event.is_active = True

    for thought in audio_log.thoughts:
        thought.is_active = True

    db.session.commit()
    return "Success", 200


@audio_log_bp.route('/<int:log_id>/thoughts', methods=['GET'])
def get_audio_log_thoughts(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return ThoughtsSchema().dump(audio_log.thoughts, many=True)


@audio_log_bp.route('/<int:log_id>/events', methods=['GET'])
def get_audio_log_events(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return EventSchema().dump(audio_log.events, many=True)
