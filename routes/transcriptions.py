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
from utils.inference import run_inference, ModelTypes
from utils.tasks import run_shallow_analysis, run_deep_analysis
from dotenv import load_dotenv
from utils.tasks import add_together

load_dotenv()
transcription_bp = Blueprint('transcription_bp', __name__)


# Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

s3_client = boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))


@transcription_bp.route('/generate_presigned_url', methods=['POST'])
def generate_presigned_url():
    file_name = request.json['file_name']
    file_type = request.json['file_type']

    presigned_url = s3_client.generate_presigned_url('put_object',
                                                     Params={'Bucket': S3_BUCKET,
                                                             'Key': file_name,
                                                             'ContentType': file_type},
                                                     ExpiresIn=3600)
    return jsonify({'url': presigned_url})


@transcription_bp.route('/transcription/<int:transcription_id>', methods=['GET'])
def get_transcription(transcription_id):
    thing = Transcription.query.get_or_404(transcription_id)
    return TranscriptionSchema().dump(thing)


@transcription_bp.route('/transcription', methods=['POST'])
def create_transcription():  # put application's code here
    file_name = request.json['file_name']
    audio_url = s3_client.generate_presigned_url('get_object',
                                                 Params={'Bucket': S3_BUCKET,
                                                         'Key': file_name},
                                                 ExpiresIn=3600)

    config = aai.TranscriptionConfig().set_webhook(f"{os.getenv('API_URL')}/api/finalize_transcription")
    aai_result = aai.Transcriber().submit(audio_url, config)
    transcription = Transcription(file_name=file_name,
                                  status="processing",
                                  assemblyai_id=aai_result.id)
    db.session.add(transcription)
    db.session.commit()

    return jsonify(TranscriptionSchema().dump(transcription)), 201


@transcription_bp.route('/finalize_transcription', methods=['POST'])
def finalize_transcription():  # put application's code here
    transcription_id = request.json['transcript_id']
    aai_result = aai.Transcript.get_by_id(transcription_id)

    # TODO: make status an enum
    # TODO: pass assemblyai our id directly. Validate that the transcription was a success.
    transcription = Transcription.query.filter_by(assemblyai_id=transcription_id).first()
    transcription.status = "transcribed"
    transcription.text = aai_result.text
    db.session.commit()

    if transcription.text:
        run_shallow_analysis.delay(transcription.id)
        run_deep_analysis.delay(transcription.id)

    return "Success", 200

