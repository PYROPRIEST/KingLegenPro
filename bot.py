# ===============================
# PYTHON 3.13 + MOTOR PATCH
# ===============================
import asyncio

try:
    from asyncio import coroutine
except ImportError:
    def coroutine(func):
        return func
    asyncio.coroutine = coroutine

# ===============================
# IMPORTS
# ===============================
import logging
import logging.config
from datetime import date, datetime
import pytz

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web

from info import (
    SESSION, API_ID, API_HASH, BOT_TOKEN,
    LOG_STR, LOG_CHANNEL, PORT
)
from database.ia_filterdb import Media
from database.users_chats_db import db
from plugins import web_server
from utils import temp
from Script import script

# ===============================
# LOGGING
# ===============================
logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

# ===============================
# BOT CLASS
# ===============================
class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=100,
            plugins={"root": "plugins"},
            sleep_threshold=5
        )

    async def start(self):
        await super().start()

        # Load banned users
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        # Mongo indexes
        await Media.ensure_indexes()

        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name

        logging.info(
            f"{me.first_name} started | Pyrogram v{__version__} | Layer {layer}"
        )

        # Restart log
        tz = pytz.timezone("Asia/Kolkata")
        today = date.today()
        now = datetime.now(tz).strftime("%H:%M:%S %p")
        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, now)
        )

        # ===============================
        # WEB SERVER (RENDER NEEDS THIS)
        # ===============================
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        logging.info(f"Web server started on PORT {PORT}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped")

# ===============================
# RUN
# ===============================
Bot().run()

