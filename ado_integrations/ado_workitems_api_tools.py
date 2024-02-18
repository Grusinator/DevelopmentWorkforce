from typing import List, Dict
from langchain.tools import tool

from ado_integrations.ado_workitems_api import ADOWorkitemsApi


import logging

from ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi

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
    

from typing import List
from ado_integrations.mock_ado_workitems_api import AdoWorkItem
from typing import List, Dict
from langchain.tools import tool
from ado_integrations.ado_workitems_api import ADOWorkitemsApi
import logging

logger = logging.getLogger(__name__)
class AdoWorkitemsApiTools:
    def __init__(self, ado_workitems_api: BaseAdoWorkitemsApi):
        self.ado_workitems_api = ado_workitems_api

    def get_tools(self):
        return [self.create_work_item, self.get_work_item, self.update_work_item, self.delete_work_item, self.list_work_items]

    @tool
    def create_work_item(self, work_item: Dict[str, str]) -> int:
        """Create a work item."""
        ado_work_item = AdoWorkItem(**work_item)
        try:
            return self.ado_workitems_api.create_work_item(ado_work_item)
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return {"error": str(e)}

    @tool
    def get_work_item(self, work_item_id: int) -> Dict[str, str]:
        """Get a ADO work item."""
        try:
            ado_work_item = self.ado_workitems_api.get_work_item(work_item_id)
            return ado_work_item.model_dump_json()
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return {"error": str(e)}

    @tool
    def update_work_item(self, work_item_id: int, updated_work_item: Dict[str, str]) -> None:
        """Update a ADO work item."""
        ado_work_item = AdoWorkItem(**updated_work_item)
        try:
            self.ado_workitems_api.update_work_item(work_item_id, ado_work_item)
        except Exception as e:
            logger.error(f"Error updating work item: {e}")

    @tool
    def delete_work_item(self, work_item_id: int) -> None:
        """Delete a ADO work item."""
        try:
            self.ado_workitems_api.delete_work_item(work_item_id)
        except Exception as e:
            logger.error(f"Error deleting work item: {e}")

    @tool
    def list_work_items(self, work_item_type: str = None, assigned_to: str = None) -> List[Dict[str, str]]:
        """List filtered ADO work items."""
        try:
            ado_work_items = self.ado_workitems_api.list_work_items(work_item_type, assigned_to)
            # Convert the list of AdoWorkItem models to a list of dictionaries
            return [work_item.dict() for work_item in ado_work_items]
        except Exception as e:
            logger.error(f"Error listing work items: {e}")
            return {"error": str(e)}



