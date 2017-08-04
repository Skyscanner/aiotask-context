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
    def test_get_without_factory(self, event_loop):
        event_loop.set_task_factory(None)

        @asyncio.coroutine
        def coro():
            assert context.get("key") is None
            assert context.get("key", default='default') == "default"

        yield from asyncio.ensure_future(coro())

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_set(self):
        context.set("key", "value")
        context.set("key", "updated_value")
        assert context.get("key") == "updated_value"

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_set_without_factory(self, event_loop):
        event_loop.set_task_factory(None)

        @asyncio.coroutine
        def coro():
            context.set("key", "default")
            assert context.get("key") == "default"

        yield from asyncio.ensure_future(coro())

    def test_get_without_loop(self):
        with pytest.raises(ValueError):
            context.get("random")

    def test_set_without_loop(self):
        with pytest.raises(ValueError):
            context.set("random", "value")
