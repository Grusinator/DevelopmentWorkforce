import json
import logging
from pathlib import Path
from typing import Optional

import pytest
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from src.utils import log_inputs

from loguru import logger


class PytestTool(BaseTool):
    name = "run pytests"
    description = "This tool runs pytest in the working directory and generates a JSON report. " \
                  "this tool requires no input, just leave the input field empty: 'Action Input: ' "
    _working_directory: Path

    def __init__(self, _working_directory: Path):
        super().__init__()
        object.__setattr__(self, '_working_directory', _working_directory)

    @log_inputs
    def _run(self, args=(), kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        try:
            json_report_path = self._working_directory / 'pytest_report.json'
            pytest.main([str(self._working_directory), '--json-report', f'--json-report-file={json_report_path}'])
            with open(json_report_path, 'r') as report_file:
                report_json = json.load(report_file)
                return report_json
        except Exception as e:
            logger.error(f"Failed run pytest. Error: {e}")
            return {"error": str(e)}
