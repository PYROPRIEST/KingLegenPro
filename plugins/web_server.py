from aiohttp import web

async def web_server():
    app = web.Application()

    async def root(request):
        return web.Response(text="🔥 Bot is alive and running")

    app.router.add_get("/", root)
    return app
