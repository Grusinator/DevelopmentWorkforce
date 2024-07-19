from enum import Enum
from typing import List
from dotenv import load_dotenv
from src.ado_integrations.ado_connection import ADOConnection
from src.ado_integrations.workitems.ado_workitem_models import AdoWorkItem, CreateWorkItemInput, UpdateWorkItemInput
from src.ado_integrations.workitems.base_ado_workitems_api import BaseAdoWorkitemsApi


class WorkItemType(Enum):
    Bug = "Bug"
    Task = "Task"
    Feature = "Feature"
    Epic = "Epic"
    UserStory = "User Story"


load_dotenv()


class ADOWorkitemsApi(ADOConnection, BaseAdoWorkitemsApi):
    api_version = "7.1-preview.3"

    def create_work_item(self, work_item: CreateWorkItemInput) -> int:
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/${{type}}?api-version={self.api_version}"
        document = [
            {"op": "add", "path": "/fields/System.Title", "value": work_item.title},
            {"op": "add", "path": "/fields/System.Description", "value": work_item.description}
        ]
        response = self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)
        return response['id']

    def get_work_item(self, work_item_id: int) -> AdoWorkItem:
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
        response = self.make_request('GET', url)
        return AdoWorkItem.from_api(response)

    def update_work_item(self, updates: UpdateWorkItemInput) -> None:
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
        document = [{"op": "replace", "path": field, "value": value} for field, value in updates.items()]
        self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)

    def delete_work_item(self, work_item_id: int) -> None:
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
        self.make_request('DELETE', url)

    def list_work_items(self, work_item_type: str = None, assigned_to: str = None) -> List[AdoWorkItem]:
        query = "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.WorkItemType], [System.Description] FROM WorkItems"
        conditions = []
        if work_item_type:
            conditions.append(f"[System.WorkItemType] = '{work_item_type}'")
        if assigned_to:
            conditions.append(f"[System.AssignedTo] = '{assigned_to}'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY [System.CreatedDate] DESC"

        url = f"{self.organization_url}/{self.project_name}/_apis/wit/wiql?api-version={self.api_version}"
        response_data = self.make_request('POST', url, json={"query": query})
        work_items_ids = [item["id"] for item in response_data.get("workItems", [])]

        work_items = [self.get_work_item(work_item_id) for work_item_id in work_items_ids]
        return work_items

    def update_work_item_description(self, updated_work_item: UpdateWorkItemInput) -> int:
        if not updated_work_item.description:
            raise ValueError("Description is required to update a work item's description.")

        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{updated_work_item.id}?api-version={self.api_version}"
        document = [
            {
                "op": "replace",
                "path": "/fields/System.Description",
                "value": updated_work_item.description
            }
        ]
        response = self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)
        return response['id']

    def update_workitem_state(self, work_item_id, new_state):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
        document = [
            {
                "op": "replace",
                "path": "/fields/System.State",
                "value": new_state
            }
        ]
        self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)

    def set_workitem_relationship(self, source_id, target_id, relationship):
        url = f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{source_id}?api-version={self.api_version}"
        document = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": relationship,
                    "url": f"{self.organization_url}/{self.project_name}/_apis/wit/workitems/{target_id}"
                }
            }
        ]
        self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)
