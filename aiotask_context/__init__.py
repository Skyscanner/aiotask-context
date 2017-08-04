import asyncio
import logging


logger = logging.getLogger(__name__)


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


def get(key, default=None):
    """
    Retrieves the value stored in key from the Task.context dict. If key does not exist,
    default will be returned

    :param key: identifier for accessing the context dict.
    :param default: None by default, returned in case key is not found.
    :return: Value stored inside the dict[key].
    :raises ValueError: if loop cant be found
    """
    if not asyncio.Task.current_task():
        raise ValueError('No event loop found')

    try:
        return asyncio.Task.current_task().context.get(key, default)
    except (AttributeError, KeyError):
        return default


def set(key, value):
    """
    Sets the given value inside Task.context[key]. If the key does not exist it creates it.

    :param key: identifier for accessing the context dict.
    :param value: value to store inside context[key].
    :raises ValueError: if loop cant be found
    """
    if not asyncio.Task.current_task():
        raise ValueError('No event loop found')

    try:
        asyncio.Task.current_task().context[key] = value
    except AttributeError:
        logger.warning("context dict not exists, creating it")
        asyncio.Task.current_task().context = {key: value}
