from deep_translator import GoogleTranslator
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.helpers.list import list

@Client.on_message(filters.command(["tr"]))
async def left(client, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        ms = await message.reply_text("Reply to a text message to translate 🌍")
        return

    try:
        # get language code
        lg_cd = message.text.replace("/tr", "").strip().lower()
        if not lg_cd:
            lg_cd = "en"

        tr_text = message.reply_to_message.text

        translator = GoogleTranslator(source="auto", target=lg_cd)
        translated_text = translator.translate(tr_text)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="𝘔𝘰𝘳𝘦 𝘓𝘢𝘯𝘨 𝘊𝘰𝘥𝘦𝘴",
                        url="https://cloud.google.com/translate/docs/languages",
                    )
                ],
                [
                    InlineKeyboardButton("𝘊𝘭𝘰𝘴𝘦", callback_data="close_data")
                ],
            ]
        )

        await message.reply_text(
            f"**Translated Text:**\n\n```{translated_text}```",
            reply_markup=keyboard,
            quote=True,
        )

    except Exception as e:
        await message.reply_text("❌ Translation failed")
        print(e)

