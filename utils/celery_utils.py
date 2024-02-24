import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()


def make_celery():
    return Celery("void-backend-celery", broker=os.getenv("CELERY_BROKER_URL"))


def configure_celery(app, celery):
    # Configure Celery to work with the Flask app context
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
