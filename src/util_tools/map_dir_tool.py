from pathlib import Path
from typing import Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from loguru import logger

from src.util_tools.map_dir import DirectoryStructure


class DirectoryStructureTool(BaseTool):
    name = "map_directory_structure"
    description = "Maps the directory structure of a given root directory."
    _working_directory: Path

    def __init__(self, _working_directory: Path):
        super().__init__()
        object.__setattr__(self, '_working_directory', _working_directory)

    def _run(self, args=(), kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            ds = DirectoryStructure(self._working_directory)
            formatted_structure = ds.get_formatted_directory_structure()
            return "\n".join(formatted_structure)
        except Exception as e:
            logger.error(f"Failed to map directory structure. Error: {e}")
            return str(e)
