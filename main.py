from flask import Flask
import os

from routes.transcriptions import transcription_bp
from routes.things import thing_bp
from dotenv import load_dotenv

from utils.celery_utils import configure_celery
from utils.extensions import db, ma, celery

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db.init_app(app)
ma.init_app(app)
configure_celery(app, celery)

app.register_blueprint(thing_bp, url_prefix='/api')
app.register_blueprint(transcription_bp, url_prefix='/api')

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World'


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=os.getenv("PORT", default=5003))
