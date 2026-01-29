import logging
import asyncio
import re

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    ChannelInvalid,
    ChatAdminRequired,
    UsernameInvalid,
    UsernameNotModified
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from info import ADMINS, INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

lock = asyncio.Lock()

# ==============================
# CALLBACK HANDLER
# ==============================
@Client.on_callback_query(filters.regex(r"^index"))
async def index_files(bot, query):
    if query.data == "index_cancel":
        temp.CANCEL = True
        return await query.answer("Indexing cancelled")

    _, action, chat, last_msg_id, user_id = query.data.split("#")

    if action == "reject":
        await query.message.delete()
        await bot.send_message(
            int(user_id),
            f"Your indexing request for {chat} was rejected.",
            reply_to_message_id=int(last_msg_id)
        )
        return

    if lock.locked():
        return await query.answer("Wait for current process to finish.", show_alert=True)

    await query.answer("Processing…", show_alert=True)

    msg = query.message

    await msg.edit_text(
        "Starting indexing…",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
        )
    )

    try:
        chat = int(chat)
    except ValueError:
        pass

    await index_files_to_db(int(last_msg_id), chat, msg, bot)


# ==============================
# PM FILTER / LINK HANDLER
# ==============================
@Client.on_message(
    (filters.private & filters.incoming) &
    (filters.forwarded | filters.regex(r"(https://)?(t\.me|telegram\.me|telegram\.dog)/(c/)?(\d+|[\w_]+)/(\d+)"))
)
async def send_for_index(bot, message):
    chat_id = None
    last_msg_id = None

    if message.text:
        match = re.search(
            r"(https://)?(t\.me|telegram\.me|telegram\.dog)/(c/)?(\d+|[\w_]+)/(\d+)",
            message.text
        )
        if not match:
            return await message.reply("Invalid Telegram link.")

        chat_id = match.group(4)
        last_msg_id = int(match.group(5))

        if chat_id.isdigit():
            chat_id = int(f"-100{chat_id}")

    elif message.forward_from_chat:
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
        last_msg_id = message.forward_from_message_id

    else:
        return

    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply("Private channel. Make me admin first.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("Invalid link.")
    except Exception as e:
        logger.exception(e)
        return await message.reply(str(e))

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Accept", callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}")],
            [InlineKeyboardButton("Reject", callback_data=f"index#reject#{chat_id}#{last_msg_id}#{message.from_user.id}")]
        ]
    )

    await bot.send_message(
        LOG_CHANNEL,
        f"#IndexRequest\n\n"
        f"User: {message.from_user.mention}\n"
        f"Chat: <code>{chat_id}</code>\n"
        f"Last Msg ID: <code>{last_msg_id}</code>",
        reply_markup=buttons
    )

    await message.reply("Index request sent to moderators.")


# ==============================
# INDEX CORE
# ==============================
async def index_files_to_db(last_msg_id, chat, msg, bot):
    total = dup = deleted = errors = unsupported = 0
    temp.CANCEL = False
    current = temp.CURRENT

    async with lock:
        try:
            async for message in bot.get_chat_history(chat, offset_id=last_msg_id):
                if temp.CANCEL:
                    break

                current += 1

                if message.empty:
                    deleted += 1
                    continue

                if not message.media:
                    continue

                if message.media not in (
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT
                ):
                    unsupported += 1
                    continue

                media = getattr(message, message.media.value, None)
                if not media:
                    continue

                media.file_type = message.media.value
                media.caption = message.caption

                saved, status = await save_file(media)

                if saved:
                    total += 1
                elif status == 0:
                    dup += 1
                else:
                    errors += 1

                if current % 20 == 0:
                    await msg.edit_text(
                        f"Fetched: <code>{current}</code>\n"
                        f"Saved: <code>{total}</code>\n"
                        f"Duplicates: <code>{dup}</code>\n"
                        f"Deleted: <code>{deleted}</code>\n"
                        f"Unsupported: <code>{unsupported}</code>\n"
                        f"Errors: <code>{errors}</code>",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                        )
                    )

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            logger.exception(e)
            await msg.edit_text(f"Error: {e}")
        else:
            await msg.edit_text(
                f"✅ Indexing completed\n\n"
                f"Saved: <code>{total}</code>\n"
                f"Duplicates: <code>{dup}</code>\n"
                f"Deleted: <code>{deleted}</code>\n"
                f"Unsupported: <code>{unsupported}</code>\n"
                f"Errors: <code>{errors}</code>"
            )

