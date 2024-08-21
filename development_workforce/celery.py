import os

from celery import Celery, signals
from loguru import logger


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
        logger.info("Discovered tasks:")
        for task_name in self.app.tasks.keys():
            logger.info(f"- {task_name}")

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

    def connect_task_signals(self, handler):
        """Connect the task success signal to the provided handler."""
        signals.task_success.connect(handler)

    def register_task(self, task_name, task_function):
        """Register a task dynamically with Celery."""
        task = self.app.task(task_function, name=task_name)
        self.tasks[task_name] = task  # Keep track of the task
        logger.info(f"Task {task_name} registered.")
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


