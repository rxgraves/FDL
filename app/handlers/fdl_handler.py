import logging
import secrets
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import WEB_BASE_URL, LOG_CHANNEL_ID
from app.server import DB, bot

logger = logging.getLogger("fdl_handler")

async def media_listener(client, message):
    code = secrets.token_urlsafe(6)[:6]
    mime_type = "application/octet-stream"
    is_audio = False
    if message.document:
        mime_type = message.document.mime_type or "application/octet-stream"
    elif message.video:
        mime_type = "video/mp4"
    elif message.audio:
        mime_type = message.audio.mime_type or "audio/mpeg"
        is_audio = True
    elif message.photo:
        mime_type = "image/jpeg"
    elif message.voice:
        mime_type = "audio/ogg"
        is_audio = True

    try:
        sent = await message.forward(LOG_CHANNEL_ID)
        file_id = sent.id
        expire_time = int((datetime.now() + timedelta(days=1)).timestamp())

        with DB.cursor() as c:
            c.execute(
                '''INSERT INTO files (file_id, code, expire_time, mime)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (file_id) DO UPDATE SET
                       code = EXCLUDED.code,
                       expire_time = EXCLUDED.expire_time,
                       mime = EXCLUDED.mime''',
                (file_id, code, expire_time, mime_type)
            )
            DB.commit()

        stream_url = WEB_BASE_URL.rstrip("/") + f"/stream/{file_id}?code={code}"
        download_url = WEB_BASE_URL.rstrip("/") + f"/dl/{file_id}?code={code}"

        buttons = [
            InlineKeyboardButton("▶️ Stream", url=stream_url),
            InlineKeyboardButton("⬇️ Download", url=download_url)
        ]
        if is_audio:
            player_url = WEB_BASE_URL.rstrip("/") + f"/player/{file_id}?code={code}"
            buttons.insert(1, InlineKeyboardButton("🎵 Play", url=player_url))

        keyboard = InlineKeyboardMarkup([buttons])

        text = f"Links for the media:\n\n• Stream: {stream_url}\n"
        if is_audio:
            text += f"• Play: {player_url}\n"
        text += f"• Download: {download_url}"
        await message.reply_text(text, reply_markup=keyboard, quote=True)
        logger.info(f"Generated links for file_id: {file_id}")
    except Exception as e:
        logger.exception("Error handling media message")
        await message.reply_text("Sorry, failed to process the file. Try again later.")

async def fdl_command(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a media message with /fdl to create links.", quote=True)
        return
    replied = message.reply_to_message
    if not (replied.document or replied.video or replied.audio or replied.photo or replied.voice):
        await message.reply_text("Reply to a media message with /fdl to create links.", quote=True)
        return

    code = secrets.token_urlsafe(6)[:6]
    mime_type = "application/octet-stream"
    is_audio = False
    if replied.document:
        mime_type = replied.document.mime_type or "application/octet-stream"
    elif replied.video:
        mime_type = "video/mp4"
    elif replied.audio:
        mime_type = replied.audio.mime_type or "audio/mpeg"
        is_audio = True
    elif replied.photo:
        mime_type = "image/jpeg"
    elif replied.voice:
        mime_type = "audio/ogg"
        is_audio = True

    try:
        sent = await replied.forward(LOG_CHANNEL_ID)
        file_id = sent.id
        expire_time = int((datetime.now() + timedelta(days=1)).timestamp())

        with DB.cursor() as c:
            c.execute(
                '''INSERT INTO files (file_id, code, expire_time, mime)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (file_id) DO UPDATE SET
                       code = EXCLUDED.code,
                       expire_time = EXCLUDED.expire_time,
                       mime = EXCLUDED.mime''',
                (file_id, code, expire_time, mime_type)
            )
            DB.commit()

        stream_url = WEB_BASE_URL.rstrip("/") + f"/stream/{file_id}?code={code}"
        download_url = WEB_BASE_URL.rstrip("/") + f"/dl/{file_id}?code={code}"

        buttons = [
            InlineKeyboardButton("▶️ Stream", url=stream_url),
            InlineKeyboardButton("⬇️ Download", url=download_url)
        ]
        if is_audio:
            player_url = WEB_BASE_URL.rstrip("/") + f"/player/{file_id}?code={code}"
            buttons.insert(1, InlineKeyboardButton("🎵 Play", url=player_url))

        keyboard = InlineKeyboardMarkup([buttons])

        text = f"Links for the media:\n\n• Stream: {stream_url}\n"
        if is_audio:
            text += f"• Play: {player_url}\n"
        text += f"• Download: {download_url}"
        await message.reply_text(text, reply_markup=keyboard, quote=True)
        logger.info(f"Generated links for /fdl command, file_id: {file_id}")
    except Exception as e:
        logger.exception("Error handling /fdl command")
        await message.reply_text("Sorry, failed to generate links. Try again later.", quote=True)
