from aiohttp import web
import os


class WebServer():
    def __init__(self, port=None):
        self.port = port


routes = web.RouteTableDef()


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        # this is needed to handle ``return web.HTTPNotFound()`` case
        if response.status == 404:
            return web.FileResponse(f"./web/dist/index.html")
        return response
    except web.HTTPException as ex:
        # this is needed to handle ``raise web.HTTPNotFound()`` case
        if ex.status == 404:
            return web.FileResponse(f"./web/dist/index.html")
        raise
    # this is needed to handle non-HTTPException
    except Exception:
        return web.Response(text='Oops, something went wrong', status=500)


@routes.get('/')
async def hello(request):
    return web.FileResponse(f"./web/dist/index.html")


@routes.get('/json')
async def js(request):
    data = {
        'some': 'data'
    }
    return web.json_response(data)


async def websocket_handler(request):
    print('Websocket connection starting')
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    print('Websocket connection ready')

    async for msg in ws:
        print(msg)
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(msg.data)
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')

    print('Websocket connection closed')
    return ws


app = web.Application(middlewares=[error_middleware])
app.add_routes([web.get('/ws', websocket_handler)])

routes.static('/', "./web/dist/")

app.add_routes(routes)

web.run_app(app, port=8088)
