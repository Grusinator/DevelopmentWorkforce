import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from src.utils import log_inputs

logger = logging.getLogger(__name__)


class PytestTool(BaseTool):
    name = "run_pytest"
    description = "This tool runs pytest in the working directory and generates a JSON report. " \
                  "this tool requires no input, just leave the input field empty: 'Action Input: ' "
    _working_directory: Path

    def __init__(self, _working_directory: Path):
        super().__init__()
        object.__setattr__(self, '_working_directory',
                           _working_directory)  # has to be like this to not mess with langchain

    @log_inputs
    def _run(self, args=(), kwargs=None, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        try:
            return self.run_pytest()
        except Exception as e:
            logger.error(f"Failed to run pytest. Error: {e}")
            return {"error": str(e)}

    def run_pytest(self):

        env = os.environ.copy()
        env['PYTHONPATH'] = str(self._working_directory) + os.pathsep + env.get('PYTHONPATH', '')

        json_report_path = self._working_directory / 'pytest_report.json'
        command = f'pytest {self._working_directory} --json-report --json-report-file={json_report_path}'
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self._working_directory),
            shell=True,
            env=env
        )
        report_json = self.load_json_report(json_report_path)

        return {
            'output': result.stdout,
            'error_output': result.stderr,
            'report': report_json
        }

    def load_json_report(self, json_report_path):
        if json_report_path.exists():
            with open(json_report_path, 'r') as report_file:
                report_json = json.load(report_file)
        else:
            report_json = {}
        return report_json
