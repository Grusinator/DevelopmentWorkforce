from abc import ABC
from typing import Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from src.git_tool.git_abstraction import GitAbstraction
import logging
from pydantic import BaseModel, Field

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from src.utils import log_inputs

logger = logging.getLogger(__name__)


class CreateBranchInput(BaseModel):
    branch_name: str = Field(..., title="Branch Name", description="Name of the branch to be created")


class GitToolBase(BaseTool, ABC):
    _git_abstraction: GitAbstraction

    def __init__(self, git_api: GitAbstraction):
        super().__init__()
        object.__setattr__(self, '_git_abstraction', git_api)


class CloneRepoTool(GitToolBase):
    name = "clone git repository"
    description = "Tool to clone a git repository"

    @log_inputs
    def _run(self, args, kwargs, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            self._git_abstraction.clone_repo()
            return {"message": "Repository cloned successfully"}
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return {"error": str(e)}


class CreateBranchTool(GitToolBase):
    name = "create git branch"
    description = "Tool to create and checkout a new branch in a git repository"

    @log_inputs
    def _run(self, args, kwargs, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            input_model = CreateBranchInput(**kwargs)
            self._git_abstraction.create_and_checkout_branch(input_model.branch_name)
            return {"message": f"Branch '{input_model.branch_name}' created and checked out successfully"}
        except Exception as e:
            logger.error(f"Error creating/checking out branch: {e}")
            return {"error": str(e)}


class PullRepoTool(GitToolBase):
    name = "pull git repository"
    description = "Tool to pull the latest changes from the remote repository"

    @log_inputs
    def _run(self, args, kwargs, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            self._git_abstraction.pull()
            return {"message": "Repository pulled successfully"}
        except Exception as e:
            logger.error(f"Error pulling repository: {e}")
            return {"error": str(e)}


class PushRepoTool(GitToolBase):
    name = "push git repository"
    description = "Tool to push local changes to the remote repository"

    @log_inputs
    def _run(self, args, kwargs, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            self._git_abstraction.push()
            return {"message": "Repository pushed successfully"}
        except Exception as e:
            logger.error(f"Error pushing repository: {e}")
            return {"error": str(e)}


class CommitAllInput(BaseModel):
    message: str = Field(..., title="Commit Message", description="Message for the commit")

class CommitAllTool(GitToolBase):
    name = "commit all changes"
    description = "Tool to add and commit all changes in the repository"

    @log_inputs
    def _run(self, args, kwargs, run_manager: Optional[CallbackManagerForToolRun] = None) -> Dict[str, str]:
        try:
            input_model = CommitAllInput(**kwargs)
            self._git_abstraction.commit_all(input_model.message)
            return {"message": "All changes committed successfully"}
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return {"error": str(e)}


def instantiate_git_tools(git_api: GitAbstraction) -> List[GitToolBase]:
    tools = [
        CloneRepoTool(git_api),
        CreateBranchTool(git_api),
        PullRepoTool(git_api),
        PushRepoTool(git_api),
        CommitAllTool(git_api),
    ]
    return tools
