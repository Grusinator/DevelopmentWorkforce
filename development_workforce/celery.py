import os
from typing import Callable, Dict, Any

from celery import Celery, signals
from django_extensions import settings
from loguru import logger

from functools import wraps
from django.db import connection

def close_old_connections(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        connection.close_if_unusable_or_obsolete()
        try:
            return f(*args, **kwargs)
        finally:
            connection.close_if_unusable_or_obsolete()
    return wrapper


from celery import Celery
from django.db import connection

class CustomCelery(Celery):
    def on_task_prerun(self, *args, **kwargs):
        connection.close_if_unusable_or_obsolete()

    def on_task_postrun(self, *args, **kwargs):
        connection.close_if_unusable_or_obsolete()

class CeleryWorker:
    def __init__(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'development_workforce.settings')
        self.app = Celery('development_workforce')
        self.tasks = {}  # Dictionary to keep track of registered tasks
        self._configure()

    def _configure(self):
        # Load configuration from Django settings
        self.app.config_from_object('django.conf:settings', namespace='CELERY')
        logger.info(f"Celery backend configuration: {self.app.conf.CELERY_RESULT_BACKEND}")
        self.app.autodiscover_tasks()
        self.show_discovered_tasks()

    def show_discovered_tasks(self):
        logger.debug("Discovered tasks:")
        for task_name in self.app.tasks.keys():
            logger.debug(f"- {task_name}")

    def setup_cron_job(self, beat_schedule_name, task_name, schedule):
        """Set up a periodic task using the provided schedule."""
        self.app.conf.beat_schedule[beat_schedule_name] = {"task": task_name, "schedule": schedule}

    def schedule_task(self, task_name, task_id, *args, **kwargs):
        """Queue a task for execution using apply_async."""
        if task_name in self.tasks:
            task = self.tasks[task_name]
            # For some strange reason i cant make send task, trigger a signal when done.
            return task.apply_async(task_id=task_id, args=args, kwargs=kwargs)
        else:
            raise ValueError(f"Task {task_name} is not registered.")

    def get_task_result(self, task_id):
        """Fetch the result of a task."""
        return self.app.AsyncResult(str(task_id)).result

    def connect_task_success_signals(self, handler):
        """Connect the task success signal to the provided handler."""
        signals.task_success.connect(handler)

    def connect_task_prerun_signals(self, handler):
        """Connect the task success signal to the provided handler."""
        signals.task_prerun.connect(handler)

    def register_task(self, task_function, task_name=None):
        """Register a task dynamically with Celery."""
        task_name = task_name or task_function.__name__
        task = self.app.task(task_function, name=task_name)
        self.tasks[task_name] = task  # Keep track of the task
        logger.info(f"Task {task_name} registered.")
        return task

    @property
    def celery_app(self):
        return self.app


# Initialize CeleryWorker and expose the app globally
celery_worker = CeleryWorker()
app = celery_worker.celery_app

app.conf.update(
    worker_pool='solo',
    worker_concurrency=1,
)


