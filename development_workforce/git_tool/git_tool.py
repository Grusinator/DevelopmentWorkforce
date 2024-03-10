from typing import Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun

from git import Repo, exc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
repo_url = os.getenv("GIT_REPO_URL")

# Path to your local git repository
repo_path = 'path_to_your_local_repo'


def clone_repo(url, path):
    try:
        print(f"Cloning repo from {url} into {path}")
        Repo.clone_from(url, path)
        print("Repo cloned successfully.")
    except exc.GitCommandError as e:
        print(f"Error cloning repo: {e}")


def pull():
    try:
        repo = Repo(repo_path)
        origin = repo.remotes.origin
        origin.pull()
        print("Repo pulled successfully.")
    except exc.GitCommandError as e:
        print(f"Error pulling repo: {e}")


def push():
    try:
        repo = Repo(repo_path)
        origin = repo.remotes.origin
        origin.push()
        print("Repo pushed successfully.")
    except exc.GitCommandError as e:
        print(f"Error pushing repo: {e}")


def commit_all(message="Auto commit"):
    try:
        repo = Repo(repo_path)
        repo.git.add(A=True)
        repo.index.commit(message)
        print("All changes committed.")
    except exc.GitCommandError as e:
        print(f"Error committing: {e}")


class PullInput(BaseModel):
    # No input needed for pull and push operations
    pass


class PushInput(BaseModel):
    pass


# Input required for commit operation
class CommitInput(BaseModel):
    message: str = Field(description="Commit message")


class GitPullTool(BaseTool):
    name = "git_pull"
    description = "Pulls the latest changes from the remote repository."
    args_schema: Type[BaseModel] = PullInput

    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        pull()
        return "Pulled latest changes from remote."

    async def _arun(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        raise NotImplementedError("GitPullTool does not support async operations")


class GitPushTool(BaseTool):
    name = "git_push"
    description = "Pushes local commits to the remote repository."
    args_schema: Type[BaseModel] = PushInput

    def _run(self, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        push()
        return "Pushed local commits to remote."

    async def _arun(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        raise NotImplementedError("GitPushTool does not support async operations")


class GitCommitTool(BaseTool):
    name = "git_commit"
    description = "Commits all changes with a provided commit message."
    args_schema: Type[BaseModel] = CommitInput

    def _run(self, message: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        commit_all(message)
        return f"Committed all changes with message: '{message}'"

    async def _arun(self, message: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        raise NotImplementedError("GitCommitTool does not support async operations")
