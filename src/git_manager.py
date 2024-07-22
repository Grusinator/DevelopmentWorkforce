import os

import git
from pathlib import Path

from src.ado_integrations.workitems.ado_workitem_models import AdoWorkItem


class GitManager:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.workspace_root_dir = Path(os.getenv("WORKSPACE_DIR"))

    def clone_and_setup(self, work_item: AdoWorkItem):
        branch_name = f"{work_item.id}-{work_item.title.replace(' ', '_')}"
        repo_path = self.workspace_root_dir / branch_name

        if repo_path.exists() and any(repo_path.iterdir()):
            try:
                repo = git.Repo(str(repo_path))
                if branch_name in [b.name for b in repo.branches]:
                    # If branch exists, checkout to it
                    repo.git.checkout(branch_name)
                else:
                    if repo.active_branch.name == 'main':
                        repo.remotes.origin.pull()
                    else:
                        # If not on 'main', checkout 'main' and pull the latest changes
                        repo.git.checkout('main')
                        repo.remotes.origin.pull()
                    # Create and switch to a new branch for the work item
                    new_branch = repo.create_head(branch_name)
                    repo.head.reference = new_branch
                    repo.head.reset(index=True, working_tree=True)
            except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError, ValueError):
                # If the directory is not a git repo or 'main' branch doesn't exist, clone and setup
                repo_path.mkdir(parents=True, exist_ok=True)
                repo = git.Repo.clone_from(self.repo_url, str(repo_path))
                # Create and switch to a new branch for the work item
                new_branch = repo.create_head(branch_name)
                repo.head.reference = new_branch
                repo.head.reset(index=True, working_tree=True)
        else:
            # If the directory doesn't exist, clone and setup
            repo_path.mkdir(parents=True, exist_ok=True)
            repo = git.Repo.clone_from(self.repo_url, str(repo_path))
            # Create and switch to a new branch for the work item
            new_branch = repo.create_head(branch_name)
            repo.head.reference = new_branch
            repo.head.reset(index=True, working_tree=True)

        return repo_path

    def push_changes(self, repo_path, branch_name, commit_message):
        repo = git.Repo(str(repo_path))
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push(branch_name)
