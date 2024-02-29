from flask import Flask, request, jsonify
import os

from routes.audio_logs import audio_log_bp
from routes.things import thing_bp
from dotenv import load_dotenv

from utils.s3_utils import generate_presigned_upload_url
from utils.celery_utils import configure_celery
from utils.extensions import db, ma, celery

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db.init_app(app)
ma.init_app(app)
configure_celery(app, celery)

app.register_blueprint(thing_bp, url_prefix='/api/things')
app.register_blueprint(audio_log_bp, url_prefix='/api/audio_logs')

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World'


@app.route('/api/generate_presigned_url', methods=['POST'])
def generate_presigned_url():
    file_name = request.json['file_name']
    file_type = request.json['file_type']

    url = generate_presigned_upload_url(file_name, file_type)
    return jsonify({'url': url})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=os.getenv("PORT", default=5003))
