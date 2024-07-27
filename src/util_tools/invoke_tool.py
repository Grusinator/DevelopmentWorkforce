import sys

from invoke import task, Collection, Context
from langchain.tools import BaseTool
from typing import Optional, Any

from langchain_core.callbacks import CallbackManagerForToolRun
from loguru import logger

import tasks
from src.utils import log_inputs


# Sample Invoke tasks
@task
def hello(ctx):
    """Prints Hello, world!"""
    print("Hello, world!")


@task
def add(ctx, a, b):
    """Adds two numbers and prints the result"""
    print(f"The sum of {a} and {b} is {a + b}")


logger.add(sys.stderr, level="DEBUG")


# Wrapper to convert Invoke tasks to LangChain tools
class InvokeTaskTool(BaseTool):
    def __init__(self, task_func):
        name = task_func.__name__
        description = task_func.__doc__ if task_func.__doc__ else "No description available"
        super().__init__(name=name, description=description)
        object.__setattr__(self, '_task_func', task_func)

    @log_inputs
    def _run(self, args: tuple = tuple(), kwargs: dict = None,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> Any:
        # The first argument for invoke tasks is always the context (ctx)
        ctx = Context()
        try:
            return self._task_func(ctx, *args, **kwargs or dict())
        except Exception as e:
            logger.exception(f"Error running task: {e}")
            raise e


class TaskCollector:
    def __init__(self, namespace):
        self.namespace = namespace

    def collect_tasks(self):
        tools = [InvokeTaskTool(task.body) for _, task in self.namespace.tasks.items()]
        return tools


# Example usage
if __name__ == "__main__":

    namespace = Collection.from_module(tasks)

    collector = TaskCollector(tasks.collection)
    collected_tasks = collector.collect_tasks()
    print(collected_tasks)

    for tool in collected_tasks:
        print(f"Tool name: {tool.name}, Description: {tool.description}")
