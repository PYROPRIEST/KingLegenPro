import re
import os
from os import environ
from pyrogram import enums, Client
from Script import script
import asyncio
import json
from collections import defaultdict
from typing import Dict, List, Union

# -------------------- BASIC UTILS --------------------

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if str(value).lower() in ["true", "yes", "1", "enable", "y", "on"]:
        return True
    elif str(value).lower() in ["false", "no", "0", "disable", "n", "off"]:
        return False
    return default

# -------------------- HARD CODED CONFIG --------------------

SESSION = "Media_search"

API_ID = 26974083
API_HASH = "e013696bd13ea9495b803a679852da59"
BOT_TOKEN = "6141743333:AAHrC11ZFQa-XJIy0K6zrn5j1sItD1PzPmk"

CACHE_TIME = 300
USE_CAPTION_FILTER = False

PICS = ["https://telegra.ph/file/10009136df7620d9d3e5a.jpg"]
NOR_IMG = "https://graph.org/file/5813021ba24f773df40a8.jpg"
SPELL_IMG = "https://telegra.ph/file/b58f576fed14cd645d2cf.jpg"

MELCOW_IMG = "https://telegra.ph/file/e54cae941b9b81f13eb71.jpg"
MELCOW_VID = ""

ADMINS = [6256516042, 1246881279]
CHANNELS = [-1001591139633]

AUTH_USERS = ADMINS
AUTH_CHANNEL = -1001677223924
AUTH_GROUPS = None

SUPPORT_CHAT_ID = None

TMP_DOWNLOAD_DIRECTORY = "./DOWNLOADS/"
COMMAND_HAND_LER = "/"

# -------------------- MONGODB --------------------

DATABASE_URI = "mongodb+srv://grtrobot:grtrobot@cluster0.llshxmk.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "Cluster0"
COLLECTION_NAME = "Telegram_files"

# -------------------- OTHER SETTINGS --------------------

DOWNLOAD_LOCATION = "./DOWNLOADS/AudioBoT/"

SHORTLINK_URL = ""
SHORTLINK_API = ""
IS_SHORTLINK = False

CHAT_ID = []
TEXT = "Hello {mention}\nWelcome To {title}\n\nYour request has been approved"
APPROVED = "on"

NO_RESULTS_MSG = True
DELETE_CHANNELS = [0]

PORT = 8080   # ✅ FIXED (Render requires int)

MAX_BTN = 7

S_GROUP = "https://t.me/pirate_cinemas_group"
MAIN_CHANNEL = "https://t.me/the_aecr"
FILE_FORWARD = "https://t.me/+YkGthFjwHBpmZDY1"

MSG_ALRT = "𝑪𝑯𝑬𝑪𝑲 & 𝑻𝑹𝒀 𝑨𝑳𝑳 𝑴𝒀 𝑭𝑬𝑨𝑻𝑼𝑹𝑬𝑺"

FILE_CHANNEL = -1001928955385
LOG_CHANNEL = -1001167461473

SUPPORT_CHAT = "jackeybots_support"

AUTO_DELETE = True
P_TTI_SHOW_OFF = False
IMDB = False
SINGLE_BUTTON = False

CUSTOM_FILE_CAPTION = script.CUSTOM_FILE_CAPTION
BATCH_FILE_CAPTION = CUSTOM_FILE_CAPTION
IMDB_TEMPLATE = script.IMDB_TEMPLATE_TXT
LONG_IMDB_DESCRIPTION = False
SPELL_CHECK_REPLY = True
MAX_LIST_ELM = None

INDEX_REQ_CHANNEL = LOG_CHANNEL
FILE_STORE_CHANNEL = []

MELCOW_NEW_USERS = True
PROTECT_CONTENT = False
PUBLIC_FILE_STORE = True

# -------------------- LOG STRING --------------------

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB enabled\n" if IMDB else "IMDB disabled\n")
LOG_STR += ("Single button enabled\n" if SINGLE_BUTTON else "Single button disabled\n")
LOG_STR += f"IMDB Template: {IMDB_TEMPLATE}\n"

# -------------------- CLIENT CLASS --------------------

class evamaria(Client):
    filterstore: Dict[str, Dict[str, str]] = defaultdict(dict)
    warndatastore: Dict[str, Dict[str, Union[str, int, List[str]]]] = defaultdict(dict)
    warnsettingsstore: Dict[str, str] = defaultdict(dict)

    def __init__(self):
        super().__init__(
            SESSION,
            plugins=dict(root="plugins"),
            workdir=TMP_DOWNLOAD_DIRECTORY,
            api_id=API_ID,          # ✅ FIXED (APP_ID bug)
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            parse_mode=enums.ParseMode.HTML,
            sleep_threshold=60
        )
