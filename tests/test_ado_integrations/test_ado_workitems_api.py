import pytest
from development_workforce.ado_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from development_workforce.ado_integrations.workitems.ado_workitem_models import CreateWorkItemInput, UpdateWorkItemInput

@pytest.mark.integration
class TestADOWorkitemsApiIntegration:

    @pytest.fixture
    def api(self) -> ADOWorkitemsApi:
        return ADOWorkitemsApi()

    @pytest.fixture
    def create_work_item(self, api: ADOWorkitemsApi):
        work_item_input = CreateWorkItemInput(title="Test Work Item", description="This is a test work item", type="Task")
        work_item_id = api.create_object(work_item_input.title, work_item_input.description, work_item_input.type)
        yield work_item_id
        api.delete_work_item(work_item_id)

    def test_create_work_item(self, api: ADOWorkitemsApi):
        work_item_input = CreateWorkItemInput(title="Create Test", description="Test Description", type="Task")
        work_item_id = api.create_object(work_item_input.title, work_item_input.description, work_item_input.type)
        assert isinstance(work_item_id, int)
        api.delete_work_item(work_item_id)

    def test_get_work_item(self, api: ADOWorkitemsApi, create_work_item):
        work_item_details = api.get_work_item(create_work_item)
        assert work_item_details['id'] == create_work_item

    def test_update_work_item(self, api: ADOWorkitemsApi, create_work_item):
        new_title = "Updated Title"
        new_description = "Updated Description"
        api.update_object_details(create_work_item, new_title, new_description)
        updated_work_item = api.get_work_item(create_work_item)
        assert updated_work_item['title'] == new_title
        assert updated_work_item['description'] == new_description

    def test_delete_work_item(self, api: ADOWorkitemsApi):
        work_item_input = CreateWorkItemInput(title="Delete Test", description="Delete Description", type="Task")
        work_item_id = api.create_object(work_item_input.title, work_item_input.description, work_item_input.type)
        api.delete_work_item(work_item_id)
        with pytest.raises(Exception):
            api.get_work_item(work_item_id)
