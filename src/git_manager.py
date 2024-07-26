import os
import time
from pathlib import Path
import git
from src.ado_integrations.workitems.ado_workitem_models import WorkItem


class GitManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.workspace_root_dir = Path(os.getenv("WORKSPACE_DIR"))

    def clone_and_setup(self, work_item: WorkItem):
        branch_name = f"{work_item.id}-{work_item.title.replace(' ', '_')}"
        repo_path = self.workspace_root_dir / branch_name

        if self.git_repo_exists(repo_path):
            self._get_existing_repo(repo_path, branch_name)
        else:
            self._clone_and_create_branch(repo_path, branch_name)

        return repo_path

    def git_repo_exists(self, repo_path):
        return repo_path.exists() and any(repo_path.iterdir())

    def _get_existing_repo(self, repo_path, branch_name):
        repo = git.Repo(str(repo_path))
        for _ in range(5):
            try:
                self._checkout_or_create_branch(repo, branch_name)
                break
            except OSError as e:
                if "could not be obtained" in str(e):
                    time.sleep(1)
                else:
                    raise
        else:
            raise OSError("Failed to obtain lock after multiple attempts")
        return repo

    def _clone_and_create_branch(self, repo_path, branch_name):
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = git.Repo.clone_from(self.repo_url, str(repo_path))
        new_branch = repo.create_head(branch_name)
        repo.head.reference = new_branch
        repo.head.reset(index=True, working_tree=True)
        return repo

    def _checkout_or_create_branch(self, repo, branch_name):
        if branch_name in [b.name for b in repo.branches]:
            repo.git.checkout(branch_name)
        else:
            if repo.active_branch.name != 'main':
                repo.git.checkout('main')
                repo.remotes.origin.pull()
            new_branch = repo.create_head(branch_name)
            repo.head.reference = new_branch
            repo.head.reset(index=True, working_tree=True)

    def push_changes(self, repo_path, branch_name, commit_message):
        repo = git.Repo(str(repo_path))
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push(branch_name)
