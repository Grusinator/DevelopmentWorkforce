import pytest
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel, CreateWorkItemInputModel, UpdateWorkItemInputModel
from src.devops_integrations.workitems.mock_workitems_api import MockWorkitemsApi


class TestMockAdoWorkitemApi:

    @pytest.fixture
    def mock_workitem_api(self) -> MockWorkitemsApi:
        return MockWorkitemsApi()

    @pytest.fixture
    def add_work_item1(self, mock_workitem_api: MockWorkitemsApi):
        work_item = WorkItemModel(source_id=1, type='Bug', assigned_to='John', title='Test', state="New")
        mock_workitem_api.work_items.append(work_item)
        return work_item.source_id

    @pytest.fixture
    def add_work_item2(self, mock_workitem_api):
        work_item = WorkItemModel(source_id=2, type='Feature', assigned_to='Jane', title='Test2', state="New")
        mock_workitem_api.work_items.append(work_item)
        return work_item.source_id

    def test_create_work_item(self, mock_workitem_api):
        work_item = CreateWorkItemInputModel(type='Bug', assigned_to='John', title='Test', state="New")
        mock_workitem_api.create_work_item(work_item)
        assert len(mock_workitem_api.work_items) == 1
        assert mock_workitem_api.work_items[0].assigned_to == work_item.assigned_to

    def test_get_work_item(self, mock_workitem_api: MockWorkitemsApi, add_work_item1: int):
        retrieved_work_item = mock_workitem_api.get_work_item(add_work_item1)
        assert retrieved_work_item.source_id == add_work_item1
        assert mock_workitem_api.work_items[0] == retrieved_work_item

    def test_get_work_item_not_found(self, mock_workitem_api: MockWorkitemsApi):
        with pytest.raises(ValueError):
            mock_workitem_api.get_work_item(1)

    def test_update_work_item(self, mock_workitem_api: MockWorkitemsApi, add_work_item1):
        updated_work_item = UpdateWorkItemInputModel(source_id=1, type='Bug', assigned_to='Jane')
        mock_workitem_api.update_work_item(updated_work_item)
        assert len(mock_workitem_api.work_items) == 1
        assert mock_workitem_api.work_items[0].assigned_to == 'Jane'

    def test_update_work_item_not_found(self, mock_workitem_api):
        with pytest.raises(ValueError):
            mock_workitem_api.update_work_item(UpdateWorkItemInputModel(source_id=1, type='Bug', assigned_to='Jane'))

    def test_delete_work_item(self, mock_workitem_api: MockWorkitemsApi, add_work_item1):
        mock_workitem_api.delete_work_item(1)
        assert len(mock_workitem_api.work_items) == 0

    def test_delete_work_item_not_found(self, mock_workitem_api):
        with pytest.raises(ValueError):
            mock_workitem_api.delete_work_item(1)

    def test_list_work_items(self, mock_workitem_api, add_work_item1, add_work_item2):
        work_items = mock_workitem_api.list_work_items()
        assert len(work_items) == 2
        assert work_items[0].source_id == add_work_item1
