from pathlib import Path

from src.util_tools.vector_db import VectorDB


class TestVectorDB:

    def test_load_repo(self, workspace_dir_with_codebase):
        vector_db = VectorDB()
        vector_db.load_repo(workspace_dir_with_codebase)

        assert len(vector_db.documents) == 5
        assert len(vector_db.filenames) == 5

    def test_fetch_most_relevant_docs(self, workspace_dir_with_codebase):
        vector_db = VectorDB()
        vector_db.load_repo(workspace_dir_with_codebase)

        query = "def fibonacci(n):"
        results = vector_db.fetch_most_relevant_docs(query, n=1)

        assert len(results) == 1
        assert "nested\\deep\\file5.py" in results.keys()

    def test_fetch_top_n_relevant_docs(self, workspace_dir_with_codebase):
        vector_db = VectorDB()
        vector_db.load_repo(workspace_dir_with_codebase)

        query = "def"
        results = vector_db.fetch_most_relevant_docs(query, n=3)

        assert len(results) == 3

    def test_ignore_folders(self, workspace_dir_with_codebase):
        vector_db = VectorDB()
        vector_db.ignore_folders = [".git"]
        vector_db.load_repo(workspace_dir_with_codebase)

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
