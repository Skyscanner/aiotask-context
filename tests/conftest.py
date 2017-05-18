import pytest

from aiotask_context import task_factory


@pytest.fixture(autouse=True)
def context_loop(event_loop):
    event_loop.set_task_factory(task_factory)
