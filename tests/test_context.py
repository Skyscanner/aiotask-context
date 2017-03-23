import pytest
import asyncio

from unittest import mock

from aiotask_context import context


@asyncio.coroutine
def dummy():
    pass


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
