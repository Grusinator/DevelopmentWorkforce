from pathlib import Path


class DirectoryStructure:
    def __init__(self, root_dir):
        self.root_path = Path(root_dir)
        self.directory_structure = self._dir_to_dict(self.root_path)

    def _dir_to_dict(self, path):
        directory = {'name': path.name}
        if path.is_dir():
            directory['type'] = 'directory'
            directory['children'] = [self._dir_to_dict(child) for child in path.iterdir()]
        else:
            directory['type'] = 'file'
        return directory

    def get_directory_structure(self):
        return self.directory_structure

    def format_directory_structure(self):
        return self._format_directory_structure(self.directory_structure)

    def _format_directory_structure(self, directory, indent=0):
        lines = []
        indent_str = ' ' * 4 * indent
        if directory['type'] == 'directory':
            lines.append(f"{indent_str}{directory['name']}/")
            for child in directory.get('children', []):
                lines.extend(self._format_directory_structure(child, indent + 1))
        else:
            lines.append(f"{indent_str}{directory['name']}")
        return lines


# Example usage
root_directory = 'path/to/your/root_directory'

# Create an instance of DirectoryStructure
ds = DirectoryStructure(root_directory)

# Get the directory structure as a dictionary
directory_structure = ds.get_directory_structure()
print(directory_structure)

# Format the directory structure for display
formatted_structure = ds.format_directory_structure()
print("\n".join(formatted_structure))
