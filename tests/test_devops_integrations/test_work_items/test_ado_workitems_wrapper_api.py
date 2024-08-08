import pytest

from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel, \
    UpdateWorkItemInputModel
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi


@pytest.mark.integration
class TestADOWorkitemsApi:

    def test_create_work_item(self, ado_workitems_api: ADOWorkitemsApi, agent_model):
        work_item_input = CreateWorkItemInputModel(title="Create Test", description="Test Description", type="Task",
                                                   assigned_to=agent_model.agent_user_name, state="New")
        work_item = ado_workitems_api.create_work_item(work_item_input)
        assert isinstance(work_item.source_id, int)
        ado_workitems_api.delete_work_item(work_item.source_id)

    def test_get_work_item(self, ado_workitems_api: ADOWorkitemsApi, create_work_item):
        work_item_details = ado_workitems_api.get_work_item(create_work_item.source_id)
        assert work_item_details.source_id == create_work_item.source_id

    def test_get_work_item_snake(self, ado_workitems_api: ADOWorkitemsApi):
        work_item_details = ado_workitems_api.get_work_item(3)
        assert "snake" in work_item_details.title

    def test_update_work_item(self, ado_workitems_api: ADOWorkitemsApi, create_work_item):
        new_title = "Updated Title"
        new_description = "Updated Description"
        updates = UpdateWorkItemInputModel(source_id=create_work_item.source_id, title=new_title,
                                           description=new_description,
                                           acceptance_criteria="new acc")
        ado_workitems_api.update_work_item(updates)
        updated_work_item = ado_workitems_api.get_work_item(create_work_item.source_id)
        assert updated_work_item.title == new_title
        assert updated_work_item.description == new_description

    def test_delete_work_item(self, ado_workitems_api: ADOWorkitemsApi, create_work_item):
        work_item_id = create_work_item.source_id
        ado_workitems_api.delete_work_item(work_item_id)
        with pytest.raises(Exception):
            ado_workitems_api.get_work_item(work_item_id)

    def test_list_work_items(self, ado_workitems_api: ADOWorkitemsApi, create_work_item):
        work_items = ado_workitems_api.list_work_items(work_item_type="Task")
        assert any(work_item.source_id == create_work_item.source_id for work_item in work_items)

    def test_list_work_items_assigned_to(self, ado_workitems_api: ADOWorkitemsApi, create_work_item, agent_model):
        work_items = ado_workitems_api.list_work_items(assigned_to=agent_model.agent_user_name)
        assert any(work_item.source_id == create_work_item.source_id for work_item in work_items)

    def test_add_and_list_comments(self, ado_workitems_api, create_work_item):
        work_item_id = create_work_item.source_id
        comment_text = "This is a test comment."

        # Act
        created_comment = ado_workitems_api.create_comment(work_item_id, comment_text)
        comments = ado_workitems_api.list_comments(work_item_id)

        # Assert
        assert any(comment.text == comment_text for comment in comments)
        assert created_comment.text == comment_text
