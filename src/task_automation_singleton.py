# myapp/task_manager_singleton.py
import os
from threading import Lock
from .task_listener import TaskAutomation
import loguru


class TaskAutomationSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(TaskAutomationSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, repo_url, ado_org_name, project_name, pat, user_name):
        if not self._initialized:
            self.task_automation = TaskAutomation(repo_url, ado_org_name, project_name, pat, user_name)
            self._initialized = True

    def start(self):
        loguru.logger.info("Starting TaskAutomation...")
        self.task_automation.start()

    def stop(self):
        loguru.logger.info("Stopping TaskAutomation...")
        self.task_automation.stop()

    def is_running(self):
        return self.task_automation.running
