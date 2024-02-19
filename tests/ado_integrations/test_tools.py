import pytest

from development_workforce.ado_integrations.ado_tools import ado_read_work_item_details, ado_read_work_items

@pytest.mark.skip(reason="This test is not yet implemented")
def test_tool_ado_read_work_items():
    # Your code to read work items from ADO goes here
    res = ado_read_work_items()
    assert res is not None

@pytest.mark.skip(reason="This test is not yet implemented")
def test_tool_ado_read_work_item_details():
    # Your code to read work item details from ADO goes here
    ado_read_work_item_details(1)
