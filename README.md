# asyncio-locals

[![Build Status](https://travis-ci.org/Skyscanner/aiotask-context.svg?branch=master)](https://travis-ci.org/Skyscanner/aiotask-context)

Store context information within the [asyncio.Task](https://docs.python.org/3/library/asyncio-task.html#task) object. For more information about why this package was developed, please read the blog post [From Flask to aiohttp](http://codevoyagers.com/2016/08/24/from-flask-to-aiohttp/).

## Installation

The package is not yet published to pypi. You can install it by doing:

```bash
pip install -e git+https://github.com/Skyscanner/aiotask-context#egg=aiotask-context
```

## Usage

This package allows to store context information inside the [asyncio.Task](https://docs.python.org/3/library/asyncio-task.html#task) object. A typical use case for it is to pass information between coroutine calls without the need to do it explicitly using the called coroutine args.

For example, in your application, to share the `request_id` between all the calls, you should do the following:

```python
import asyncio

from asyncio_context import context


async def my_coro_1(request_id):
  print(request_id)


async def my_coro_2(request_id):
  await my_coro_1(request_id)


async def my_coro_3():
  request_id = "1234"
  await my_coro_2(request_id)


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(my_coro_3())
```

As you can see, this code smells a bit and feels like repeating yourself a lot. With this library, you can just do the following:

```python
import asyncio

from asyncio_context import context


async def my_coro_1():
  print(context.get("request_id", default="Unknown"))


async def my_coro_2():
  await my_coro_1()


async def my_coro_3():
  context.set(key="request_id", value="1234")
  await my_coro_2()


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(my_coro_3())
```

If you execute this code, you will a "1234" printed in your display. You can even change the value in the middle of the execution to decide actions in the middle of the flow:


```python
import asyncio

from asyncio_context import context


async def my_coro_1():
  asyncio.sleep(5)
  context.set("status", "DONE")


async def my_coro_2():
  context.set("status", "RUNNING")
  print(context.get("status"))
  await my_coro_1()
  print(context.get("status"))


if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(my_coro_2())
```


## Future work

The library currently supports only the `await` calls. All the other calls that are returning a new `asyncio.Task` object instance like `asyncio.ensure_future`, `asyncio.call_later`, etc are not passing the context object from the parent to the child. In the future versions, the intention is to wrap or monkeypatch all this calls in order to pass the context object if available.
