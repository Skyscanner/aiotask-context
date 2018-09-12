import pytest
import asyncio

import uvloop

import aiotask_context as context


@pytest.fixture()
def asyncio_loop():
    asyncio.set_event_loop_policy(None)
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
    # restore the virgin state
    asyncio.set_event_loop_policy(None)


@pytest.fixture()
def uvloop_loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
    # restore the virgin state
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@pytest.fixture(params=[
    'asyncio_loop',
    'uvloop_loop'
])
def event_loop(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(autouse=True)
def context_loop(event_loop):
    event_loop.set_task_factory(context.task_factory)
