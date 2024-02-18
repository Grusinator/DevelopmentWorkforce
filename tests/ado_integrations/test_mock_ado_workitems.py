import pytest
from ado_integrations.ado_models import AdoWorkItem
from ado_integrations.mock_ado_workitems_api import MockAdoWorkitemsApi

class TestMockAdoWorkitemApi:
    @pytest.fixture
    def api(self):
        return MockAdoWorkitemsApi()

    def test_create_work_item(self, api):
        work_item = AdoWorkItem(id=1, type='Bug', assigned_to='John')
        work_item_id = api.create_work_item(work_item)
        assert work_item_id == 1
        assert len(api.work_items) == 1
        assert api.work_items[0] == work_item

    def test_get_work_item(self, api):
        work_item = AdoWorkItem(id=1, type='Bug', assigned_to='John')
        api.work_items.append(work_item)
        retrieved_work_item = api.get_work_item(1)
        assert retrieved_work_item == work_item

    def test_get_work_item_not_found(self, api):
        with pytest.raises(ValueError):
            api.get_work_item(1)

    def test_update_work_item(self, api):
        work_item = AdoWorkItem(id=1, type='Bug', assigned_to='John')
        updated_work_item = AdoWorkItem(id=1, type='Bug', assigned_to='Jane')
        api.work_items.append(work_item)
        api.update_work_item(1, updated_work_item)
        assert len(api.work_items) == 1
        assert api.work_items[0] == updated_work_item

    def test_update_work_item_not_found(self, api):
        with pytest.raises(ValueError):
            api.update_work_item(1, AdoWorkItem(id=1, type='Bug', assigned_to='Jane'))

    def test_delete_work_item(self, api):
        work_item = AdoWorkItem(id=1, type='Bug', assigned_to='John')
        api.work_items.append(work_item)
        api.delete_work_item(1)
        assert len(api.work_items) == 0

    def test_delete_work_item_not_found(self, api):
        with pytest.raises(ValueError):
            api.delete_work_item(1)

    def test_list_work_items(self, api):
        work_item1 = AdoWorkItem(id=1, type='Bug', assigned_to='John')
        work_item2 = AdoWorkItem(id=2, type='Feature', assigned_to='Jane')
        api.work_items.append(work_item1)
        api.work_items.append(work_item2)
        filtered_work_items = api.list_work_items(work_item_type='Bug')
        assert len(filtered_work_items) == 1
        assert filtered_work_items[0] == work_item1

        filtered_work_items = api.list_work_items(assigned_to='Jane')
        assert len(filtered_work_items) == 1
        assert filtered_work_items[0] == work_item2

        filtered_work_items = api.list_work_items(work_item_type='Bug', assigned_to='Jane')
        assert len(filtered_work_items) == 0
