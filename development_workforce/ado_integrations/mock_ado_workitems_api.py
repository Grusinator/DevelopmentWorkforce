from typing import List

from development_workforce.ado_integrations.ado_models import AdoWorkItem, CreateWorkItemInput, UpdateWorkItemInput
from development_workforce.ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi


class MockAdoWorkitemsApi(BaseAdoWorkitemsApi):
    def __init__(self):
        self.work_items = []

    def create_work_item(self, work_item: CreateWorkItemInput) -> int:
        next_id = max([work_item.id for work_item in self.work_items], default=0) + 1
        work_item_w_new_id = AdoWorkItem(id=next_id, **work_item.model_dump())
        self.work_items.append(work_item_w_new_id)
        return work_item_w_new_id.id

    def get_work_item(self, work_item_id: int) -> AdoWorkItem:
        for work_item in self.work_items:
            if work_item.id == work_item_id:
                return work_item
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def update_work_item_description(self, updated_work_item: UpdateWorkItemInput) -> int:
        for i, work_item in enumerate(self.work_items):
            if work_item.id == updated_work_item.id:
                self.work_items[i] = self._update_work_item_fields(work_item, updated_work_item.model_dump())
                return updated_work_item.id
        raise ValueError(f"Work item with ID {updated_work_item.id} not found.")

    def _update_work_item_fields(self, work_item: AdoWorkItem, updated_fields: dict) -> AdoWorkItem:
        for key, value in updated_fields.items():
            setattr(work_item, key, value)
        return work_item

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


