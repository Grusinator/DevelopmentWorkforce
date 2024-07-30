import os
from pathlib import Path
from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class VectorDB:
    def __init__(self, ignore_folders=None, ignore_extensions=None):
        self.documents = []
        self.filenames = []
        self.vectorizer = TfidfVectorizer()
        self.vectors = None
        self.ignore_folders = set(ignore_folders) if ignore_folders else {".git", ".vscode", ".idea"}
        self.ignore_extensions = set(ignore_extensions) if ignore_extensions else {".pyc", ".sqlite", ".env"}

    def _is_valid_file(self, file_path: Path):
        if file_path.suffix in self.ignore_extensions:
            return False
        return True

    def find_files(self, repo_path: Path):
        files = []
        for root, dirs, file_names in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            for file_name in file_names:
                file_path = Path(root) / file_name
                if self._is_valid_file(file_path):
                    relative_path = file_path.relative_to(repo_path)
                    files.append(relative_path)
        return files

    def load_files(self, files: List[Path], repo_path: Path):
        self.documents = []
        self.filenames = []
        for file_path in files:
            try:
                with open(repo_path / file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append(content)
                    self.filenames.append(str(file_path))
            except UnicodeDecodeError:
                print(f"Skipping binary file {file_path}")
        self.vectors = self.vectorizer.fit_transform(self.documents)

    def load_repo(self, repo_path: Path):
        files = self.find_files(repo_path)
        self.load_files(files, repo_path)

    def fetch_most_relevant_docs(self, query: str, n: int = 5) -> Dict[str, str]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors).flatten()
        relevant_indices = similarities.argsort()[-n:][::-1]
        relevant_docs = {self.filenames[idx]: self.documents[idx] for idx in relevant_indices}
        return relevant_docs

    def format_files_as_text(self, docs):
        files_as_text = [f"### {filename} ###: \n  {content}" for filename, content in docs.items()]
        files_joined = "\n-------------------------------------------\n\n".join(files_as_text)
        return files_joined




