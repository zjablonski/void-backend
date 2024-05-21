import assemblyai as aai
import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from db.models import AudioLog, AudioLogStatus
from db.schemas import AudioLogListSchema, AudioLogSchema, EventSchema, ThoughtsSchema
from utils.extensions import db
from utils.s3_utils import generate_presigned_fetch_url
from utils.tasks import run_deep_analysis, run_shallow_analysis

# Configuration
load_dotenv()
audio_log_bp = Blueprint("audio_log_bp", __name__)
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")


@audio_log_bp.before_request
@jwt_required()
def require_jwt():
    g.user_id = get_jwt_identity()


@audio_log_bp.route("/<int:log_id>", methods=["GET"])
def get_audio_log(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return AudioLogSchema().dump(audio_log)


@audio_log_bp.route("/", methods=["GET"])
def get_audio_logs():
    audio_log = AudioLog.all()
    return AudioLogListSchema().dump(audio_log, many=True)


@audio_log_bp.route("/", methods=["POST"])
def create_audio_log():
    file_name = request.json["file_name"]
    audio_url = generate_presigned_fetch_url(file_name)

    audio_log = AudioLog(
        file_name=file_name,
        status="processing",
        user_id=g.user_id,
    )
    db.session.add(audio_log)
    db.session.commit()

    # generate a short-term token for AAI
    token = create_access_token(
        identity=str(g.user_id), expires_delta=timedelta(hours=1)
    )
    config = aai.TranscriptionConfig().set_webhook(
        f"{os.getenv('API_URL')}/api/audio_logs/{audio_log.id}/update_transcription",
        "Authorization",
        f"Bearer {token}",
    )
    aai_result = aai.Transcriber().submit(audio_url, config)

    audio_log.assemblyai_id = aai_result.id
    db.session.add(audio_log)
    db.session.commit()

    return jsonify(AudioLogSchema().dump(audio_log)), 201


@audio_log_bp.route("/<int:log_id>/update_transcription", methods=["POST"])
def update_transcription(log_id):  # put application's code here
    audio_log = AudioLog.get_or_404(log_id)
    transcription_id = request.json["transcript_id"]
    aai_result = aai.Transcript.get_by_id(transcription_id)
    print("Here", aai_result.text)

    if audio_log.assemblyai_id != transcription_id:
        return "permission denied", 403

    audio_log.text = aai_result.text
    db.session.commit()

    if audio_log.text:
        run_deep_analysis.delay(audio_log.id)
        run_shallow_analysis.delay(audio_log.id)
    else:
        audio_log.is_processing_complete = True
        db.session.commit()

    return "Success", 200


@audio_log_bp.route("/<int:log_id>/approve", methods=["POST"])
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


@audio_log_bp.route("/<int:log_id>/thoughts", methods=["GET"])
def get_audio_log_thoughts(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return ThoughtsSchema().dump(audio_log.thoughts, many=True)


@audio_log_bp.route("/<int:log_id>/events", methods=["GET"])
def get_audio_log_events(log_id):
    audio_log = AudioLog.get_or_404(log_id)
    return EventSchema().dump(audio_log.events, many=True)
