from typing import List, Dict
from langchain.tools import tool

from ado_integrations.ado_workitems_api import ADOWorkitemsApi


import logging

logger = logging.getLogger(__name__)


# Mock function to simulate fetching all work items from the ADO board
@tool
def ado_read_work_items() -> List[Dict]:
    """Fetch all work items from the ADO board."""
    try:
        return ADOWorkitemsApi().fetch_all_work_items()
    except Exception as e:
        logger.error(f"Error fetching work items: {e}")
        return {"error": str(e)}

# Mock function to simulate fetching details of a specific work item from the ADO board
@tool
def ado_read_work_item_details(work_item_id: int) -> Dict:
    """Fetch the details of a specific work item from the ADO board."""
    try:
        return ADOWorkitemsApi().fetch_object_details(work_item_id)
    except Exception as e:
        logger.error(f"Error fetching work item details: {e}")
        return {"error": str(e)}


ado_tools = [ado_read_work_items, ado_read_work_item_details]


if __name__ == "__main__":
    print(ado_read_work_items())
    print(ado_read_work_item_details)
