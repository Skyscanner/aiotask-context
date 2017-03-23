import pytest
import asyncio

from aiotask_context import context


@pytest.mark.asyncio
async def test_ensure_future_concurrent():
    pass


@pytest.mark.asyncio
async def test_ensurefuture_context_mutability():
    context.set("key", "value")

    async def change_context():
        assert context.get("key") == "value"
        context.set("key", "what")
        context.set("other", "data")

    await context.ensure_future(change_context())

    assert context.get("key") == "what"
    assert context.get("other") == "data"
