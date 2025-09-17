import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
WEB_BASE_URL = os.getenv("WEB_BASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PUBLIC_MODE = os.getenv("PUBLIC_MODE")  # No default, let it be None if not set
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

DATABASE_URL = os.getenv("DATABASE_URL")

# Basic validation
if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN in environment")
if not API_ID or not API_HASH:
    raise RuntimeError("Missing API_ID or API_HASH in environment")
if not WEB_BASE_URL:
    raise RuntimeError("Missing WEB_BASE_URL in environment")
if not LOG_CHANNEL_ID:
    raise RuntimeError("Missing LOG_CHANNEL_ID in environment")
if not DATABASE_URL:
    raise RuntimeError("Missing DATABASE_URL in environment")
