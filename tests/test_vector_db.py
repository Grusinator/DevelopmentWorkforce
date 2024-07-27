import tempfile
from pathlib import Path
import pytest

from src.util_tools.vector_db import VectorDB


class TestVectorDB:

    @pytest.fixture
    def temp_repo(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some Python files in the temporary directory
            file_contents = {
                "file1.py": "def add(a, b):\n    return a + b\n",
                "file2.py": "def subtract(a, b):\n    return a - b\n",
                "file3.py": "def multiply(a, b):\n    return a * b\n",
                "nested/file4.py": "def divide(a, b):\n    return a / b\n",
                "nested/deep/file5.py": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)\n",
                ".git/file6.py": "def ignored_function():\n    return None\n"
            }

            for filename, content in file_contents.items():
                file_path = temp_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)

            yield temp_path  # Yield the temporary directory path for use in the test

    def test_load_repo(self, temp_repo):
        vector_db = VectorDB()
        vector_db.load_repo(temp_repo)

        assert len(vector_db.documents) == 5
        assert len(vector_db.filenames) == 5

    def test_fetch_most_relevant_docs(self, temp_repo):
        vector_db = VectorDB()
        vector_db.load_repo(temp_repo)

        query = "def fibonacci(n):"
        results = vector_db.fetch_most_relevant_docs(query, n=1)

        assert len(results) == 1
        assert "nested\\deep\\file5.py" in results.keys()

    def test_fetch_top_n_relevant_docs(self, temp_repo):
        vector_db = VectorDB()
        vector_db.load_repo(temp_repo)

        query = "def"
        results = vector_db.fetch_most_relevant_docs(query, n=3)

        assert len(results) == 3

    def test_ignore_folders(self, temp_repo):
        vector_db = VectorDB()
        vector_db.ignore_folders = [".git"]
        vector_db.load_repo(temp_repo)

        assert len(vector_db.documents) == 5
        assert len(vector_db.filenames) == 5

    def find_repo_root(self, path: Path = None) -> Path:
        if path is None:
            path = Path.cwd()  # Start from the current working directory

        for parent in path.resolve().parents:
            if (parent / ".git").is_dir():
                return parent
        return None

    def test_load_repo_full(self):
        vector_db = VectorDB()
        root = Path.cwd()
        vector_db.load_repo(root)
        assert len(vector_db.documents) > 10
