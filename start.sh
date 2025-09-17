#!/bin/sh
set -e

echo "⏰ Setting timezone to Asia/Bangkok..."
export TZ=Asia/Bangkok

echo "🚀 Starting FastAPI server with Uvicorn..."
exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT}
