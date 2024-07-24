import pytest
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi
from src.ado_integrations.workitems.ado_workitems_api_tools import (CreateWorkItemInput,
                                                                                      CreateWorkItemTool, GetWorkItemTool, UpdateWorkItemTool,
                                                                                      DeleteWorkItemTool, ListWorkItemsTool,
                                                                                      UpdateWorkItemInput, DeleteWorkItemInput,
                                                                                      ListWorkItemsInput
                                                                                      )
from src.ado_integrations.workitems.ado_workitem_models import GetWorkItemInput


class TestAdoWorkitemsApiTools:

    @pytest.fixture
    def mock_ado_workitems_api(self):
        return MockAdoWorkitemsApi()

    @pytest.fixture
    def add_ado_test_item(self, mock_ado_workitems_api) -> int:
        work_item = CreateWorkItemInput(title="Initial Item", type='Bug', description="Initial Bug",
                                        assigned_to='John Doe', tags=[])
        work_item_id = mock_ado_workitems_api.create_work_item(work_item)
        return work_item_id

    def test_create_work_item(self, mock_ado_workitems_api):
        tool = CreateWorkItemTool(mock_ado_workitems_api)
        work_item = CreateWorkItemInput(
            title="New Feature",
            type="Feature",
            description="Implement new feature",
            assigned_to="Alice",
            tags=["feature"],
            state="New"
        )
        result = tool._run(work_item)
        assert isinstance(result, int)

    def test_get_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = GetWorkItemTool(mock_ado_workitems_api)
        result = tool._run(GetWorkItemInput(id=add_ado_test_item))
        assert isinstance(result, dict)
        assert result["id"] == add_ado_test_item

    def test_update_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = UpdateWorkItemTool(mock_ado_workitems_api)
        updated_data = {"id": add_ado_test_item,
                        "work_item": {"title": "Updated Title", "description": "Updated description"}}
        input_model = UpdateWorkItemInput(**updated_data)
        result = tool._run(input_model)
        assert "message" in result
        assert result["id"] == add_ado_test_item

    def test_delete_work_item(self, mock_ado_workitems_api, add_ado_test_item):
        tool = DeleteWorkItemTool(mock_ado_workitems_api)
        tool._run(DeleteWorkItemInput(id=add_ado_test_item))
        # Additional assertions can be added here as needed

    def test_list_work_items(self, mock_ado_workitems_api, add_ado_test_item):
        tool = ListWorkItemsTool(mock_ado_workitems_api)
        result = tool._run(ListWorkItemsInput())
        assert isinstance(result, list)
        assert any(item["id"] == add_ado_test_item for item in result)
