from pathlib import Path

from pathlib import Path

space = '    '
branch = '│   '
tee = '├── '
last = '└── '


# Example, but does not exclude the git folder
# def tree(dir_path: Path, prefix: str=''):
#     """A recursive generator, given a directory Path object
#     will yield a visual tree structure line by line
#     with each line prefixed by the same characters
#     """
#     contents = list(dir_path.iterdir())
#     # contents each get pointers that are ├── with a final └── :
#     pointers = [tee] * (len(contents) - 1) + [last]
#     for pointer, path in zip(pointers, contents):
#         yield prefix + pointer + path.name
#         if path.is_dir(): # extend the prefix and recurse:
#             extension = branch if pointer == tee else space
#             # i.e. space because last, └── , above so no more |
#             yield from tree(path, prefix=prefix+extension)

class DirectoryStructure:
    def __init__(self, root_dir):
        self.ignore_list = [".git", "__pycache__"]
        self.ignore_ext_list = [".pyc",]
        self.root_path = Path(root_dir)
        self.directory_structure = self._dir_to_dict(self.root_path)

    def _dir_to_dict(self, path):
        directory = {'name': path.name}
        if path.is_dir():
            directory['type'] = 'directory'
            directory['children'] = [self._dir_to_dict(child)
                                     for child in path.iterdir()
                                     if child.name not in self.ignore_list
                                     and not any(child.name.endswith(ext) for ext in self.ignore_ext_list)]
        else:
            directory['type'] = 'file'
        return directory

    def get_formatted_directory_structure(self) -> str:
        lines = self._format_directory_structure(self.directory_structure)
        return "\n".join(lines)

    def _format_directory_structure(self, directory, prefix=''):
        """A recursive generator, given a directory dictionary
        will yield a visual tree structure line by line
        with each line prefixed by the same characters
        """

        lines = []
        if directory['type'] == 'directory':
            lines.append(f"{prefix}{directory['name']}/")
            children = directory.get('children', [])
            pointers = [tee] * (len(children) - 1) + [last]
            for pointer, child in zip(pointers, children):
                if child['type'] == 'directory':
                    lines.append(f"{prefix}{pointer}{child['name']}/")
                    extension = branch if pointer == tee else space
                    lines.extend(self._format_directory_structure(child, prefix=prefix + extension))
                else:
                    lines.append(f"{prefix}{pointer}{child['name']}")
        else:
            lines.append(f"{prefix}{directory['name']}")
        return lines
