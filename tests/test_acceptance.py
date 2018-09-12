import asyncio
import random
import pytest
import uuid

from collections import defaultdict

import aiotask_context as context


@asyncio.coroutine
def dummy3():
    yield from asyncio.sleep(random.uniform(0, 2))
    return context.get("key")


@asyncio.coroutine
def dummy2(a, b):
    yield from asyncio.sleep(random.uniform(0, 2))
    res = context.get("key")
    yield from asyncio.sleep(random.uniform(0, 2))
    res1 = yield from dummy3()
    assert res == res1
    return a, b, res


@asyncio.coroutine
def dummy1(n_tasks):
    context.set("key", str(uuid.uuid4()))
    tasks = [
        asyncio.ensure_future(
            dummy2(id(context.asyncio_current_task()), n)) for n in range(n_tasks)]
    results = yield from asyncio.gather(*tasks)
    info = defaultdict(list)
    for taskid, n, key in results:
        info[key].append([taskid, n])

    return info


@pytest.mark.asyncio
@asyncio.coroutine
def test_ensure_future_concurrent():
    n_tasks = 10
    results = yield from asyncio.gather(*[dummy1(n_tasks=n_tasks) for x in range(1000)])
    for r in results:
        assert len(r) == 1
        for key, value in r.items():
            assert len(value) == n_tasks


@pytest.mark.asyncio
@asyncio.coroutine
def test_ensurefuture_context_propagation():
    context.set("key", "value")

    @asyncio.coroutine
    def change_context():
        assert context.get("key") == "value"
        context.set("key", "what")
        context.set("other", "data")

    yield from asyncio.ensure_future(change_context())

    assert context.get("key") == "what"
    assert context.get("other") == "data"


@pytest.mark.asyncio
@asyncio.coroutine
def test_waitfor_context_propagation():
    context.set("key", "value")

    @asyncio.coroutine
    def change_context():
        assert context.get("key") == "value"
        context.set("key", "what")
        context.set("other", "data")

    yield from asyncio.wait_for(change_context(), 1)
    assert context.get("key") == "what"
    assert context.get("other") == "data"


@pytest.mark.asyncio
@asyncio.coroutine
def test_gather_context_propagation():
    context.set("key", "value")

    @asyncio.coroutine
    def change_context():
        assert context.get("key") == "value"
        context.set("key", "what")
        context.set("other", "data")

    yield from asyncio.gather(change_context())
    assert context.get("key") == "what"
    assert context.get("other") == "data"
