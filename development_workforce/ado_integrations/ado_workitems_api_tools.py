from development_workforce.ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi
from development_workforce.ado_integrations.mock_ado_workitems_api import AdoWorkItem
from typing import List, Dict
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)
class AdoWorkitemsApiTools:
    def __init__(self, ado_workitems_api: BaseAdoWorkitemsApi):
        self.ado_workitems_api = ado_workitems_api

    def get_tools(self):
        tools = [self.create_work_item, self.get_work_item, self.update_work_item, self.delete_work_item, self.list_work_items]
        return tools

    @tool
    def create_work_item(self, work_item: Dict[str, str]) -> int:
        """Create a work item. insert the json content of the work item as a dictionary to set fields"""
        ado_work_item = AdoWorkItem(**work_item)
        try:
            return self.ado_workitems_api.create_work_item(ado_work_item)
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return {"error": str(e)}

    @tool
    def get_work_item(self, work_item_id: int) -> Dict[str, str]:
        """Get a ADO work item. query by using the id of the work item."""
        try:
            ado_work_item = self.ado_workitems_api.get_work_item(work_item_id)
            return ado_work_item.model_dump_json()
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return {"error": str(e)}

    @tool
    def update_work_item(self, work_item_id: int, updated_work_item: Dict[str, str]) -> None:
        """Create a work item. insert the json content of the work item as a dictionary to update fields. """
        ado_work_item = AdoWorkItem(**updated_work_item)
        try:
            self.ado_workitems_api.update_work_item(work_item_id, ado_work_item)
        except Exception as e:
            logger.error(f"Error updating work item: {e}")

    @tool
    def delete_work_item(self, work_item_id: int) -> None:
        """Delete a ADO work item, by passing an id of the work item."""
        try:
            self.ado_workitems_api.delete_work_item(work_item_id)
        except Exception as e:
            logger.error(f"Error deleting work item: {e}")

    @tool
    def list_work_items(self) -> List[Dict[str, str]]:
        """List all ADO work items. no filtering is done."""
        try:
            ado_work_items = self.ado_workitems_api.list_work_items()
            # Convert the list of AdoWorkItem models to a list of dictionaries
            return [work_item.model_dump() for work_item in ado_work_items]
        except Exception as e:
            logger.error(f"Error listing work items: {e}")
            return {"error": str(e)}



