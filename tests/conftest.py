import pytest

import aiotask_context as context


@pytest.fixture(autouse=True)
def context_loop(event_loop):
    event_loop.set_task_factory(context.task_factory)
