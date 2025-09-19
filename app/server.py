import os
import logging
import psycopg2
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse
from pyrogram import Client
from pyrogram.errors import PeerIdInvalid
from app import fdl_handler

# =========================
# Config
# =========================
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
LOG_CHANNEL_ID = int(os.environ["LOG_CHANNEL_ID"])
DATABASE_URL = os.environ["DATABASE_URL"]

# =========================
# Logger setup
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("fdl")

# =========================
# DB Connection
# =========================
DB = psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    with DB.cursor() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id BIGINT PRIMARY KEY,
                mime TEXT
            )
        """)
        DB.commit()
    logger.info("✅ Files table ensured.")

init_db()

# =========================
# Bot
# =========================
bot = Client(
    "fdl-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# =========================
# FastAPI App
# =========================
app = FastAPI()

# include handlers
app.include_router(fdl_handler.router)

# =========================
# Helper Functions
# =========================
async def generate_code(file_id: int) -> str:
    return "ABC123"  # TODO: implement proper code generation

async def verify_code(file_id: int, code: str) -> bool:
    return True  # TODO: implement code verification

# =========================
# Routes
# =========================

@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting bot...")
    await bot.start()

@app.on_event("shutdown")
async def shutdown():
    await bot.stop()

@app.get("/stream/{file_id}")
async def serve_stream(file_id: int, code: str):
    if not await verify_code(file_id, code):
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    try:
        message = await bot.get_messages(LOG_CHANNEL_ID, file_id)
        return StreamingResponse(
            message.download(stream=True),
            media_type="video/mp4"
        )
    except PeerIdInvalid:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/dl/{file_id}")
async def serve_download(file_id: int, code: str):
    if not await verify_code(file_id, code):
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    try:
        message = await bot.get_messages(LOG_CHANNEL_ID, file_id)
        file_path = await message.download()
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except PeerIdInvalid:
        raise HTTPException(status_code=404, detail="File not found")

# =========================
# 🎬 Video Player Route
# =========================
@app.get("/player/{file_id}")
async def serve_player(file_id: int, code: str):
    if not await verify_code(file_id, code):
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    try:
        # file info from DB
        with DB.cursor() as c:
            c.execute("SELECT mime FROM files WHERE file_id = %s", (file_id,))
            row = c.fetchone()
            mime_type = row[0] if row else "video/mp4"

        stream_url = f"/stream/{file_id}?code={code}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>FDL Video Player</title>
            <style>
                body {{ background:#000; margin:0; display:flex; justify-content:center; align-items:center; height:100vh; }}
                video {{ max-width:100%; max-height:100%; }}
                .controls {{ position:absolute; bottom:30px; left:50%; transform:translateX(-50%); }}
                button {{
                    background: rgba(0,0,0,0.6);
                    border: none;
                    color: white;
                    font-size: 16px;
                    padding: 10px 15px;
                    margin: 0 5px;
                    cursor: pointer;
                    border-radius: 5px;
                }}
                button:hover {{ background: rgba(255,255,255,0.2); }}
            </style>
        </head>
        <body>
            <video id="player" controls autoplay>
                <source src="{stream_url}" type="{mime_type}">
                Your browser does not support the video tag.
            </video>
            <div class="controls">
                <button onclick="skip(-10)">⏪ 10s</button>
                <button onclick="skip(10)">⏩ 10s</button>
            </div>
            <script>
                const video = document.getElementById("player");
                function skip(seconds) {{
                    video.currentTime += seconds;
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except PeerIdInvalid:
        raise HTTPException(status_code=404, detail="File not found")
