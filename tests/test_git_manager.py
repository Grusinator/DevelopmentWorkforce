import pytest
from git import Repo
from git.exc import GitCommandError
from src.git_manager import GitManager

@pytest.mark.django_db
class TestGitManager:

    @pytest.fixture(autouse=True)
    def setup(self, agent_model):
        self.git_manager = GitManager(pat=agent_model.pat)

    def test_clone_and_checkout_branch(self, workspace_dir, repository_model):
        repo_dir = workspace_dir / "test_repo"
        branch_name = "test-branch"

        result = self.git_manager.clone_and_checkout_branch(repository_model.git_url, repo_dir, branch_name)

        assert isinstance(result, Repo)
        assert (repo_dir / ".git").is_dir()
        
        repo = Repo(repo_dir)
        assert repo.active_branch.name == branch_name
        assert f"origin/{branch_name}" in [ref.name for ref in repo.references]

        # Clean up: delete the remote branch
        repo.git.push('origin', '--delete', branch_name)

    def test_push_changes(self, workspace_dir_w_git, repository_model):
        branch_name = "test-branch"
        commit_message = "Test commit"

        # Create a test file
        test_file = workspace_dir_w_git / "test_file.txt"
        test_file.write_text("This is a test file")

        # Initialize the repo and set the remote URL
        repo = Repo(workspace_dir_w_git)
        origin = repo.create_remote('origin', url=repository_model.git_url)

        # Push changes
        self.git_manager.push_changes(workspace_dir_w_git, branch_name, commit_message)

        # Verify that the changes were pushed
        remote_branches = origin.fetch()
        assert any(ref.name == f'origin/{branch_name}' for ref in remote_branches)

        # Verify the commit
        latest_commit = repo.head.commit
        assert latest_commit.message == commit_message
        assert "test_file.txt" in latest_commit.stats.files

        # Clean up: delete the remote branch
        repo.git.push('origin', '--delete', branch_name)

    def test_clone_failure(self, workspace_dir):
        repo_dir = workspace_dir / "test_repo"
        branch_name = "test-branch"
        invalid_url = "https://invalid-url.com/nonexistent-repo.git"

        with pytest.raises(GitCommandError):
            self.git_manager.clone_and_checkout_branch(invalid_url, repo_dir, branch_name)