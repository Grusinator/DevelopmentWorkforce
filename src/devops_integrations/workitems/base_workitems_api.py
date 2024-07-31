from abc import ABC, abstractmethod
from typing import List
from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInput, WorkItem, UpdateWorkItemInput, \
    WorkItemCommentModel


class BaseWorkitemsApi(ABC):
    @abstractmethod
    def create_work_item(self, work_item: CreateWorkItemInput) -> int:
        pass

    @abstractmethod
    def get_work_item(self, work_item_id: int) -> WorkItem:
        pass

    @abstractmethod
    def update_work_item(self, updates: UpdateWorkItemInput) -> None:
        pass

    @abstractmethod
    def delete_work_item(self, work_item_id: int) -> None:
        pass

    @abstractmethod
    def list_work_items(self, work_item_type: str = None, assigned_to: str = None, state: str = None) -> List[WorkItem]:
        pass

    @abstractmethod
    def list_comments(self, work_item_id: int) -> List[WorkItemCommentModel]:
        pass

    @abstractmethod
    def create_comment(self, work_item_id: int, text: str) -> WorkItemCommentModel:
        pass

    @abstractmethod
    def update_workitem_state(self, work_item_id: int, new_state: str) -> None:
        pass

    @abstractmethod
    def set_workitem_relationship(self, source_id: int, target_id: int, relationship: str) -> None:
        pass

    @abstractmethod
    def get_workitem_url(self, work_item_id: int = None, wiql: bool = False) -> str:
        pass
