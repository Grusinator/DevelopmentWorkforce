
import pytest
from src.git_tool.git_abstraction import GitAbstraction


@pytest.fixture(scope="function")
def git_abstraction(create_test_workspace_repo):
    repo_url = "https://github.com/Grusinator/ai-test-project.git"
    git = GitAbstraction(repo_url, create_test_workspace_repo, main_branch_name="automated_testing")
    yield git


@pytest.fixture
def git_cloned_repo(git_abstraction):
    git_abstraction.clone_repo()
    yield git_abstraction


@pytest.fixture
def add_test_file(git_cloned_repo):
    test_file_path = git_cloned_repo.repo_path / "test_file.py"
    with open(test_file_path, "w") as f:
        f.write("print('This is a test file')")
    yield test_file_path


@pytest.fixture
def git_with_commit(git_cloned_repo, add_test_file):
    git_cloned_repo.commit_all("Test commit")
    yield git_cloned_repo


def test_clone_repo(git_abstraction):
    git_abstraction.clone_repo()
    # Add assertions to check if the repository was cloned successfully


def test_commit_all(git_cloned_repo, add_test_file):
    message = "Test commit"
    git_cloned_repo.commit_all(message)


def test_push(git_with_commit):
    git_with_commit.push()
    # Add assertions to check if the changes were pushed successfully


def test_pull(git_cloned_repo):
    git_cloned_repo.pull()
    # Add assertions to check if the repository was pulled successfully


def test_clone_branch_add_commit_push_pull(git_cloned_repo, add_test_file):
    git_cloned_repo.create_and_checkout_branch("test_branch")
    git_cloned_repo.commit_all("Test commit")
    git_cloned_repo.push()
