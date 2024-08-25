import pytest
from git import Repo
from git.exc import GitCommandError
from src.git_manager import GitManager

@pytest.mark.django_db
class TestGitManager:

    def test_clone_and_checkout_branch(self, workspace_dir, repository_model, git_manager):
        repo_dir = workspace_dir / "test_repo"
        branch_name = "test-branch"

        result = git_manager.clone_and_checkout_branch(repository_model.git_url, repo_dir, branch_name)

        assert isinstance(result, Repo)
        assert (repo_dir / ".git").is_dir()
        
        repo = Repo(repo_dir)
        assert repo.active_branch.name == branch_name
        assert f"{branch_name}" in [ref.name for ref in repo.references]

        git_manager.delete_remote_branch(repo_dir, branch_name)

    @pytest.mark.skip("not important rigth now")
    def test_push_changes(self, workspace_dir_w_git, repository_model, git_manager, setup_feature_branch):
        branch_name = setup_feature_branch
        commit_message = "Test commit"

        # Create a test file
        test_file = workspace_dir_w_git / "test_file.txt"
        test_file.write_text("This is a test file")

        # Initialize the repo and set the remote URL

        # Push changes
        git_manager.push_changes(workspace_dir_w_git, branch_name, commit_message)


        git_manager.delete_remote_branch(workspace_dir_w_git, branch_name)

    def test_clone_failure(self, workspace_dir, git_manager):
        repo_dir = workspace_dir / "test_repo"
        branch_name = "test-branch"
        invalid_url = "https://invalid-url.com/nonexistent-repo.git"

        with pytest.raises(GitCommandError):
            git_manager.clone_and_checkout_branch(invalid_url, repo_dir, branch_name)