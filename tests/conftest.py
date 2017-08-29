import pytest
import asyncio

import uvloop

import aiotask_context as context


@pytest.fixture()
def asyncio_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def uvloop_loop():
    loop = uvloop.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(params=[
    'asyncio_loop',
    'uvloop_loop'
])
def event_loop(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture(autouse=True)
def context_loop(event_loop):
    event_loop.set_task_factory(context.task_factory)
