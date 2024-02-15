import subprocess
import os
from dotenv import load_dotenv

class GitHelper:
    def __init__(self):
        self.repo_path = os.getenv('REPO_PATH')
        self.repo_url = os.getenv('REPO_URL')

    def run_git_command(self, command):
        try:
            output = subprocess.check_output(['git', '-C', self.repo_path] + command.split(), stderr=subprocess.STDOUT)
            return output.decode().strip()
        except subprocess.CalledProcessError as e:
            return e.output.decode().strip()

    def clone(self):
        return self.run_git_command(f'clone {self.repo_url}')

    def pull(self):
        return self.run_git_command('pull')

    def add(self, file_path):
        return self.run_git_command(f'add {file_path}')

    def commit(self, message):
        return self.run_git_command(f'commit -m "{message}"')

    def push(self):
        return self.run_git_command('push')

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    git = GitHelper()
    git.clone()
    git.pull()
    git.add('file.txt')
    git.commit('Added file.txt')
    git.push()