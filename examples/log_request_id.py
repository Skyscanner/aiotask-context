"""
POC to demonstrate the usage of the aiotask_context package for writing the request_id
from aiohttp into every log call. If you run this script, you can try to query with curl or the
browser:

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
  2016-09-07 12:02:39,890 INFO aiohttp.access:405 357ab21e-5f05-44eb-884b-0ce3ceebc1ce | 127.0.0.1 - -
    [07/Sep/2016:10:02:39 +0000] "GET /Manuel HTTP/1.1" 200 70 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
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
