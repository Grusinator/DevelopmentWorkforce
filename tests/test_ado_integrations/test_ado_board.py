import pytest
from src.ado_integrations.workitems.ado_workitems_api import ADOWorkitemsApi


@pytest.mark.skip(reason="This test is not yet implemented")
def test_fetch_all_objects():
    interface = ADOWorkitemsApi()
    objects = interface.fetch_all_objects()

    assert isinstance(objects, list)
    assert all(isinstance(obj, dict) for obj in objects)
    assert all('id' in obj and 'title' in obj and 'state' in obj for obj in objects)

@pytest.mark.skip(reason="This test is not yet implemented")
def test_fetch_object_details():
    interface = ADOWorkitemsApi()
    work_item_id = 1
    details = interface.fetch_object_details(work_item_id)

    assert isinstance(details, dict)
    assert 'id' in details
    assert 'title' in details
    assert 'state' in details
