from unittest.mock import patch

import pytest

from organization.models import Repository as DbRepository
from organization.schemas import AgentModel
from src.devops_integrations.repos.ado_repos_models import Repository


@pytest.mark.django_db
def test_fetch_new_workitems(client, work_item_fetcher, agent, repo, mock_work_item):
    with patch('organization.services.fetch_new_tasks.app.send_task') as mock_send_task:
        work_item_fetcher.fetch_new_workitems(agent, repo)

        agent_md = AgentModel.model_validate(agent)
        repo_md = Repository.model_validate(repo)

        mock_send_task.assert_called_once_with(
            'organization.tasks.execute_task',
            args=[agent_md.model_dump(), repo_md.model_dump(), mock_work_item.model_dump()]
        )
