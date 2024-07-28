from pathlib import Path
from typing import List


class ReadFiles:
    def __init__(self, workspace_dir):
        self.workspace_dir = Path(workspace_dir)

    def read_files(self, relative_dirs):
        file_contents = {}
        for relative_dir in relative_dirs:
            file_path = self.workspace_dir / relative_dir
            if file_path.is_file():
                with open(file_path, 'r') as file:
                    file_contents[relative_dir] = file.read()
        return file_contents

    def format_files(self, file_contents):
        files_as_text = [f"### {filename} ###: \n  {content}" for filename, content in file_contents.items()]
        return "\n-------------------------------------------\n\n".join(files_as_text)

    def read_and_format_files(self, relative_dirs: List[str]):
        files = self.read_files(relative_dirs)
        return self.format_files(files)
