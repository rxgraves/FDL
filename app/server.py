import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.errors import PeerIdInvalid
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

from app.config import BOT_TOKEN, API_ID, API_HASH, WEB_BASE_URL, LOG_CHANNEL_ID, DATABASE_URL
from app.session_store import ensure_session_table, load_session_from_db, save_session_to_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("fdl")

app = FastAPI(title="FDL Bot Server")

# Database connection
DB = None
def init_store():
    global DB
    try:
        DB = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        with DB.cursor() as c:
            c.execute(
                '''CREATE TABLE IF NOT EXISTS files (
                       file_id INTEGER PRIMARY KEY,
                       code TEXT NOT NULL,
                       expire_time INTEGER NOT NULL,
                       mime TEXT NOT NULL
                   )'''
            )
            DB.commit()
        ensure_session_table(DB)
        logger.info("✅ Database connection established and tables checked.")
    except Exception as e:
        logger.exception("❌ Failed to connect to database")
        raise

init_store()

session_file = os.path.join(os.getcwd(), "fdl-bot.session")

# Load previous session (if any) from DB
load_session_from_db(DB, session_file)

bot = Client(
    "fdl-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir=os.getcwd()
)

# Basic command
@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! I'm FDL Bot. Send me a file or use /fdl to generate download links.")

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting Pyrogram bot client...")
    try:
        await bot.start()
        try:
            await bot.send_message(LOG_CHANNEL_ID, "Bot is now active ✅")
            logger.info(f"Successfully sent test message to channel {LOG_CHANNEL_ID}")
        except Exception as e:
            logger.error(f"Failed to send test message to channel {LOG_CHANNEL_ID}: {str(e)}")

        from app.handlers.fdl_handler import media_listener, fdl_command
        bot.add_handler(MessageHandler(media_listener, filters.document | filters.video | filters.audio | filters.photo | filters.voice))
        bot.add_handler(MessageHandler(fdl_command, filters.command("fdl")))
        bot.add_handler(MessageHandler(start_command, filters.command("start")))
        logger.info("✅ Bot started successfully and handlers registered.")
    except Exception as e:
        logger.exception("❌ Pyrogram bot failed to start")
        raise

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 Stopping Pyrogram bot client...")
    try:
        save_session_to_db(DB, session_file)
    except Exception:
        pass
    if DB:
        DB.close()
    await bot.stop()
    logger.info("✅ Bot stopped successfully.")

async def verify_code(file_id: int, code: str) -> bool:
    with DB.cursor() as c:
        c.execute("SELECT code, expire_time FROM files WHERE file_id = %s", (file_id,))
        row = c.fetchone()
        if not row:
            return False
        db_code, expire_time = row
        return db_code == code and expire_time >= int(datetime.now().timestamp())

@app.get("/stream/{file_id}")
async def serve_stream(file_id: int, code: str):
    if not await verify_code(file_id, code):
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    try:
        message = await bot.get_messages(LOG_CHANNEL_ID, file_id)
        with DB.cursor() as c:
            c.execute("SELECT mime FROM files WHERE file_id = %s", (file_id,))
            row = c.fetchone()
            mime_type = row[0] if row else "application/octet-stream"

        return StreamingResponse(
            bot.stream_media(message),
            media_type=mime_type
        )
    except PeerIdInvalid:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/dl/{file_id}")
async def serve_download(file_id: int, code: str):
    if not await verify_code(file_id, code):
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    try:
        message = await bot.get_messages(LOG_CHANNEL_ID, file_id)
        with DB.cursor() as c:
            c.execute("SELECT mime FROM files WHERE file_id = %s", (file_id,))
            row = c.fetchone()
            mime_type = row[0] if row else "application/octet-stream"

        # Download to local temp file
        file_path = await bot.download_media(message)
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            filename=message.document.file_name if message.document else f"file_{file_id}"
        )
    except PeerIdInvalid:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/")
async def root():
    return {"status": "running", "message": "FDL Bot is alive"}

@app.get("/_health")
async def health():
    try:
        with DB.cursor() as c:
            c.execute("SELECT COUNT(*) FROM files")
            return {"status": "ok", "items": c.fetchone()[0]}
    except Exception:
        return {"status": "ok"}
