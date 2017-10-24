import asyncio
import logging
from copy import deepcopy


logger = logging.getLogger(__name__)

NO_LOOP_EXCEPTION_MSG = "No event loop found, key {} couldn't be set"


def task_factory(loop, coro, copy_context=False):
    task = asyncio.tasks.Task(coro, loop=loop)
    if task._source_traceback:
        del task._source_traceback[-1]

    try:
        context = asyncio.Task.current_task(loop=loop).context
        if copy_context:
            context = deepcopy(context)

        task.context = context
    except AttributeError:
        task.context = {}

    return task


def copying_task_factory(loop, coro):
    """
    Returns a task factory that copies a task's context into new tasks instead of
    sharing it.

    :param loop: The active event loop
    :param coro: A coroutine object
    :return: A context copying task factory
    """
    return task_factory(loop, coro, copy_context=True)


def get(key, default=None):
    """
    Retrieves the value stored in key from the Task.context dict. If key does not exist,
    or there is no event loop running, default will be returned

    :param key: identifier for accessing the context dict.
    :param default: None by default, returned in case key is not found.
    :return: Value stored inside the dict[key].
    """
    if not asyncio.Task.current_task():
        raise ValueError(NO_LOOP_EXCEPTION_MSG.format(key))

    return asyncio.Task.current_task().context.get(key, default)


def set(key, value):
    """
    Sets the given value inside Task.context[key]. If the key does not exist it creates it.

    :param key: identifier for accessing the context dict.
    :param value: value to store inside context[key].
    :raises
    """
    if not asyncio.Task.current_task():
        raise ValueError(NO_LOOP_EXCEPTION_MSG.format(key))

    asyncio.Task.current_task().context[key] = value
