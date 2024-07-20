import pytest
from src.ado_integrations.workitems.ado_workitem_models import AdoWorkItem, CreateWorkItemInput, UpdateWorkItemInput
from src.ado_integrations.workitems.mock_ado_workitems_api import MockAdoWorkitemsApi

class TestMockAdoWorkitemApi:

    @pytest.fixture
    def api(self) -> MockAdoWorkitemsApi:
        return MockAdoWorkitemsApi()
    
    @pytest.fixture
    def add_work_item1(self, api: MockAdoWorkitemsApi):
        work_item = AdoWorkItem(id=1, type='Bug', assigned_to='John', title='Test')
        api.work_items.append(work_item)
        return work_item.id
    
    @pytest.fixture
    def add_work_item2(self, api):
        work_item = AdoWorkItem(id=2, type='Feature', assigned_to='Jane', title='Test2')
        api.work_items.append(work_item)
        return work_item.id

    def test_create_work_item(self, api):
        work_item = CreateWorkItemInput(type='Bug', assigned_to='John', title='Test')
        work_item_id = api.create_work_item(work_item)
        assert len(api.work_items) == 1
        assert api.work_items[0].assigned_to == work_item.assigned_to

    def test_get_work_item(self, api: MockAdoWorkitemsApi, add_work_item1: int):
        retrieved_work_item = api.get_work_item(add_work_item1)
        assert retrieved_work_item.id == add_work_item1
        assert api.work_items[0] == retrieved_work_item

    def test_get_work_item_not_found(self, api: MockAdoWorkitemsApi):
        with pytest.raises(ValueError):
            api.get_work_item(1)

    def test_update_work_item(self, api: MockAdoWorkitemsApi, add_work_item1):
        updated_work_item = UpdateWorkItemInput(id=1, type='Bug', assigned_to='Jane')
        api.update_work_item_description(updated_work_item)
        assert len(api.work_items) == 1
        assert api.work_items[0].assigned_to == 'Jane'

    def test_update_work_item_not_found(self, api):
        with pytest.raises(ValueError):
            api.update_work_item_description(UpdateWorkItemInput(id=1, type='Bug', assigned_to='Jane'))

    def test_delete_work_item(self, api: MockAdoWorkitemsApi, add_work_item1):
        api.delete_work_item(1)
        assert len(api.work_items) == 0

    def test_delete_work_item_not_found(self, api):
        with pytest.raises(ValueError):
            api.delete_work_item(1)

    def test_list_work_items(self, api, add_work_item1, add_work_item2):
        work_items = api.list_work_items()
        assert len(work_items) == 2
        assert work_items[0].id == add_work_item1
