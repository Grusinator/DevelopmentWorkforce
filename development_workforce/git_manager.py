import os

import git
from pathlib import Path

from development_workforce.ado_integrations.workitems.ado_workitem_models import AdoWorkItem


class GitManager:
    def __init__(self):
        self.repo_url = os.getenv("REPO_URL")
        self.workspace_root_dir = Path(os.getenv("WORKSPACE_DIR"))

    def clone_and_setup(self, work_item: AdoWorkItem):
        # Format the branch name and directory as "(id)-(title)"
        branch_name = f"{work_item.id}-{work_item.title.replace(' ', '_')}"
        repo_path = self.workspace_root_dir / branch_name

        # Ensure the specific workspace directory for this branch exists
        repo_path.mkdir(parents=True, exist_ok=True)

        # Clone the repository into the specified directory and setup the branch
        repo = git.Repo.clone_from(self.repo_url, str(repo_path))
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
