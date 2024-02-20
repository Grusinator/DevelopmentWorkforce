from typing import Dict, List, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from development_workforce.ado_integrations.base_ado_workitems_api import BaseAdoWorkitemsApi
from development_workforce.ado_integrations.mock_ado_workitems_api import AdoWorkItem
import logging

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

logger = logging.getLogger(__name__)

# Base class for ADO Work Item operations to handle dependency injection
class AdoWorkitemToolBase(BaseTool):
    def __init__(self, ado_workitems_api: BaseAdoWorkitemsApi):
        super().__init__()
        # this is in order to dodge pydantics type checking to allow for dependency injection into thic class. is similar to 
        # self._ado_workitems_api = ado_workitems_api
        object.__setattr__(self, '_ado_workitems_api', ado_workitems_api)


class CreateWorkItemTool(AdoWorkitemToolBase):
    name = "create ADO workitem"
    description = "Tool to create a new ADO work item"
    args_schema: Type[BaseModel] = AdoWorkItem

    def _run(self, work_item: AdoWorkItem, run_manager: Optional[CallbackManagerForToolRun] = None) -> int:
        try:
            return self._ado_workitems_api.create_work_item(work_item)
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return {"error": str(e)}
        


class ADOWorkItemID(BaseModel):
    id: int = Field(description="ID of the work item to get")

class GetWorkItemTool(AdoWorkitemToolBase):
    name = "get ADO work item"
    description = "Tool to get a single ADO work item"
    args_schema: Type[BaseModel] = ADOWorkItemID

    def _run(self, ado_work_item_id: ADOWorkItemID, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            ado_work_item = self._ado_workitems_api.get_work_item(ado_work_item_id.id)
            return ado_work_item.model_dump_json()
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return {"error": str(e)}
        


        
class UpdateWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to update")
    work_item: Dict[str, str] = Field(description="Updated fields of the work item")

        
class UpdateWorkItemTool(AdoWorkitemToolBase):
    name = "update ADO work item"
    description = "Tool to update an existing ADO work item"
    args_schema: Type[BaseModel] = UpdateWorkItemInput

    def _run(self, input_model: UpdateWorkItemInput, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            ado_work_item = AdoWorkItem(**input_model.work_item)
            self._ado_workitems_api.update_work_item(input_model.id, ado_work_item)
            return {"message": "Work item updated successfully"}
        except Exception as e:
            logger.error(f"Error updating work item: {e}")
            return {"error": str(e)}


class DeleteWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to delete")


class DeleteWorkItemTool(AdoWorkitemToolBase):
    name = "delete ADO work item"
    description = "Tool to delete an ADO work item"
    args_schema: Type[BaseModel] = DeleteWorkItemInput

    def _run(self, input_model: DeleteWorkItemInput, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            self._ado_workitems_api.delete_work_item(input_model.id)
            return {"message": "Work item deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting work item: {e}")
            return {"error": str(e)}


class ListWorkItemsInput(BaseModel):
    # Add any filtering fields here if needed
    pass


class ListWorkItemsTool(AdoWorkitemToolBase):
    name = "list ADO work items"
    description = "Tool to list all ADO work items"
    args_schema: Type[BaseModel] = ListWorkItemsInput  # Adjust if you add filters

    def _run(self, input_model: ListWorkItemsInput = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> List[Dict[str, str]]:
        try:
            work_items = self._ado_workitems_api.list_work_items()
            return [item.model_dump_json() for item in work_items]
        except Exception as e:
            logger.error(f"Error listing work items: {e}")
            return [{"error": str(e)}]



def instantiate_ado_tools(ado_workitems_api: BaseAdoWorkitemsApi) -> List[AdoWorkitemToolBase]:
    tools = [
        CreateWorkItemTool(ado_workitems_api),
        GetWorkItemTool(ado_workitems_api),
        UpdateWorkItemTool(ado_workitems_api),
        DeleteWorkItemTool(ado_workitems_api),
        ListWorkItemsTool(ado_workitems_api),
    ]
    return tools
