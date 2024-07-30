import os
import pytest
from azure.devops.exceptions import AzureDevOpsServiceError
from src.ado_integrations.workitems.ado_workitem_models import CreateWorkItemInput
from src.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi
from src.ado_integrations.workitems.ado_workitems_comments_api import ADOWorkitemsCommentsApi

ASSIGNED_TO = os.getenv("AI_USER_NAME")


@pytest.mark.integration
class TestADOWorkitemsCommentsApiIntegration:

    @pytest.fixture
    def workitems_api(self) -> ADOWorkitemsWrapperApi:
        pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
        project_name = os.getenv("ADO_PROJECT_NAME")
        return ADOWorkitemsWrapperApi(pat, ado_org_name, project_name)

    @pytest.fixture
    def comments_api(self) -> ADOWorkitemsCommentsApi:
        pat = os.getenv("ADO_PERSONAL_ACCESS_TOKEN")
        ado_org_name = os.getenv("ADO_ORGANIZATION_NAME")
        project_name = os.getenv("ADO_PROJECT_NAME")
        return ADOWorkitemsCommentsApi(pat, ado_org_name, project_name)

    @pytest.fixture
    def create_work_item(self, workitems_api: ADOWorkitemsWrapperApi):
        work_item_input = CreateWorkItemInput(title="Test Work Item", description="This is a test work item",
                                              type="Task", assigned_to=ASSIGNED_TO, state="New")
        work_item_id = workitems_api.create_work_item(work_item_input)
        yield work_item_id
        try:
            workitems_api.delete_work_item(work_item_id)
        except AzureDevOpsServiceError as e:
            if "does not exist" not in str(e):
                raise e

    def test_add_and_list_comments(self, comments_api: ADOWorkitemsCommentsApi, create_work_item):
        work_item_id = create_work_item
        comment_text = "This is a test comment."

        # Act
        created_comment = comments_api.create_comment(work_item_id, comment_text)
        comments = comments_api.list_comments(work_item_id)

        # Assert
        assert any(comment.text == comment_text for comment in comments)
        assert created_comment.text == comment_text
