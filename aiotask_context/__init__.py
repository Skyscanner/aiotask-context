import asyncio
import logging
import sys
from collections import ChainMap
from copy import deepcopy
from functools import partial

PY37 = sys.version_info >= (3, 7)

if PY37:
    def asyncio_current_task(loop=None):
        """Return the current task or None."""
        try:
            return asyncio.current_task(loop)
        except RuntimeError:
            # simulate old behaviour
            return None
else:
    asyncio_current_task = asyncio.Task.current_task


logger = logging.getLogger(__name__)

NO_LOOP_EXCEPTION_MSG = "No event loop found, key {} couldn't be set"


def dict_context_factory(parent_context=None, copy_context=False):
    """A traditional ``dict`` context to keep things simple"""
    if parent_context is None:
        # initial context
        return {}
    else:
        # inherit context
        new_context = parent_context
        if copy_context:
            new_context = deepcopy(new_context)
        return new_context


def chainmap_context_factory(parent_context=None):
    """
    A ``ChainMap`` context, to avoid copying any data
    and yet preserve strict one-way inheritance
    (just like with dict copying)
    """
    if parent_context is None:
        # initial context
        return ChainMap()
    else:
        # inherit context
        if not isinstance(parent_context, ChainMap):
            # if a dict context was previously used, then convert
            # (without modifying the original dict)
            parent_context = ChainMap(parent_context)
        return parent_context.new_child()


def task_factory(loop, coro, copy_context=False, context_factory=None):
    """
    By default returns a task factory that uses a simple dict as the task context,
    but allows context creation and inheritance to be customized via ``context_factory``.
    """
    context_factory = context_factory or partial(
        dict_context_factory, copy_context=copy_context)

    task = asyncio.tasks.Task(coro, loop=loop)
    if task._source_traceback:
        del task._source_traceback[-1]

    try:
        context = asyncio_current_task(loop=loop).context
    except AttributeError:
        context = None

    task.context = context_factory(context)

    return task


def copying_task_factory(loop, coro):
    """
    Returns a task factory that copies a task's context into new tasks instead of
    sharing it.

    :param loop: The active event loop
    :param coro: A coroutine object
    :return: A context-copying task factory
    """
    return task_factory(loop, coro, copy_context=True)


def chainmap_task_factory(loop, coro):
    """
    Returns a task factory that uses ``ChainMap`` as the context.

    :param loop: The active event loop
    :param coro: A coroutine object
    :return: A ``ChainMap`` task factory
    """
    return task_factory(loop, coro, context_factory=chainmap_context_factory)


def get(key, default=None):
    """
    Retrieves the value stored in key from the Task.context dict. If key does not exist,
    or there is no event loop running, default will be returned

    :param key: identifier for accessing the context dict.
    :param default: None by default, returned in case key is not found.
    :return: Value stored inside the dict[key].
    """
    current_task = asyncio_current_task()
    if not current_task:
        raise ValueError(NO_LOOP_EXCEPTION_MSG.format(key))

    return current_task.context.get(key, default)


def set(key, value):
    """
    Sets the given value inside Task.context[key]. If the key does not exist it creates it.

    :param key: identifier for accessing the context dict.
    :param value: value to store inside context[key].
    :raises
    """
    current_task = asyncio_current_task()
    if not current_task:
        raise ValueError(NO_LOOP_EXCEPTION_MSG.format(key))

    current_task.context[key] = value


def clear():
    """
    Clear the Task.context.

    :raises ValueError: if no current task.
    """
    current_task = asyncio_current_task()
    if not current_task:
        raise ValueError("No event loop found")

    current_task.context.clear()
