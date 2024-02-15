import pytest
import os
from dotenv import load_dotenv
import tempfile

from ado_integrations.ado_repo import GitHelper

@pytest.fixture
def temp_repo_folder():
    # Create a temporary folder for the repository
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set the REPO_PATH environment variable to the temporary folder
        os.environ['REPO_PATH'] = temp_dir
        yield temp_dir

@pytest.fixture
def git_helper(temp_repo_folder):
    # Load environment variables from .env file
    load_dotenv()
    git = GitHelper()
    yield git

# def test_clone(git_helper):
#     # Test the clone method
#     assert git_helper.clone() == "Cloning repository..."

# def test_pull(git_helper):
#     # Test the pull method
#     assert git_helper.pull() == "Pulling changes..."

# def test_add(git_helper):
#     # Test the add method
#     assert git_helper.add('file.txt') == "Adding file.txt..."

# def test_commit(git_helper):
#     # Test the commit method
#     assert git_helper.commit('Added file.txt') == "Committing changes..."

# def test_push(git_helper):
#     # Test the push method
#     assert git_helper.push() == "Pushing changes..."
