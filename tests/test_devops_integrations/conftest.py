import os

import pytest

from src.devops_integrations.models import ProjectAuthentication


@pytest.fixture
def auth() -> ProjectAuthentication:
    return ProjectAuthentication(
        ado_org_name=os.getenv("ADO_ORGANIZATION_NAME"),
        pat=os.getenv("ADO_PERSONAL_ACCESS_TOKEN"),
        project_name=os.getenv("ADO_PROJECT_NAME")
    )
