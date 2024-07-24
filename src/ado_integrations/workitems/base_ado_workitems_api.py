from abc import ABC, abstractmethod
from typing import List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ado_integrations.workitems.ado_workitem_models import WorkItem, CreateWorkItemInput, UpdateWorkItemInput


class BaseAdoWorkitemsApi(ABC):
    @abstractmethod
    def create_work_item(self, work_item: "CreateWorkItemInput") -> int:
        pass

    @abstractmethod
    def get_work_item(self, work_item_id: int) -> "WorkItem":
        pass

    @abstractmethod
    def update_work_item(self, updated_work_item: "UpdateWorkItemInput") -> int:
        pass

    @abstractmethod
    def delete_work_item(self, work_item_id: int) -> None:
        pass

    @abstractmethod
    def list_work_items(self, work_item_type: str = None, assigned_to: str = None) -> List["WorkItem"]:
        pass
