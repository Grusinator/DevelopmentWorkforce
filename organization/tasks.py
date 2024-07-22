# tasks.py
from typing import Dict

from celery import shared_task
from loguru import logger

from src.ado_integrations.workitems.ado_workitem_models import AdoWorkItem
from src.task_listener import TaskAutomation


@shared_task
def execute_task(repo_url: str, repo_name, ado_org_name: str, project_name: str, pat: str, user_name: str, work_item: Dict):
    task = AdoWorkItem(**work_item)
    logger.debug(f"running task: {task}")
    task_automation = TaskAutomation(repo_url, repo_name, ado_org_name, project_name, pat, user_name)
    task_automation.process_task(task)
