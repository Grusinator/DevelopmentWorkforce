import os
import time
import uuid
from pathlib import Path
import git
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel


class GitManager:

    def clone_and_checkout_branch(self, remote_url, repo_dir, branch_name):
        if self.git_repo_exists(repo_dir):
            self._get_existing_repo(repo_dir, branch_name)
        else:
            self._clone_and_create_branch(remote_url, repo_dir, branch_name)

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

    def _clone_and_create_branch(self, remote_repo_url, repo_path, branch_name):
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = git.Repo.clone_from(remote_repo_url, str(repo_path))
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
