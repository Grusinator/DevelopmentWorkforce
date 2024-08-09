from pathlib import Path

from organization.models import Repository
from src.crew.models import TaskResult, LocalDevelopmentResult
from src.devops_integrations.workitems.ado_workitem_models import WorkItemModel
from src.models import TaskExtraInfo


class MockDevSession:

    def __init__(self, repo_dir):
        self.repo_dir = Path(repo_dir)

    def local_development_on_workitem(self, work_item: WorkItemModel, repo: Repository,
                                      task_extra_info: TaskExtraInfo = None):
        dummy_file_path = self.repo_dir / "dummy_file.txt"
        with dummy_file_path.open("w") as dummy_file:
            fil_content = f"This is a dummy file created by the mocked AI runner:  \n{work_item.description} \n\n"
            dummy_file.write(fil_content)

        task_results = [TaskResult(task_id=str(_id), work_item_id=work_item.source_id, thread_id=comment_thread.id,
                                   output=f"Response to comment thread: {comment_thread.id}")
                        for _id, comment_thread in enumerate(task_extra_info.pr_comments)]
        task_results.append(TaskResult(task_id="100", work_item_id=work_item.source_id))
        return LocalDevelopmentResult(succeeded=True, task_results=task_results, token_usage=1)
