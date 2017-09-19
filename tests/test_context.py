import pytest
import asyncio
import traceback

import aiotask_context as context


@asyncio.coroutine
def dummy(t=0):
    yield from asyncio.sleep(t)
    return True


class TestSetGet:

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_get_ok(self):
        context.set("key", "value")
        assert context.get("key") == "value"

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_get_missing_key(self):
        context.set("random", "value")
        assert context.get("key", "default") == "default"
        assert context.get("key") is None

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_get_missing_context(self):
        assert context.get("key", "default") == "default"
        assert context.get("key") is None

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_set(self):
        context.set("key", "value")
        context.set("key", "updated_value")
        assert context.get("key") == "updated_value"

    def test_get_without_loop(self):
        with pytest.raises(ValueError):
            context.get("key")

    def test_set_without_loop(self):
        with pytest.raises(ValueError):
            context.set("random", "value")

    def test_loop_bug_aiohttp(self, event_loop):
        assert event_loop.run_until_complete(dummy()) is True
        asyncio.set_event_loop(None)
        assert event_loop.run_until_complete(dummy()) is True

    def test_closed_loop(self, event_loop):
        event_loop.close()
        with pytest.raises(RuntimeError):
            context.task_factory(event_loop, dummy())


class TestTaskFactory:

    @pytest.mark.asyncio
    async def test_propagates_context(self, event_loop):
        context.set('key', 'value')
        task = context.task_factory(event_loop, dummy())
        task.cancel()

        assert task.context == {'key': 'value'}

    @pytest.mark.asyncio
    async def test_sets_empty_context(self, event_loop):
        task = context.task_factory(event_loop, dummy())
        task.cancel()

        assert task.context == {}

    @pytest.mark.asyncio
    async def test_sets_traceback(self, event_loop):
        event_loop.set_debug(True)
        task = context.task_factory(event_loop, dummy())
        task.cancel()

        assert isinstance(task._source_traceback, traceback.StackSummary)

    @pytest.mark.asyncio
    async def test_propagates_copy_of_context(self, event_loop):
        @asyncio.coroutine
        def adds_to_context():
            context.set('foo', 'bar')
            return True

        context.set('key', 'value')
        task = context.copying_task_factory(event_loop, adds_to_context())
        await task

        assert task.context == {'key': 'value', 'foo': 'bar'}
        assert context.get('foo') is None
