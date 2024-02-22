import json
from threading import Thread

from flask import Blueprint, jsonify, request
import assemblyai as aai
import boto3
import os
from utils.extensions import db
from utils.prompts import VOID_BIG_BRAIN_PROMPT, VOID_SMOL_BRAIN_PROMPT
from models import Thing, Transcription
from schemas import ThingSchema, TranscriptionSchema
from utils.inference import run_inference, ModelTypes, run_shallow_analysis, run_deep_analysis
from utils.transcription import transcribe_audio_from_base64
from dotenv import load_dotenv

load_dotenv()
events_bp = Blueprint('events_bp', __name__)


# Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

s3_client = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))


@events_bp.route('/generate_presigned_url', methods=['POST'])
def generate_presigned_url():
    file_name = request.json['file_name']
    file_type = request.json['file_type']

    presigned_url = s3_client.generate_presigned_url('put_object',
                                                     Params={'Bucket': S3_BUCKET,
                                                             'Key': file_name,
                                                             'ContentType': file_type},
                                                     ExpiresIn=3600)
    return jsonify({'url': presigned_url})


@events_bp.route('/find_things', methods=['POST'])
def find_things():
    transcription = request.json['transcription']
    # run through openai to generate events
    all_things = Thing.query.all()
    output = run_inference(ModelTypes.GPT3_5_TURBO.value, VOID_SMOL_BRAIN_PROMPT, json.dumps({
        "things": [thing.name for thing in all_things],
        "text": transcription
    }))
    identified_things = output.get("identified_things", [])
    return jsonify(identified_things)


@events_bp.route('/generate_events', methods=['POST'])
def generate_events():  # put application's code here
    transcription = request.json['transcription']
    # run through openai to generate events
    all_things = Thing.query.all()
    events = run_inference(ModelTypes.GPT4_TURBO.value, VOID_BIG_BRAIN_PROMPT, json.dumps({
        "things": ThingSchema(many=True).dump(all_things),
        "text": transcription
    }))
    print(events)
    return events


@events_bp.route('/transcription', methods=['POST'])
def create_transcription():  # put application's code here
    file_name = request.json['file_name']
    audio_url = s3_client.generate_presigned_url('get_object',
                                                 Params={'Bucket': S3_BUCKET,
                                                         'Key': file_name},
                                                 ExpiresIn=3600)

    config = aai.TranscriptionConfig().set_webhook(f"{os.getenv('NGROK_URL')}/api/finalize_transcription")
    aai_result = aai.Transcriber().submit(audio_url, config)
    transcription = Transcription(file_name=file_name, status="processing", assemblyai_id=aai_result.id)
    db.session.add(transcription)
    db.session.commit()
    return jsonify(TranscriptionSchema().dump(transcription)), 201


@events_bp.route('/finalize_transcription', methods=['POST'])
def finalize_transcription():  # put application's code here
    transcription_id = request.json['transcript_id']
    aai_result = aai.Transcript.get_by_id(transcription_id)

    transcription = Transcription.query.filter_by(assemblyai_id=transcription_id).first()
    transcription.status = "complete"
    transcription.text = aai_result.text

    db.session.commit()
    run_shallow_analysis(transcription.id)
    run_deep_analysis(transcription.id)
    # Thread(target=run_shallow_analysis, args=(transcription_id,)).start()
    # Thread(target=long_running_task_2).start()

    return "Success", 200



