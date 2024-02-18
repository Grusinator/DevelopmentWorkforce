from typing import List

from ado_integrations.ado_models import AdoWorkItem
from ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi


class MockAdoWorkitemsApi(BaseAdoWorkitemsApi):
    def __init__(self):
        self.work_items = []

    def create_work_item(self, work_item: AdoWorkItem) -> int:
        self.work_items.append(work_item)
        return work_item.id

    def get_work_item(self, work_item_id: int) -> AdoWorkItem:
        for work_item in self.work_items:
            if work_item.id == work_item_id:
                return work_item
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def update_work_item(self, work_item_id: int, updated_work_item: AdoWorkItem) -> None:
        for i, work_item in enumerate(self.work_items):
            if work_item.id == work_item_id:
                self.work_items[i] = updated_work_item
                return
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def delete_work_item(self, work_item_id: int) -> None:
        for i, work_item in enumerate(self.work_items):
            if work_item.id == work_item_id:
                del self.work_items[i]
                return
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def list_work_items(self, work_item_type: str = None, assigned_to: str = None) -> List[AdoWorkItem]:
        filtered_work_items = self.work_items
        if work_item_type:
            filtered_work_items = [work_item for work_item in filtered_work_items if work_item.type == work_item_type]
        if assigned_to:
            filtered_work_items = [work_item for work_item in filtered_work_items if work_item.assigned_to == assigned_to]
        return filtered_work_items


