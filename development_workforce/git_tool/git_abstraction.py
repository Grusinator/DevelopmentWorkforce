import os
from pathlib import Path

from git import Repo, exc


class GitAbstraction:
    def __init__(self, repo_url, repo_path: Path):
        self.main_branch_name = 'main'
        self.repo_url = repo_url
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except exc.InvalidGitRepositoryError:
            self.repo = None

    def clone_repo(self):
        try:
            print(f"Cloning repo from {self.repo_url} into {self.repo_path}")
            self.repo = Repo.clone_from(self.repo_url, self.repo_path)
            print("Repo cloned successfully.")
        except exc.GitCommandError as e:
            print(f"Error cloning repo: {e}")

    def create_and_checkout_branch(self, branch_name):
        try:
            self.repo.git.checkout(self.main_branch_name)
            self.repo.git.branch(branch_name)
            self.repo.git.checkout(branch_name)
            print(f"Branch '{branch_name}' created and checked out.")
        except exc.GitCommandError as e:
            print(f"Error creating and checking out branch: {e}")

    def pull(self):
        try:
            repo = Repo(self.repo_path)
            origin = repo.remote(name='origin')
            origin.pull()
            print("Repo pulled successfully.")
        except exc.GitCommandError as e:
            print(f"Error pulling repo: {e}")

    def push(self):
        try:
            origin = self.repo.remotes.origin
            origin.push()
            print("Repo pushed successfully.")
        except exc.GitCommandError as e:
            print(f"Error pushing repo: {e}")

    def commit_all(self, message="Auto commit"):
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(message)
            print("All changes committed.")
        except exc.GitCommandError as e:
            print(f"Error committing: {e}")
