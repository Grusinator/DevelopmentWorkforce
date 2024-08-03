import pytest
from azure.devops.exceptions import AzureDevOpsServiceError

from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from tests.test_devops_integrations.test_work_items.test_ado_workitems_wrapper_api import AGENT_USER_NAME


@pytest.fixture
def ado_workitems_api(auth) -> ADOWorkitemsApi:
    return ADOWorkitemsApi(auth)


@pytest.fixture
def create_work_item(ado_workitems_api: ADOWorkitemsApi):
    work_item_input = CreateWorkItemInputModel(title="Test Work Item", description="This is a test work item",
                                               type="Task", assigned_to=AGENT_USER_NAME, state="New")
    work_item_id = ado_workitems_api.create_work_item(work_item_input)
    yield work_item_id
    try:
        ado_workitems_api.delete_work_item(work_item_id)
    except AzureDevOpsServiceError as e:
        if "does not exist" not in str(e):
            raise e
