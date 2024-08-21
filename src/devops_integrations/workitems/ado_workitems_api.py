from typing import List

from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation, WorkItemComment, CommentCreate
from dotenv import load_dotenv


from src.devops_integrations.ado_connection import ADOConnection
from src.devops_integrations.models import ProjectAuthenticationModel
from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel, WorkItemModel, \
    UpdateWorkItemInputModel, \
    WorkItemCommentModel, WorkItemStateEnum
from src.devops_integrations.workitems.base_workitems_api import BaseWorkitemsApi



load_dotenv()


class ADOWorkitemsApi(ADOConnection, BaseWorkitemsApi):
    api_version = "7.1-preview.3"
    STATE_MAPPER = {
        "New": WorkItemStateEnum.PENDING,
        "Active": WorkItemStateEnum.IN_PROGRESS,
        "Closed": WorkItemStateEnum.COMPLETED,
        "Resolved": WorkItemStateEnum.COMPLETED,
        "Removed": WorkItemStateEnum.FAILED,
    }

    def __init__(self, auth: ProjectAuthenticationModel):
        super().__init__(auth)

    def create_work_item(self, work_item: CreateWorkItemInputModel) -> WorkItemModel:
        document = [
            JsonPatchOperation(op='add', path='/fields/System.Title', value=work_item.title),
            JsonPatchOperation(op='add', path='/fields/System.Description', value=work_item.description),
            JsonPatchOperation(op='add', path='/fields/System.WorkItemType', value=work_item.type),
            JsonPatchOperation(op='add', path='/fields/System.AssignedTo', value=work_item.assigned_to),
            JsonPatchOperation(op='add', path='/fields/System.State', value=self._get_source_state(work_item.state)),
        ]
        created_work_item = self.wo_client.create_work_item(document, self.auth.project_name, work_item.type)
        return self._to_work_item(created_work_item)

    def get_work_item(self, work_item_id: int) -> WorkItemModel:
        work_item = self.wo_client.get_work_item(work_item_id)
        return self._to_work_item(work_item)

    def _to_work_item(self, work_item):
        return WorkItemModel(
            source_id=work_item.id,
            title=work_item.fields['System.Title'],
            type=work_item.fields['System.WorkItemType'],
            description=work_item.fields.get('System.Description', None),
            assigned_to=work_item.fields.get('System.AssignedTo', {}).get('displayName') if work_item.fields.get(
                'System.AssignedTo') else None,
            tags=work_item.fields.get('System.Tags', '').split('; ') if work_item.fields.get('System.Tags') else [],
            state=self.STATE_MAPPER.get(work_item.fields.get('System.State', None), WorkItemStateEnum.PENDING),
            acceptance_criteria=work_item.fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", None)
        )
    @classmethod
    def _get_source_state(cls, state):
        for key, value in cls.STATE_MAPPER.items():
            if value == state:
                return key
        raise ValueError(f"Invalid state: {state}")

    def update_work_item(self, updates: UpdateWorkItemInputModel) -> None:
        document = []
        if updates.title:
            document.append(JsonPatchOperation(op='replace', path='/fields/System.Title', value=updates.title))
        if updates.description:
            document.append(
                JsonPatchOperation(op='replace', path='/fields/System.Description', value=updates.description))
        if updates.assigned_to:
            document.append(
                JsonPatchOperation(op='replace', path='/fields/System.AssignedTo', value=updates.assigned_to))
        if updates.state:
            state = self._get_source_state(updates.state)
            document.append(JsonPatchOperation(op='replace', path='/fields/System.State', value=state))
        if updates.tags:
            document.append(JsonPatchOperation(op='replace', path='/fields/System.Tags', value="; ".join(updates.tags)))
        if updates.acceptance_criteria:
            document.append(
                JsonPatchOperation(op='replace', path='/fields/Microsoft.VSTS.Common.AcceptanceCriteria',
                                   value=updates.acceptance_criteria))

        self.wo_client.update_work_item(document, updates.source_id)

    def delete_work_item(self, work_item_id: int) -> None:
        self.wo_client.delete_work_item(work_item_id)

    def list_work_items(self, work_item_type: str = None, assigned_to: str = None,
                        state: WorkItemStateEnum = None) -> List[WorkItemModel]:
        query = "SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], [System.WorkItemType], [System.Description] FROM WorkItems"
        conditions = []
        if work_item_type:
            conditions.append(f"[System.WorkItemType] = '{work_item_type}'")
        if assigned_to:
            conditions.append(f"[System.AssignedTo] = '{assigned_to}'")
        if state:
            source_state = self._get_source_state(state)
            conditions.append(f"[System.State] = '{source_state}'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY [System.CreatedDate] DESC"
        wiql = {'query': query}
        result = self.wo_client.query_by_wiql(wiql)
        work_items = [self.get_work_item(work_item.id) for work_item in result.work_items]
        return work_items

    def list_comments(self, work_item_id: int) -> List[WorkItemCommentModel]:
        comments = self.wo_client.get_comments(self.auth.project_name, work_item_id)
        return [self.to_work_item_comment(comment) for comment in comments.comments]

    def create_comment(self, work_item_id: int, text: str) -> WorkItemCommentModel:
        comment_create = CommentCreate(text=text)
        created_comment = self.wo_client.add_comment(comment_create, self.auth.project_name, work_item_id)
        return self.to_work_item_comment(created_comment)

    def to_work_item_comment(self, comment: WorkItemComment) -> WorkItemCommentModel:
        """Converts an Azure DevOps WorkItemComment object to a Pydantic model."""
        return WorkItemCommentModel(
            id=comment.id,
            text=comment.text,
            created_by=comment.created_by.display_name if comment.created_by else None,
            created_date=comment.created_date,
            revised_by=comment.modified_by.display_name if comment.modified_by else None,
            revised_date=comment.modified_date,
        )

    def update_workitem_state(self, work_item_id, new_state):
        url = self.get_workitem_url(work_item_id)
        document = [
            {
                "op": "replace",
                "path": "/fields/System.State",
                "value": new_state
            }
        ]
        self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)

    def set_workitem_relationship(self, source_id, target_id, relationship):
        url = self.get_workitem_url(source_id)
        document = [
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": relationship,
                    "url": self.get_workitem_url(target_id)
                }
            }
        ]
        self.make_request('PATCH', url, headers={'Content-Type': 'application/json-patch+json'}, json=document)


    def get_workitem_url(self, work_item_id: int = None, wiql: bool = False) -> str:
        base_url = f"{self.organization_url}/{self.auth.project_name}/_apis/wit"
        if wiql:
            return f"{base_url}/wiql?api-version={self.api_version}"
        if work_item_id:
            return f"{base_url}/workitems/{work_item_id}?api-version={self.api_version}"
        return f"{base_url}/workitems?api-version={self.api_version}"