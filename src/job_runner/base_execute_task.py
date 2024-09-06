from abc import ABC, abstractmethod

from organization.schemas import AgentModel
from src.crew.models import AutomatedTaskResult
from src.devops_integrations.repos.ado_repos_models import RepositoryModel


class BaseExecuteTask(ABC):
    name: str

    def __init__(self):
        if not hasattr(self, 'name'):
            raise NotImplementedError("Derived classes must define a 'name' class field")

    @abstractmethod
    def decode_and_validate_args(self, encoded_args: str):
        pass

    @abstractmethod
    def execute(self, agent: AgentModel, repo: RepositoryModel, *args) -> AutomatedTaskResult:
        pass

    def run(self, encoded_args: str) -> AutomatedTaskResult:
        args, kwargs = self.decode_and_validate_args(encoded_args)
        return self.execute( *args, **kwargs)
