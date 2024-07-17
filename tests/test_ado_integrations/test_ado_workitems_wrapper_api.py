import pytest

from development_workforce.ado_integrations.workitems.ado_workitem_models import CreateWorkItemInput, \
    UpdateWorkItemInput
from development_workforce.ado_integrations.workitems.ado_workitems_wrapper_api import ADOWorkitemsWrapperApi

ASSIGNED_TO = "William Sandvej Hansen"


@pytest.mark.integration
class TestADOWorkitemsWrapperApiIntegration:

    @pytest.fixture
    def api(self) -> ADOWorkitemsWrapperApi:
        return ADOWorkitemsWrapperApi()

    @pytest.fixture
    def create_work_item(self, api: ADOWorkitemsWrapperApi):
        work_item_input = CreateWorkItemInput(title="Test Work Item", description="This is a test work item", type="Task", assigned_to=ASSIGNED_TO)
        work_item_id = api.create_work_item(work_item_input)
        yield work_item_id
        api.delete_work_item(work_item_id)

    def test_create_work_item(self, api: ADOWorkitemsWrapperApi):
        work_item_input = CreateWorkItemInput(title="Create Test", description="Test Description", type="Task", assigned_to=ASSIGNED_TO)
        work_item_id = api.create_work_item(work_item_input)
        assert isinstance(work_item_id, int)
        api.delete_work_item(work_item_id)

    def test_get_work_item(self, api: ADOWorkitemsWrapperApi, create_work_item):
        work_item_details = api.get_work_item(create_work_item)
        assert work_item_details.id == create_work_item

    def test_get_work_item_snake(self, api: ADOWorkitemsWrapperApi):
        work_item_details = api.get_work_item(3)
        assert "snake" in work_item_details.title

    def test_update_work_item(self, api: ADOWorkitemsWrapperApi, create_work_item):
        new_title = "Updated Title"
        new_description = "Updated Description"
        updates = UpdateWorkItemInput(id=create_work_item, title=new_title, description=new_description)
        api.update_work_item(updates)
        updated_work_item = api.get_work_item(create_work_item)
        assert updated_work_item.title == new_title
        assert updated_work_item.description == new_description

    def test_delete_work_item(self, api: ADOWorkitemsWrapperApi):
        work_item_input = CreateWorkItemInput(title="Delete Test", description="Delete Description", type="Task", assigned_to=ASSIGNED_TO)
        work_item_id = api.create_work_item(work_item_input)
        api.delete_work_item(work_item_id)
        with pytest.raises(Exception):
            api.get_work_item(work_item_id)

    def test_list_work_items(self, api: ADOWorkitemsWrapperApi, create_work_item):
        work_items = api.list_work_items(work_item_type="Task")
        assert any(work_item.id == create_work_item for work_item in work_items)

    def test_list_work_items_assigned_to(self, api: ADOWorkitemsWrapperApi, create_work_item):
        work_items = api.list_work_items(assigned_to=ASSIGNED_TO)
        assert any(work_item.id == create_work_item for work_item in work_items)
