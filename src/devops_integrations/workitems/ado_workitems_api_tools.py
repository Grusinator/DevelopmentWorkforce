from abc import ABC
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from src.devops_integrations.workitems.ado_workitem_models import CreateWorkItemInputModel, \
    UpdateWorkItemInputModel, GetWorkItemInputModel
from src.devops_integrations.workitems.base_workitems_api import BaseWorkitemsApi
import logging

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from src.utils import log_inputs

logger = logging.getLogger(__name__)


class AdoWorkitemToolBase(BaseTool, ABC):
    # Base class for ADO Work Item operations to handle dependency injection
    _ado_workitems_api: BaseWorkitemsApi

    def __init__(self, ado_workitems_api: BaseWorkitemsApi):
        super().__init__()
        # this is in order to dodge pydantics type checking to allow for dependency injection into thic class. is similar to
        # self._ado_workitems_api = ado_workitems_api
        object.__setattr__(self, '_ado_workitems_api', ado_workitems_api)


class CreateWorkItemTool(AdoWorkitemToolBase):
    name = "create ADO workitem"
    description = "Tool to create a new ADO work item"
    # args_schema: Type[BaseModel] = CreateWorkItemInput

    @log_inputs
    def _run(self, args=None, kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[
        str, Union[str, int]]:
        try:
            input_model = CreateWorkItemInputModel(**kwargs)
            created_id = self._ado_workitems_api.create_work_item(input_model)
            return {"source_id": created_id.source_id}
        except Exception as e:
            logger.error(f"Error creating work item: {e}")
            return {"error": str(e)}


class GetWorkItemTool(AdoWorkitemToolBase):
    name = "get ADO work item"
    description = "Tool to get a single ADO work item"
    # args_schema: Type[BaseModel] = GetWorkItemInput
    # This is a workaround to avoid the type checking of pydantic.

    @log_inputs
    def _run(self, args=None, kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[
        str, str]:
        try:
            work_item = GetWorkItemInputModel(**kwargs)
            ado_work_item = self._ado_workitems_api.get_work_item(work_item.id)
            return ado_work_item.model_dump()
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return {"error": str(e)}


class UpdateWorkItemTool(AdoWorkitemToolBase):
    name = "update ADO work item"
    description = "Tool to update an existing ADO work item. The ID of the work item to update must be provided." \
                  "The action Input field can be filled out as following:" \
                  "title: Example title, type: Example type, description: Example description, assigned_to: Example assigned_to"

    # args_schema: Type[BaseModel] = UpdateWorkItemInput

    @log_inputs
    def _run(self, args=None, kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[
        str, str]:
        try:
            input_model = UpdateWorkItemInputModel(**kwargs)
            self._ado_workitems_api.update_work_item(input_model)
            return {"message": "Work item updated successfully"}
        except Exception as e:
            logger.error(f"Error updating work item: {e}")
            return {"error": str(e)}


class DeleteWorkItemInput(BaseModel):
    id: int = Field(description="ID of the work item to delete")


class DeleteWorkItemTool(AdoWorkitemToolBase):
    name = "delete ADO work item"
    description = "Tool to delete an ADO work item"
    # args_schema: Type[BaseModel] = DeleteWorkItemInput

    @log_inputs
    def _run(self, args=None, kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[
        str, str]:
        try:
            input_model = DeleteWorkItemInput(**kwargs)
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
    # args_schema: Type[BaseModel] = ListWorkItemsInput  # Adjust if you add filters

    @log_inputs
    def _run(self, args=None, kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> \
            List[Dict[str, str]]:
        try:
            # input_model = ListWorkItemsInput(**kwargs)
            work_items = self._ado_workitems_api.list_work_items()
            return [item.model_dump() for item in work_items]
        except Exception as e:
            logger.error(f"Error listing work items: {e}")
            return [{"error": str(e)}]


def instantiate_ado_tools(ado_workitems_api: BaseWorkitemsApi) -> List[AdoWorkitemToolBase]:
    tools = [
        CreateWorkItemTool(ado_workitems_api),
        GetWorkItemTool(ado_workitems_api),
        UpdateWorkItemTool(ado_workitems_api),
        DeleteWorkItemTool(ado_workitems_api),
        ListWorkItemsTool(ado_workitems_api),
    ]
    return tools
