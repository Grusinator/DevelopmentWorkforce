from abc import ABC, abstractmethod


class TaskUpdaterBase(ABC):
    @abstractmethod
    def start_agent_task(self, work_item_id=None, pull_request_id=None, status='pending') -> object:
        pass

    @abstractmethod
    def end_agent_task(self, agent_task_id: object, status=None, token_usage=None, pull_request_id=None):
        pass
