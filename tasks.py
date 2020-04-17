from celery import Celery
from celery.schedules import crontab

from webapp import create_app
from webapp.advert.parsers import avito

flask_app = create_app()
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def advert_snippets():
    with flask_app.app_context():
        avito.get_adverts_snippets()

@celery_app.task
def advert_content():
    with flask_app.app_context():
        avito.get_adverts_content()

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.app_periodic_task(crontab(minute='*/1'), advert_snippets.s())
    sender.app_periodic_task(crontab(minute='*/1'), advert_content.s())

