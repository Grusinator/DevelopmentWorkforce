import os
from celery import Celery, signals
from celery.schedules import crontab


class CeleryWorker:
    def __init__(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'development_workforce.settings')
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

    def add_task(self, task_name, task_id, *args, **kwargs):
        """Queue a task for execution."""
        return self.app.send_task(task_name, task_id=task_id, args=args, kwargs=kwargs)

    def get_task_result(self, task_id):
        """Fetch the result of a task."""
        return self.app.AsyncResult(task_id).result

    def connect_task_signals(self, handler):
        """Connect the task success signal to the provided handler."""
        signals.task_success.connect(handler)

    def register_task(self, task_name, task_function):
        """Register a task dynamically with Celery."""
        task = self.app.task(task_function, name=task_name)
        return task

    def register_tasks(self, tasks):
        """Register multiple tasks."""
        for task_name, task_function in tasks.items():
            self.register_task(task_name, task_function)

    @property
    def celery_app(self):
        return self.app


# Initialize CeleryWorker and expose the app globally
celery_worker = CeleryWorker()
app = celery_worker.celery_app
