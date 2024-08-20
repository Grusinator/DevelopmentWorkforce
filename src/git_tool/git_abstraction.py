import logging
from pathlib import Path

from git import Repo, exc

from loguru import logger


class GitAbstraction:
    def __init__(self, repo_url, repo_path: Path, main_branch_name="main"):
        self.main_branch_name = main_branch_name
        self.repo_url = repo_url
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except (exc.InvalidGitRepositoryError, exc.NoSuchPathError):
            logger.debug("No git repository found at the specified path.")
            self.repo = None

    def clone_repo(self):
        if isinstance(self.repo, Repo):
            raise ValueError("Repository already exists at the specified path.")
        self.repo = Repo.clone_from(self.repo_url, self.repo_path)
        logger.info(f"Repo cloned successfully from {self.repo_url} into {self.repo_path}")

    def create_and_checkout_branch(self, branch_name):
        self.repo.git.checkout(self.main_branch_name)
        self.repo.git.branch(branch_name)
        self.repo.git.checkout(branch_name)
        logger.info(f"Branch '{branch_name}' created and checked out.")

    def pull(self):
        origin = self.repo.remote(name='origin')
        origin.pull()
        logger.info("Repo pulled successfully.")

    def push(self):
        origin = self.repo.remotes.origin
        current_branch = self.repo.head.ref.name
        origin.push(refspec=f'{current_branch}:{current_branch}', set_upstream=True)
        logger.info("Repo pushed successfully.")

    def commit_all(self, message="Auto commit"):
        self.repo.git.add(A=True)
        self.repo.index.commit(message)
        logger.info("All changes committed.")
