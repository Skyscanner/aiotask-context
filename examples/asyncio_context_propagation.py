import asyncio
import uuid
import aiotask_context as context


async def my_coro(n):
    print(str(n) + ": " + context.get("request_id"))


async def my_coro_2():
    context.set("request_id", str(uuid.uuid4()))
    await asyncio.gather(
        asyncio.ensure_future(my_coro(0)),
        asyncio.wait_for(my_coro(1), 1),
        asyncio.shield(asyncio.wait_for(my_coro(2), 1)),
        my_coro(3))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # this ensure asyncio calls like ensure_future, wait_for, etc.
    # propagate the context to the new task that is created
    loop.set_task_factory(context.task_factory)
    loop.run_until_complete(my_coro_2())
