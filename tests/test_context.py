import pytest
import asyncio
import aiotask_context as context


@asyncio.coroutine
def dummy(t=0):
    yield from asyncio.sleep(t)


class TestContext:

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

        @asyncio.coroutine
        def coro(loop):
            yield from asyncio.sleep(0, loop=loop)
            return True

        assert event_loop.run_until_complete(coro(event_loop)) is True
        asyncio.set_event_loop(None)
        assert event_loop.run_until_complete(coro(event_loop)) is True


    def test_closed_loop(self, event_loop):
        event_loop.close()
        with pytest.raises(RuntimeError):
            context.task_factory(event_loop, dummy())
