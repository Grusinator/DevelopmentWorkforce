import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def create_working_dir():
    guid = str(uuid.uuid4())[0:8]
    time = datetime.now().strftime("%m-%d-%H-%M-%S")
    working_directory = Path.cwd() / "test_workspace" / f"{time}_{guid}"
    os.makedirs(working_directory)
    yield working_directory
