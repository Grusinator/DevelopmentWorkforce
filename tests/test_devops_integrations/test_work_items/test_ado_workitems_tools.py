import pytest
from src.devops_integrations.workitems.mock_workitems_api import MockWorkitemsApi
from src.devops_integrations.workitems.ado_workitems_api_tools import (CreateWorkItemInputModel,
                                                                       CreateWorkItemTool, GetWorkItemTool, UpdateWorkItemTool,
                                                                       DeleteWorkItemTool, ListWorkItemsTool,
                                                                       UpdateWorkItemInputModel, DeleteWorkItemInput,
                                                                       ListWorkItemsInput
                                                                       )
from src.devops_integrations.workitems.ado_workitem_models import GetWorkItemInputModel, WorkItemModel


class TestAdoWorkitemsApiTools:

    @pytest.fixture
    def mock_ado_workitems_api(self):
        return MockWorkitemsApi()

    @pytest.fixture
    def add_ado_test_item(self, mock_ado_workitems_api) -> WorkItemModel:
        work_item = CreateWorkItemInputModel(title="Initial Item", type='Bug', description="Initial Bug",
                                             assigned_to='John Doe', tags=[], state="New")
        work_item_id = mock_ado_workitems_api.create_work_item(work_item)
        return work_item_id

    def test_create_work_item(self, mock_ado_workitems_api):
        tool = CreateWorkItemTool(mock_ado_workitems_api)
        work_item = CreateWorkItemInputModel(
            title="New Feature",
            type="Feature",
            description="Implement new feature",
            assigned_to="Alice",
            tags=["feature"],
            state="New"
        )
        result = tool._run(kwargs=work_item.model_dump())
        assert isinstance(result["source_id"], int)

    def test_get_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = GetWorkItemTool(mock_ado_workitems_api)
        result = tool._run(kwargs=GetWorkItemInputModel(id=add_ado_test_item.source_id).model_dump())
        assert isinstance(result, dict)
        assert result["source_id"] == add_ado_test_item.source_id

    def test_update_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = UpdateWorkItemTool(mock_ado_workitems_api)
        updated_data = {"source_id": add_ado_test_item.source_id,
                        "work_item": {"title": "Updated Title", "description": "Updated description"}}
        input_model = UpdateWorkItemInputModel(**updated_data)
        result = tool._run(kwargs=input_model.model_dump())
        assert "message" in result
        assert len(mock_ado_workitems_api.work_items) == 1

    def test_delete_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = DeleteWorkItemTool(mock_ado_workitems_api)
        tool._run(kwargs=DeleteWorkItemInput(id=add_ado_test_item.source_id).model_dump())
        assert len(mock_ado_workitems_api.work_items) == 0

    def test_list_work_items(self, mock_ado_workitems_api, add_ado_test_item):
        tool = ListWorkItemsTool(mock_ado_workitems_api)
        result = tool._run(kwargs=ListWorkItemsInput().model_dump())
        assert isinstance(result, list)
        assert any(item["source_id"] == add_ado_test_item.source_id for item in result)
