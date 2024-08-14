import os

AI_AGENT_NAME = os.getenv("AI_USER_NAME")
from datetime import datetime
from typing import List

from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel, CreateWorkItemInputModel, UpdateWorkItemInputModel, \
    WorkItemCommentModel
from src.devops_integrations.workitems.base_workitems_api import BaseWorkitemsApi


class MockWorkitemsApi(BaseWorkitemsApi):
    def __init__(self, work_items=None):
        self.work_items = work_items or []

    def create_work_item(self, work_item: CreateWorkItemInputModel) -> WorkItemModel:
        next_id = max([work_item.source_id for work_item in self.work_items], default=0) + 1
        work_item_w_new_id = WorkItemModel(source_id=next_id, **work_item.model_dump())
        self.work_items.append(work_item_w_new_id)
        return work_item_w_new_id

    def get_work_item(self, work_item_id: int) -> WorkItemModel:
        for work_item in self.work_items:
            if work_item.source_id == work_item_id:
                return work_item
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def update_work_item(self, updates: UpdateWorkItemInputModel) -> None:
        for i, work_item in enumerate(self.work_items):
            if work_item.source_id == updates.source_id:
                self.work_items[i] = self._update_work_item_fields(work_item, updates.model_dump())
                return
        raise ValueError(f"Work item with ID {updates.source_id} not found.")

    def delete_work_item(self, work_item_id: int) -> None:
        for i, work_item in enumerate(self.work_items):
            if work_item.source_id == work_item_id:
                del self.work_items[i]
                return
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def list_work_items(self, work_item_type: str = None, assigned_to: str = None, state: str = None) -> List[WorkItemModel]:
        filtered_work_items = self.work_items
        if work_item_type:
            filtered_work_items = [work_item for work_item in filtered_work_items if work_item.type == work_item_type]
        if assigned_to:
            filtered_work_items = [work_item for work_item in filtered_work_items if
                                   work_item.assigned_to == assigned_to]
        if state:
            filtered_work_items = [work_item for work_item in filtered_work_items if work_item.state == state]
        return filtered_work_items

    def list_comments(self, work_item_id: int) -> List[WorkItemCommentModel]:
        return []

    def create_comment(self, work_item_id: int, text: str) -> WorkItemCommentModel:
        return WorkItemCommentModel(id=1, text=text, created_by=AI_AGENT_NAME, created_date=datetime.now())

    def update_workitem_state(self, work_item_id: int, new_state: str) -> None:
        for work_item in self.work_items:
            if work_item.source_id == work_item_id:
                work_item.state = new_state
                return
        raise ValueError(f"Work item with ID {work_item_id} not found.")

    def set_workitem_relationship(self, source_id: int, target_id: int, relationship: str) -> None:
        pass

    def get_workitem_url(self, work_item_id: int = None, wiql: bool = False) -> str:
        return "http://mock.url/workitem"

    def _update_work_item_fields(self, work_item: WorkItemModel, updated_fields: dict) -> WorkItemModel:
        for key, value in updated_fields.items():
            if value:
                setattr(work_item, key, value)
        return work_item
