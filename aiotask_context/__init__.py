import asyncio


def task_factory(loop, coro):

    loop._check_closed()
    task = asyncio.tasks.Task(coro, loop=loop)
    if task._source_traceback:
        del task._source_traceback[-1]

    try:
        task.context = asyncio.Task.current_task().context
    except AttributeError:
        task.context = {}

    return task
