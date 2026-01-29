import traceback
from asyncio import get_running_loop
from io import BytesIO

from deep_translator import GoogleTranslator
from gtts import gTTS

from pyrogram import Client, filters
from pyrogram.types import Message


def convert(text: str):
    audio = BytesIO()

    # Detect language safely
    lang = GoogleTranslator(source="auto", target="en").detect(text)

    # Generate TTS
    tts = gTTS(text=text, lang=lang)
    audio.name = f"{lang}.mp3"
    tts.write_to_fp(audio)

    audio.seek(0)
    return audio


@Client.on_message(filters.command("tts"))
async def text_to_speech(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply_text("Reply to some text.")

    m = await message.reply_text("Processing...")
    text = message.reply_to_message.text

    try:
        loop = get_running_loop()
        audio = await loop.run_in_executor(None, convert, text)

        await message.reply_audio(audio)
        await m.delete()
        audio.close()

    except Exception:
        await m.edit("TTS failed.")
        print(traceback.format_exc())
