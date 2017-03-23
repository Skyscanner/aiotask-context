import asyncio
import pytest
import uuid

from collections import defaultdict

from aiotask_context import context


@asyncio.coroutine
def dummy1(a, b):
    return a, b, context.get("key")


@asyncio.coroutine
def dummy2(n_tasks):
    context.set("key", str(uuid.uuid4()))
    tasks = [
        context.ensure_future(dummy1(id(asyncio.Task.current_task()), n)) for n in range(n_tasks)]
    results = yield from asyncio.gather(*tasks)
    info = defaultdict(list)
    for taskid, n, key in results:
        info[key].append([taskid, n])

    return info


@pytest.mark.asyncio
@asyncio.coroutine
def test_ensure_future_concurrent():
    n_tasks = 10
    results = yield from asyncio.gather(*[dummy2(n_tasks=n_tasks) for x in range(1000)])
    for r in results:
        assert len(r) == 1
        for key, value in r.items():
            assert len(value) == n_tasks


@pytest.mark.asyncio
@asyncio.coroutine
def test_ensurefuture_context_mutability():
    context.set("key", "value")

    @asyncio.coroutine
    def change_context():
        assert context.get("key") == "value"
        context.set("key", "what")
        context.set("other", "data")

    yield from context.ensure_future(change_context())

    assert context.get("key") == "what"
    assert context.get("other") == "data"
