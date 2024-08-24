import os
import time
from pathlib import Path
import git
from git import Repo
from git.exc import GitCommandError
from loguru import logger

from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel


class GitManager:
    def __init__(self, pat=None):
        self.pat = pat

    def set_pat(self, pat):
        self.pat = pat

    def _get_repo_url_with_auth(self, remote_url):
        if self.pat:
            # Split the URL into its components
            protocol, _, domain_and_path = remote_url.partition('://')
            # Remove any existing username from the URL
            if '@' in domain_and_path:
                _, domain_and_path = domain_and_path.split('@', 1)
            # Insert the PAT into the URL
            return f'{protocol}://{self.pat}@{domain_and_path}'
        return remote_url

    def clone_and_checkout_branch(self, remote_url, repo_dir, branch_name) -> git.Repo:
        repo_dir = Path(repo_dir)
        if self.git_repo_exists(repo_dir):
            return self._get_existing_repo(repo_dir, branch_name)
        else:
            return self._clone_and_create_branch(remote_url, repo_dir, branch_name)

    def git_repo_exists(self, repo_path):
        return repo_path.exists() and any(repo_path.iterdir())

    def _get_existing_repo(self, repo_path, branch_name) -> git.Repo:
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
        auth_url = self._get_repo_url_with_auth(remote_repo_url)
        try:
            repo = Repo.clone_from(auth_url, str(repo_path))
            new_branch = repo.create_head(branch_name)
            repo.head.reference = new_branch
            repo.head.reset(index=True, working_tree=True)
            return repo
        except GitCommandError as e:
            print(f"Git clone failed: {e}")
            raise

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
        
        if branch_name not in repo.branches:
            repo.git.checkout('-b', branch_name)
        else:
            repo.git.checkout(branch_name)
        
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        
        origin = repo.remote(name='origin')
        auth_url = self._get_repo_url_with_auth(origin.url)
        origin.set_url(auth_url)
        
        try:
            origin.push(branch_name)
        except GitCommandError as e:
            logger.error(f"Failed to push changes: {e}")
            raise

    def delete_branch(self, repo_path, branch_name):
        repo = git.Repo(str(repo_path))
        repo.git.branch('-D', branch_name)
        return True