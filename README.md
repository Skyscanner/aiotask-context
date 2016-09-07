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

from aiotask_context import context


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

from aiotask_context import context


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

from aiotask_context import context


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

## Examples

You can visit the [examples](examples) folder to check the source code but here are a couple of examples:

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
from aiohttp import web

from aiotask_context import context

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, {}. Your request id is {}.\n".format(name, context.get("X-Request-ID"))
    return web.Response(body=text.encode('utf-8'))


async def request_id_middleware(app, handler):
    async def middleware_handler(request):
        context.set("X-Request-ID", request.headers.get("X-Request-ID", str(uuid.uuid4())))
        response = await handler(request)
        response.headers["X-Request-ID"] = context.get("X-Request-ID")
        return response
    return middleware_handler

app = web.Application(middlewares=[request_id_middleware])
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

import uuid
import logging.config

from aiohttp import web
from aiotask_context import context


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

    await first_call()
    await second_call()
    logger.info("Received new GET /{} call".format(name))

    text = "Hello, {}. Your request id is {}.\n".format(name, context.get("X-Request-ID"))

    return web.Response(body=text.encode('utf-8'))


async def request_id_middleware(app, handler):
    async def middleware_handler(request):
        context.set("X-Request-ID", request.headers.get("X-Request-ID", str(uuid.uuid4())))
        response = await handler(request)
        response.headers["X-Request-ID"] = context.get("X-Request-ID")
        return response
    return middleware_handler


if __name__ == "__main__":
    app = web.Application(middlewares=[request_id_middleware])
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)
```


## Future work

The library currently supports only the `await` calls. All the other calls that are returning a new `asyncio.Task` object instance like `asyncio.ensure_future`, `asyncio.call_later`, etc are not passing the context object from the parent to the child. In the future versions, the intention is to wrap or monkeypatch all this calls in order to pass the context object if available.
