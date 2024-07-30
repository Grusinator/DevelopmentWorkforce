from dotenv import load_dotenv

from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking.models import WorkItemComment, CommentCreate
from msrest.authentication import BasicAuthentication
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

load_dotenv()


class WorkItemCommentModel(BaseModel):
    id: int
    text: str
    created_by: Optional[str]
    created_date: datetime
    revised_by: Optional[str]
    revised_date: Optional[datetime]


class ADOWorkitemsCommentsApi:
    def __init__(self, pat, ado_org_name, project_name):
        self.organization_url = "https://dev.azure.com/" + ado_org_name
        self.personal_access_token = pat
        self.project_name = project_name
        credentials = BasicAuthentication('', self.personal_access_token)
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        self.client = self.connection.clients.get_work_item_tracking_client()

    def list_comments(self, work_item_id: int) -> List[WorkItemCommentModel]:
        comments = self.client.get_comments(self.project_name, work_item_id)
        return [self._from_ado(comment) for comment in comments.comments]

    def create_comment(self, work_item_id: int, text: str) -> WorkItemCommentModel:
        comment_create = CommentCreate(text=text)
        created_comment = self.client.add_comment(comment_create, self.project_name, work_item_id)
        return self._from_ado(created_comment)

    def _from_ado(self, comment: WorkItemComment) -> WorkItemCommentModel:
        """Converts an Azure DevOps WorkItemComment object to a Pydantic model."""
        return WorkItemCommentModel(
            id=comment.id,
            text=comment.text,
            created_by=comment.created_by.display_name if comment.created_by else None,
            created_date=comment.created_date,
            revised_by=comment.modified_by.display_name if comment.modified_by else None,
            revised_date=comment.modified_date,
        )
