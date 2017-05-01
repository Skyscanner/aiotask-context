import pytest
import asyncio

from unittest import mock

from aiotask_context import context


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
        assert context.get("key", "default") == "default"
        assert context.get("key") is None

    def test_set_without_loop(self):
        with pytest.raises(ValueError):
            context.set("random", "value")

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_contextensurefuture_calls_asyncioensurefuture(self):
        with mock.patch("asyncio.ensure_future") as ensure_future:
            dummy_call = dummy()
            context.ensure_future(dummy_call, loop=None)
            ensure_future.assert_called_with(dummy_call, loop=None)

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_ensurefuture_returns_task(self):
        assert isinstance(context.ensure_future(dummy()), asyncio.Task)

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_waitfor_calls_asynciowaitfor(self):
        with mock.patch("asyncio.wait_for") as wait_for:
            dummy_call = dummy()
            yield from context.wait_for(dummy_call, 3)
            wait_for.assert_called_with(mock.ANY, 3, loop=None)

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_waitfor_works(self):
        with pytest.raises(asyncio.TimeoutError):
            yield from context.wait_for(dummy(1), 0.001)

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_gather_calls_asynciogather(self):
        with mock.patch("asyncio.gather") as gather:
            dummy1 = dummy()
            dummy2 = dummy()
            yield from context.gather(dummy1, dummy2)
            assert len(gather.call_args_list[0][0]) == 2
