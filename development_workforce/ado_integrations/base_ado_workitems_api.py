from abc import ABC, abstractmethod
from typing import List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from development_workforce.ado_integrations.ado_models import AdoWorkItem, CreateWorkItemInput

class BaseAdoWorkitemsApi(ABC):
    @abstractmethod
    def create_work_item(self, work_item: "CreateWorkItemInput") -> int:
        pass

    @abstractmethod
    def get_work_item(self, work_item_id: int) -> "AdoWorkItem":
        pass

    @abstractmethod
    def update_work_item(self, work_item_id: int, updated_work_item: "AdoWorkItem") -> None:
        pass

    @abstractmethod
    def delete_work_item(self, work_item_id: int) -> None:
        pass

    @abstractmethod
    def list_work_items(self, work_item_type: str = None, assigned_to: str = None) -> List["AdoWorkItem"]:
        pass
