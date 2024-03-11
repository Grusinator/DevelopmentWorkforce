import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture
def create_working_dir():
    working_directory = Path.cwd() / "test_workspace" / str(datetime.now().strftime("%m-%d-%H-%M-%S"))
    os.makedirs(working_directory)
    yield working_directory
    shutil.rmtree(working_directory)
