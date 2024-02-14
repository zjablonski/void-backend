from flask import Flask, render_template, request, redirect, session
import os
from test_transcription import transcribe_audio_from_base64
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World'

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():  # put application's code here
    transcription = transcribe_audio_from_base64(request.json['audio'])
    print(transcription)
    return transcription

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


