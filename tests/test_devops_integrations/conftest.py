import os

import pytest

from src.devops_integrations.models import ProjectAuthenticationModel


@pytest.fixture
def auth() -> ProjectAuthenticationModel:
    return ProjectAuthenticationModel(
        ado_org_name=os.getenv("ADO_ORGANIZATION_NAME"),
        pat=os.getenv("ADO_PERSONAL_ACCESS_TOKEN"),
        project_name=os.getenv("ADO_PROJECT_NAME")
    )
