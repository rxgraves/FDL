# FDL Bot - File Download and Streaming Bot 🚀

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.114.0-green?style=flat&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

FDL Bot is a Telegram bot built with FastAPI and Pyrogram, designed to allow users to upload files to a Telegram channel and generate secure, time-limited links for streaming or downloading. The bot stores session data in a PostgreSQL database to persist across deployments and uses modern Python libraries for optimal performance.

## Features ✨
- **File Upload and Link Generation**: Upload files (documents, videos, audios, photos, or voice messages) and get secure links.
- **Streaming and Downloading**: Supports direct streaming and instant downloads with save dialogs.
- **Session Persistence**: Bot session saved in PostgreSQL to avoid re-inviting after redeploys.
- **Secure Links**: Time-limited (24 hours) and code-protected links.
- **Admin-Protected Channel**: Files stored in a private log channel.

## Tech Stack 🛠️
- **Python 3.11**: Core language.
- **FastAPI 0.114.0**: For API endpoints.
- **Pyrogram**: Telegram bot framework.
- **psycopg 3.2.1**: PostgreSQL driver.
- **Uvicorn 0.31.0**: ASGI server.
- **Docker**: For containerization.

## Prerequisites 📋
- Python 3.11+ (for local dev).
- Docker (for deployment).
- PostgreSQL database (e.g., Aiven).
- Telegram Bot Token from [BotFather](https://t.me/BotFather).
- Telegram API ID/Hash from [my.telegram.org](https://my.telegram.org).
- A Telegram channel for file storage.

## Setup ⚙️

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fdl-bot
```

### 2. Configure Environment Variables
Copy `sample.env` to `.env` and fill in the values:
```env
BOT_TOKEN=your_bot_token_here
API_ID=1234567
API_HASH=your_api_hash_here
WEB_BASE_URL=https://yourdomain.com/
ADMIN_ID=123456789
PUBLIC_MODE=on
LOG_CHANNEL_ID=-100123456789
DATABASE_URL=postgresql://user:password@hostname:5432/dbname?sslmode=require
```

### 3. Local Run Instructions 🖥️
For development/testing:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Database**:
   - Ensure PostgreSQL is running.
   - Update `DATABASE_URL` in `.env`.

3. **Run the App**:
   ```bash
   uvicorn app.server:app --host 0.0.0.0 --port 8000
   ```
   - Check logs for startup.
   - Health check: `http://localhost:8000/_health`.

4. **Invite Bot**:
   - Add bot to log channel as admin.
   - Session auto-saves to DB.

### 4. Docker Deployment 📦
For production (e.g., Railway):

1. **Build Image**:
   ```bash
   docker build -t fdl-bot .
   ```

2. **Run Container**:
   ```bash
   docker run -d -p 8000:8000 --env-file .env fdl-bot
   ```

3. **Deploy to Platform**:
   - Set env vars on platform.
   - Uses `start.sh` for timezone and Uvicorn.

## Usage 📖
1. **Start Bot**: Send `/start` in Telegram.
2. **Upload File**: Send media; get stream/download links.
3. **/fdl Command**: Reply to media with `/fdl` for links.
4. **Links**: Expire in 24 hours.

## Database Persistence 💾
- Session saved to `bot_sessions` table after channel access.
- Loads automatically on redeploy—no re-invite needed.

## Troubleshooting ❗
- **Download Spins**: Check `/dl` endpoint uses `StreamingResponse`.
- **Session Loss**: Verify DB connection and table data.
- **Logs**: Review for API/DB errors.

## Contributing 🤝
Fork, create PRs. Test changes locally.

## License 📄
MIT License.
