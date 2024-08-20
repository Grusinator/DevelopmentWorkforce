import os
from celery import Celery
from celery.schedules import crontab


class CeleryWorker:
    def __init__(self):
        self.app = Celery('development_workforce')
        self._configure()

    def _configure(self):
        # Load configuration from Django settings
        self.app.config_from_object('django.conf:settings', namespace='CELERY')

        # Set broker and backend URLs from environment variables
        broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

        self.app.conf.broker_url = broker_url
        self.app.conf.result_backend = result_backend

        # Optional: Load task schedule (can be moved to Django settings if preferred)
        self.app.conf.beat_schedule = {
            'fetch-new-workitems-every-5-minutes': {
                'task': 'fetch_new_tasks_periodically',
                'schedule': crontab(minute='*/5'),  # Fetch every 5 minutes
            },
        }

        # Autodiscover tasks across installed apps
        self.app.autodiscover_tasks()

    def add_task(self, task_name, *args, **kwargs):
        """Queue a task for execution."""
        return self.app.send_task(task_name, args=args, kwargs=kwargs)

    def get_task_result(self, task_id):
        """Fetch the result of a task."""
        return self.app.AsyncResult(task_id).result

    @property
    def celery_app(self):
        return self.app


# Initialize CeleryWorker and expose the app globally
celery_worker = CeleryWorker()
app = celery_worker.celery_app
