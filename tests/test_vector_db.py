import os
import tempfile
from pathlib import Path

import pytest
from src.util_tools.vector_db import VectorDB


@pytest.fixture
def temp_repo():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some Python files in the temporary directory
        file_contents = {
            "file1.py": "def add(a, b):\n    return a + b\n",
            "file2.py": "def subtract(a, b):\n    return a - b\n",
            "file3.py": "def multiply(a, b):\n    return a * b\n",
            "file4.py": "def divide(a, b):\n    return a / b\n",
            "file5.py": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n"
        }

        for filename, content in file_contents.items():
            with open(temp_path / filename, 'w') as f:
                f.write(content)

        yield temp_path  # Yield the temporary directory path for use in the test


def test_load_repo(temp_repo):
    vector_db = VectorDB()
    vector_db.load_repo(temp_repo)

    assert len(vector_db.documents) == 5
    assert len(vector_db.filenames) == 5


def test_fetch_most_relevant_docs(temp_repo):
    vector_db = VectorDB()
    vector_db.load_repo(temp_repo)

    query = "def fibonacci(n):"
    results = vector_db.fetch_most_relevant_docs(query, n=1)

    assert len(results) == 1
    assert "file5.py" in results[0][0]


def test_fetch_top_n_relevant_docs(temp_repo):
    vector_db = VectorDB()
    vector_db.load_repo(temp_repo)

    query = "def"
    results = vector_db.fetch_most_relevant_docs(query, n=3)

    assert len(results) == 3


def find_repo_root(path: Path = None) -> Path:
    if path is None:
        path = Path.cwd()  # Start from the current working directory

    for parent in path.resolve().parents:
        if (parent / ".git").is_dir():
            return parent
    return None


def test_load_repo_full():
    vector_db = VectorDB()
    root = Path.cwd()
    vector_db.load_repo(root)
    assert len(vector_db.documents) > 10



