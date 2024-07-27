from typing import List

from azure.devops.connection import Connection
from azure.devops.exceptions import AzureDevOpsServiceError
from azure.devops.v7_1.git import GitPullRequest, GitRefUpdate, \
    GitPullRequestSearchCriteria, GitClient
from msrest.authentication import BasicAuthentication

from src.ado_integrations.repos.ado_repo import AdoRepo
from src.ado_integrations.repos.base_repos_api import BaseAdoReposApi
from src.ado_integrations.repos.ado_repos_models import CreatePullRequestInput, AdoPullRequest, \
    PullRequestComment, ProjectModel, RepositoryModel

from azure.devops.v7_1.git.models import Comment, CommentThread


class ADOReposWrapperApi(BaseAdoReposApi):
    def __init__(self, pat, ado_org_name, project_name, repo_name):
        self.organization_url = "https://dev.azure.com/" + ado_org_name
        self.personal_access_token = pat
        self.project_name = project_name
        self.repo_name = repo_name
        credentials = BasicAuthentication('', self.personal_access_token)
        self.connection = Connection(base_url=self.organization_url, creds=credentials)
        self.client: GitClient = self.connection.clients.get_git_client()
        self.build_client = self.connection.clients.get_build_client()
        self.core_client = self.connection.clients.get_core_client()
        self.ado_repo_api = AdoRepo(self.repo_name)

    def create_pull_request(self, pr_input: CreatePullRequestInput) -> int:
        repository_id = self.get_repository_id()
        # Define the pull request object
        pr = GitPullRequest(
            source_ref_name=f"refs/heads/{pr_input.source_branch}",
            target_ref_name=f"refs/heads/{pr_input.target_branch}",
            title=pr_input.title,
            description=pr_input.description
        )
        try:
            # Attempt to create a new pull request
            created_pr = self.client.create_pull_request(pr, repository_id, self.project_name)
            return created_pr.pull_request_id
        except AzureDevOpsServiceError as e:
            if "TF401179" in str(e):
                # If an active pull request already exists, search for it
                search_criteria = GitPullRequestSearchCriteria(
                    source_ref_name=pr.source_ref_name,
                    target_ref_name=pr.target_ref_name,
                    status="active"
                )
                existing_prs = self.client.get_pull_requests(
                    repository_id, search_criteria, project=self.project_name)
                if existing_prs:
                    # Return the ID of the first matching pull request found
                    return existing_prs[0].pull_request_id
            else:
                # If the error is not about an existing pull request, re-raise it
                raise

    def get_pull_request(self, pr_id: int) -> AdoPullRequest:
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id)
        return AdoPullRequest(
            id=pr.pull_request_id,
            title=pr.title,
            description=pr.description,
            source_branch=pr.source_ref_name,
            target_branch=pr.target_ref_name,
            status=pr.status
        )

    def update_pull_request_description(self, pr_id: int, description: str):
        repository_id = self.get_repository_id()
        pr = self.client.get_pull_request(repository_id, pr_id)
        pr.description = description
        self.ado_repo_api.update_pull_request(pr_id, description=description)

    def list_pull_requests(self, repository_id: str, status: str = None) -> List[AdoPullRequest]:
        search_criteria = GitPullRequestSearchCriteria(status=status)
        prs = self.client.get_pull_requests(repository_id, search_criteria, project=self.project_name)
        return [AdoPullRequest(
            id=pr.pull_request_id,
            title=pr.title,
            description=pr.description,
            source_branch=pr.source_ref_name,
            target_branch=pr.target_ref_name,
            status=pr.status
        ) for pr in prs]

    def complete_pull_request(self, pr_id: int) -> None:
        return self.ado_repo_api.approve_pull_request(pr_id)
        # repository_id = self.get_repository_id()
        # pr = self.client.get_pull_request(repository_id, pr_id, project=self.project_name)
        # completion_options = GitPullRequestCompletionOptions(delete_source_branch=False)
        # pr.status = "completed"  # Assuming 'completed' is a valid status; adjust as necessary
        # self.client.update_pull_request(pr, repository_id, pr_id, project=self.project_name,
        #                                 completion_options=completion_options)

    def abandon_pull_request(self, pr_id: int) -> None:
        return self.ado_repo_api.abandon_pull_request(pr_id)
        # repository_id = self.get_repository_id()
        # pr = self.client.get_pull_request(repository_id, pr_id)
        # pr.status = 'abandoned'
        # self.client.update_pull_request(pr, repository_id, pr_id)

    def create_branch(self, repository_id: str, branch_name: str, source_branch: str) -> None:
        refs = self.client.get_refs(repository_id, filter=f"heads/{source_branch}")
        if not refs:
            raise ValueError(f"Source branch '{source_branch}' not found.")
        source_ref = refs[0]
        new_ref = GitRefUpdate(
            name=f"refs/heads/{branch_name}",
            old_object_id="0000000000000000000000000000000000000000",
            new_object_id=source_ref.object_id
        )
        self.client.update_refs(ref_updates=[new_ref], repository_id=repository_id, project=self.project_name)

    def branch_exists(self, repository_id: str, branch_name: str) -> bool:
        refs = self.client.get_refs(repository_id, filter=f"heads/{branch_name}")
        return len(refs) > 0

    def get_repository_id(self) -> str:
        # Assuming a single repository for simplicity. Adapt as necessary.
        repositories = self.client.get_repositories(self.project_name)
        repo = [repo for repo in repositories if repo.name == self.repo_name][0]
        return repo.id if repositories else None

    def add_pull_request_comment(self, pr_id: int, content: str) -> int:
        repository_id = self.get_repository_id()
        comment = Comment(content=content)
        comment_thread = CommentThread(
            comments=[comment]
        )
        created_thread = self.client.create_thread(comment_thread, repository_id, pr_id, project=self.project_name)
        return created_thread.id

    def get_pull_request_comments(self, pr_id: int) -> List[PullRequestComment]:
        repository_id = self.get_repository_id()
        threads = self.client.get_threads(repository_id, pr_id, project=self.project_name)
        comments = []
        for thread in threads:
            for comment in thread.comments:
                comments.append(PullRequestComment(
                    id=comment.id,
                    content=comment.content,
                    created_by=comment.author.display_name,
                    created_date=comment.published_date
                ))
        return comments

    def run_build(self, pr_id: int) -> int:
        build_definition_id = pr_id
        build = {
            'definition': {'id': build_definition_id}
        }
        build = self.build_client.queue_build(build, project=self.project_name)
        return build.id

    def get_build_status(self, pr_id: int) -> str:
        builds = self.build_client.get_builds(project=self.project_name, definitions=[pr_id])
        if not builds:
            return "No builds found"
        build = builds[0]
        return build.status

    def get_projects(self) -> List[ProjectModel]:
        projects = self.core_client.get_projects()
        project_list = []
        for project in projects:
            project_list.append(ProjectModel(
                name=project.name,
                id=project.id,
                source_id=project.id,
                description=project.description,
                url=project.url
            ))
        return project_list

    def get_repositories(self, project_id: str) -> List[RepositoryModel]:
        repositories = self.client.get_repositories(project_id)
        repo_list = []
        for repo in repositories:
            repo_list.append(RepositoryModel(
                id=repo.id,
                source_id=repo.id,  # TODO ids should be reserved for internal db id. consider delete
                name=repo.name,
                git_url=repo.remote_url,
                project=ProjectModel(
                    name=repo.project.name,
                    id=repo.project.id,
                    source_id=repo.project.id,
                    description=repo.project.description,
                    url=repo.project.url
                )
            ))
        return repo_list
