import json
import subprocess
from pathlib import Path


def run_pytest_in_workspace(workspace_dir: Path):
    pytest_result = subprocess.run(
        ['pytest', str(workspace_dir), '--json-report', '--json-report-file=pytest_report.json'],
        cwd=workspace_dir,
        capture_output=True,
        text=True
    )
    json_report_path = workspace_dir / 'pytest_report.json'
    assert json_report_path.exists(), f"Report file not found: {json_report_path}"
    with open(json_report_path, 'r') as report_file:
        report_data = json.load(report_file)
        assert report_data['summary']['total'] > 0
        assert pytest_result.returncode == 0, report_data
