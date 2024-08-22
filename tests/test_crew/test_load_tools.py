import pytest
from pathlib import Path
from src.crew.tools import ToolsBuilder

def test_load_default_toolset():
    # Arrange
    working_directory = Path("/tmp/test_workspace")
    tools_builder = ToolsBuilder(working_directory)

    # Act
    default_tools = tools_builder.get_default_toolset()

    # Assert
    assert len(default_tools) > 0, "Default toolset should not be empty"
    
    # Check for specific tools
    expected_tools = {"read_file", "write_file", "file_delete", "move_file", "map_directory_structure", "run_pytest"}
    actual_tools = set(tool.name for tool in default_tools)
    
    assert expected_tools.issubset(actual_tools), f"The following tools are missing from the default toolset: {expected_tools - actual_tools}"
