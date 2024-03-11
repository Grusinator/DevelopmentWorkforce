from pathlib import Path

import pytest
from development_workforce.git_tool.git_abstraction import GitAbstraction
from tempfile import TemporaryDirectory
import shutil
import gc
import time


@pytest.fixture(scope="function")
def git_abstraction():
    with TemporaryDirectory() as temp_dir:
        repo_url = "https://github.com/Grusinator/ai-test-project.git"
        repo_path = Path(temp_dir) / "repo"
        repo_path.mkdir()
        git = GitAbstraction(repo_url, repo_path)
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
