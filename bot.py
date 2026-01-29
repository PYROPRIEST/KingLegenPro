# ===============================
# PATCH FOR MOTOR + PYTHON 3.13
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
import os
import logging
import logging.config
from datetime import date, datetime
import pytz
from aiohttp import web
from typing import Union, Optional, AsyncGenerator

from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT
from plugins import web_server
from Script import script
from utils import temp

# ------------------------------
# LOGGING
# ------------------------------
logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

# ------------------------------
# ENSURE PORT FOR RENDER
# ------------------------------
PORT = int(os.environ.get("PORT", PORT))

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
            workers=150,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        today = date.today()
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))

        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator[types.Message, None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

# ===============================
# RUN BOT
# ===============================
app = Bot()
app.run()

