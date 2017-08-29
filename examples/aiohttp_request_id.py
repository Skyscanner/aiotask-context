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
from aiohttp import web
import aiotask_context as context


def handle(request):
    name = request.match_info.get('name')
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
    loop = asyncio.get_event_loop()
    loop.set_task_factory(context.task_factory)
    app = web.Application(middlewares=[request_id_middleware])
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)
