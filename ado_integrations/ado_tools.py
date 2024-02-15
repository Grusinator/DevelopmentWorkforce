from langchain.tools import BaseTool, StructuredTool, tool

from ado_integrations.ado_board import ADOBoard


@tool
def ado_read_work_items() -> list:
    """Fetch all work items from the ADO board."""
    return [{"id": 1, "title": "Build a snake app", "state": "Active"}]
# ADOBoard().fetch_all_objects()

@tool
def ado_read_work_item_details(work_item_id: int) -> dict:
    """Fetch the details of a specific work item from the ADO board."""
    return ADOBoard().fetch_object_details(work_item_id)

ado_tools = [ado_read_work_items, ado_read_work_item_details]
