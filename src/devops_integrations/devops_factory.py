from src.devops_integrations.models import ProjectAuthentication, DevOpsSource
from src.devops_integrations.pull_requests.ado_pull_requests_api import ADOPullRequestsApi
from src.devops_integrations.pull_requests.base_pull_requests_api import BasePullRequestsApi
from src.devops_integrations.pull_requests.mock_pull_requests_api import MockPullRequestsApi
from src.devops_integrations.repos.ado_repos_api import ADOReposApi
from src.devops_integrations.repos.base_repos_api import BaseReposApi
from src.devops_integrations.repos.mock_repos_api import MockReposApi
from src.devops_integrations.workitems.ado_workitems_api import ADOWorkitemsApi
from src.devops_integrations.workitems.base_workitems_api import BaseWorkitemsApi
from src.devops_integrations.workitems.mock_workitems_api import MockWorkitemsApi


class DevOpsFactory:

    def __init__(self, auth: ProjectAuthentication, devops_source: DevOpsSource):
        self.auth = auth
        self.devops_source = devops_source
        self.mock_pull_requests_api = MockPullRequestsApi()
        self.mock_repos_api = MockReposApi()
        self.mock_workitems_api = MockWorkitemsApi()

    def get_workitems_api(self) -> BaseWorkitemsApi:
        if self.devops_source == DevOpsSource.ADO:
            return ADOWorkitemsApi(self.auth)
        elif self.devops_source == DevOpsSource.GITHUB:
            raise NotImplementedError("GitHub workitems API is not implemented yet.")
        elif self.devops_source == DevOpsSource.GITLAB:
            raise NotImplementedError("GitLab workitems API is not implemented yet.")
        elif self.devops_source == DevOpsSource.MOCK:
            return self.mock_workitems_api
        else:
            raise ValueError(f"Unknown platform: {self.devops_source}")

    def get_repos_api(self) -> BaseReposApi:
        if self.devops_source == DevOpsSource.ADO:
            return ADOReposApi(self.auth)
        elif self.devops_source == DevOpsSource.GITHUB:
            raise NotImplementedError("GitHub repos API is not implemented yet.")
        elif self.devops_source == DevOpsSource.GITLAB:
            raise NotImplementedError("GitLab repos API is not implemented yet.")
        elif self.devops_source == DevOpsSource.MOCK:
            return self.mock_repos_api
        else:
            raise ValueError(f"Unknown platform: {self.devops_source}")

    def get_pullrequests_api(self) -> BasePullRequestsApi:
        if self.devops_source == DevOpsSource.ADO:
            return ADOPullRequestsApi(self.auth)
        elif self.devops_source == DevOpsSource.GITHUB:
            raise NotImplementedError("GitHub pull requests API is not implemented yet.")
        elif self.devops_source == DevOpsSource.GITLAB:
            raise NotImplementedError("GitLab pull requests API is not implemented yet.")
        elif self.devops_source == DevOpsSource.MOCK:
            return self.mock_pull_requests_api
        else:
            raise ValueError(f"Unknown platform: {self.devops_source}")
