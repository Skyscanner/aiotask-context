# Aiotask Context

[![Build Status](https://travis-ci.org/Skyscanner/aiotask-context.svg?branch=master)](https://travis-ci.org/Skyscanner/aiotask-context)

Store context information within the [asyncio.Task](https://docs.python.org/3/library/asyncio-task.html#task) object. For more information about why this package was developed, please read the blog post [From Flask to aiohttp](http://codevoyagers.com/2016/09/01/from-flask-to-aiohttp/).

Supports both asyncio and uvloop loops.

## Installation

```bash
pip install aiotask_context
```

## Usage

This package allows to store context information inside the [asyncio.Task](https://docs.python.org/3/library/asyncio-task.html#task) object. A typical use case for it is to pass information between coroutine calls without the need to do it explicitly using the called coroutine args.


What this package is **NOT** for:

 - Don't fall into the bad pattern of storing everything your services need inside, this should only be used for objects or data that is needed by all or almost all the parts of your code where propagating it through args doesn't scale.
 - The context is a `dict` object so you can store any object you want inside. This opens the door to using it to change variables inside in the middle of an execution so other coroutines behave differently or other dirty usages. This is really **discouraged**.


Now, a (simplified) example where you could apply this: In your application, to share the `request_id` between all the calls, you should do the following:

```python
import asyncio


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

As you can see, this code smells a bit and feels like repeating yourself a lot (think about this example as if you had current API running in a framework and you needed the `request_id` everywhere to log it properly). With `aiotask_context` you can do:

```python
import asyncio
import aiotask_context as context


async def my_coro_1():
    print(context.get("request_id", default="Unknown"))


async def my_coro_2():
    print(context.get("request_id", default="Unknown"))
    await my_coro_1()


async def my_coro_3():
    context.set(key="request_id", value="1234")
    await my_coro_2()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)
    loop.run_until_complete(my_coro_3())
```

It also keeps the context between the calls like `ensure_future`, `wait_for`, `gather`, etc. That's why you have to change the [task factory](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.AbstractEventLoop.set_task_factory):


```python
import asyncio
import aiotask_context as context


async def my_coro_0():
    print("0: " + context.get("status"))

async def my_coro_1():
    context.set("status", "DONE")


async def my_coro_2():
    context.set("status", "RUNNING")
    print("2: " + context.get("status"))
    await asyncio.gather(asyncio.ensure_future(my_coro_1()), my_coro_0())
    print("2: " + context.get("status"))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)  # This is the relevant line
    loop.run_until_complete(my_coro_2())
```

You may also want to only keep a copy of the context between calls.
For example, you have one task that spawns many others
and do not want to reflect changes in one task's context into the other tasks.
To do this you have two options:

- `copying_task_factory` - uses a brand new copy of the context `dict` for *each* task
- `chainmap_task_factory` - uses a `ChainMap` instead of a `dict` as context,
    which allows some of the values to be redefined while not creating a full copy of the context

The following example yields the same results with both:

```python
import asyncio
import aiotask_context as context


async def my_coro_0():
    context.set("status", "FAILED")
    print("0: " + context.get("status"))

async def my_coro_1():
    context.set("status", "PENDING")
    print("1: " + context.get("status"))
    await my_coro_1_child()


async def my_coro_1_child():
    print("1 (child): " + context.get("status"))

async def my_coro_spawner():
    context.set("status", "RUNNING")
    print("2: " + context.get("status"))
    await asyncio.gather(asyncio.ensure_future(my_coro_1()), my_coro_0())
    print("2: " + context.get("status"))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for factory in (context.copying_task_factory,
                    context.chainmap_task_factory):
        print('\nUsing', factory.__name__)
        loop.set_task_factory(factory)  # This is the relevant line
        loop.run_until_complete(my_coro_spawner())
```

## Comparison of task factories / context types

The difference between the task factories can be best illustrated by
how they behave when inherited values are redefined or updated in child tasks.

Consider:

```python
import asyncio
import aiotask_context as context

async def my_coro_parent(loop):
    context.set("simple", "from parent")
    context.set("complex", ["from", "parent"])
    print("parent before: simple={}, complex={}".format(
        context.get("simple"), context.get("complex")))
    await loop.create_task(my_coro_child())
    print("parent after: simple={}, complex={}".format(
        context.get("simple"), context.get("complex")))

async def my_coro_child():
    context.set("simple", "from child")  # redefine value completely
    context.get("complex")[1] = "child"  # update existing object
    print("child: simple={}, complex={}".format(
        context.get("simple"), context.get("complex")))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    for factory in (context.task_factory,
                    context.copying_task_factory,
                    context.chainmap_task_factory):
        print('\nUsing', factory.__name__)
        loop.set_task_factory(factory)
        loop.run_until_complete(my_coro_parent(loop))
```

In this case the results are different for all three:

```
Using task_factory
parent before: simple=from parent, complex=['from', 'parent']
child: simple=from child, complex=['from', 'child']
parent after: simple=from child, complex=['from', 'child']

Using copying_task_factory
parent before: simple=from parent, complex=['from', 'parent']
child: simple=from child, complex=['from', 'child']
parent after: simple=from parent, complex=['from', 'parent']

Using chainmap_task_factory
parent before: simple=from parent, complex=['from', 'parent']
child: simple=from child, complex=['from', 'child']
parent after: simple=from parent, complex=['from', 'child']
```

## Complete examples

If you've reached this point it means you are interested. Here are a couple of complete examples with
`aiohttp`:

- Setting the `X-Request-ID` header and sharing it over your code:

```python
"""
POC to demonstrate the usage of the aiotask_context package for easily sharing the request_id
in all your code. If you run this script, you can try to query with curl or the browser:

    $ curl http://127.0.0.1:8080/Manuel
    Hello, Manuel. Your request id is fdcde8e3-b2e0-4b9c-96ca-a7ce0c8749be.

    $ curl -H "X-Request-ID: myid" http://127.0.0.1:8080/Manuel
    Hello, Manuel. Your request id is myid.
"""

import uuid
import asyncio
import aiotask_context as context

from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, {}. Your request id is {}.\n".format(name, context.get("X-Request-ID"))
    return web.Response(text=text)


async def request_id_middleware(app, handler):
    async def middleware_handler(request):
        context.set("X-Request-ID", request.headers.get("X-Request-ID", str(uuid.uuid4())))
        response = await handler(request)
        response.headers["X-Request-ID"] = context.get("X-Request-ID")
        return response
    return middleware_handler

loop = asyncio.get_event_loop()
loop.set_task_factory(context.task_factory)
app = web.Application(middlewares=[request_id_middleware], loop=loop)
app.router.add_route('GET', '/{name}', handle)
web.run_app(app)
```

- Setting the request_id in all log calls:

```python
"""
POC to demonstrate the usage of the aiotask_context package for writing the request_id
from aiohttp into every log call. If you run this script, you can try to query with curl or the browser:

    $ curl http://127.0.0.1:8080/Manuel
    Hello, Manuel. Your request id is fdcde8e3-b2e0-4b9c-96ca-a7ce0c8749be.

    $ curl -H "X-Request-ID: myid" http://127.0.0.1:8080/Manuel
    Hello, Manuel. Your request id is myid.

In the terminal you should see something similar to:

  ======== Running on http://0.0.0.0:8080/ ========
  (Press CTRL+C to quit)
  2016-09-07 12:02:39,887 WARNING __main__:63 357ab21e-5f05-44eb-884b-0ce3ceebc1ce | First_call called
  2016-09-07 12:02:39,887 ERROR __main__:67 357ab21e-5f05-44eb-884b-0ce3ceebc1ce | Second_call called
  2016-09-07 12:02:39,887 INFO __main__:76 357ab21e-5f05-44eb-884b-0ce3ceebc1ce | Received new GET /Manuel call
  2016-09-07 12:02:39,890 INFO aiohttp.access:405 357ab21e-5f05-44eb-884b-0ce3ceebc1ce | 127.0.0.1 - - [07/Sep/2016:10:02:39 +0000] "GET /Manuel HTTP/1.1" 200 70 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
"""

import asyncio
import uuid
import logging.config
import aiotask_context as context

from aiohttp import web


class RequestIdFilter(logging.Filter):

    def filter(self, record):
        record.request_id = context.get("X-Request-ID")
        return True

LOG_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filters': ['requestid'],
        },
    },
    'filters': {
        'requestid': {
            '()': RequestIdFilter,
        },
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s:%(lineno)d %(request_id)s | %(message)s',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True
        },
    }
}

logging.config.dictConfig(LOG_SETTINGS)
logger = logging.getLogger(__name__)
logger.addFilter(RequestIdFilter())


async def first_call():
    logger.warning("First_call called")


async def second_call():
    logger.error("Second_call called")


async def handle(request):

    name = request.match_info.get('name')

    await asyncio.gather(first_call())
    await second_call()
    logger.info("Received new GET /{} call".format(name))

    text = "Hello, {}. Your request id is {}.\n".format(name, context.get("X-Request-ID"))

    return web.Response(text=text)


async def request_id_middleware(app, handler):
    async def middleware_handler(request):
        context.set("X-Request-ID", request.headers.get("X-Request-ID", str(uuid.uuid4())))
        response = await handler(request)
        response.headers["X-Request-ID"] = context.get("X-Request-ID")
        return response
    return middleware_handler


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)
    app = web.Application(middlewares=[request_id_middleware], loop=loop)
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)
```
