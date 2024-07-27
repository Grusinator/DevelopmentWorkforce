import pytest
from invoke import task, Collection

import tasks
from src.util_tools.invoke_tool import InvokeTaskTool, TaskCollector


@task
def hello(ctx):
    """Prints Hello, world!"""
    print("Hello, world!")


@task
def add(ctx, a, b):
    """Adds two numbers and prints the result"""
    print(f"The sum of {a} and {b} is {a + b}")


@pytest.mark.parametrize("task_func, args, expected_output, expected_description", [
    (hello, (), "Hello, world!", "Prints Hello, world!"),
    (add, (1, 2), "The sum of 1 and 2 is 3", "Adds two numbers and prints the result"),
])
def test_invoke_tasks(task_func, args, expected_output, expected_description):
    tool = InvokeTaskTool(task_func)
    assert tool.description == expected_description
    result = tool._run(args, {})
    assert result is None  # Because the functions print their output, they return None


def test_build_tools():
    namespace = Collection()
    namespace.add_task(hello)
    namespace.add_task(add)

    collector = TaskCollector(namespace)
    tools = collector.collect_tasks()
    assert len(tools) == 2



def test_build_tools2():
    namespace = Collection.from_module(tasks)

    collector = TaskCollector(namespace)
    tools = collector.collect_tasks()
    assert len(tools) == 1
