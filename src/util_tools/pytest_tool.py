import pytest
import json
import logging
from pathlib import Path
from typing import Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool

from src.utils import log_inputs

logger = logging.getLogger(__name__)

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
            return self.run_pytest()
        except Exception as e:
            logger.error(f"Failed to run pytest. Error: {e}")
            return {"error": str(e)}

    def run_pytest(self):
        json_report_path = self._working_directory / 'pytest_report.json'

        # Use a list to collect the output for logging
        output_lines = []

        # Custom plugin to capture and store output
        class CaptureOutputPlugin:
            def pytest_runtest_logreport(self, report):
                if report.outcome == "passed":
                    output_lines.append(f"PASSED: {report.nodeid}")
                elif report.outcome == "failed":
                    output_lines.append(f"FAILED: {report.nodeid}")
                elif report.outcome == "skipped":
                    output_lines.append(f"SKIPPED: {report.nodeid}")

            def pytest_terminal_summary(self, terminalreporter, exitstatus):
                output_lines.append("=== Test Summary ===")
                output_lines.extend(terminalreporter.stats)

        # Run pytest with the custom plugin
        pytest.main(
            [str(self._working_directory), '--json-report', f'--json-report-file={json_report_path}'],
            plugins=[CaptureOutputPlugin()]
        )

        # Log the captured output
        for line in output_lines:
            logger.debug(line)

        # Load and return the JSON report
        with open(json_report_path, 'r') as report_file:
            report_json = json.load(report_file)
            return report_json

