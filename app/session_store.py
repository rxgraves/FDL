import psycopg2, os
from psycopg2.extras import DictCursor
import logging

logger = logging.getLogger("session_store")

def ensure_session_table(db):
    with db.cursor() as c:
        c.execute(
            '''CREATE TABLE IF NOT EXISTS bot_sessions (
                   id SERIAL PRIMARY KEY,
                   session_data BYTEA,
                   updated_at TIMESTAMP DEFAULT NOW()
               )'''
        )
        db.commit()

def load_session_from_db(db, session_file):
    try:
        with db.cursor() as c:
            c.execute("SELECT session_data FROM bot_sessions ORDER BY id DESC LIMIT 1")
            row = c.fetchone()
            if row and row[0]:
                with open(session_file, "wb") as f:
                    f.write(row[0])
                logger.info("✅ Loaded session from DB into file %s", session_file)
                return True
    except Exception as e:
        logger.exception("Error loading session from DB")
    return False

def save_session_to_db(db, session_file):
    try:
        if not os.path.exists(session_file):
            return
        with open(session_file, "rb") as f:
            data = f.read()
        with db.cursor() as c:
            c.execute("DELETE FROM bot_sessions")
            c.execute("INSERT INTO bot_sessions (session_data) VALUES (%s)", (data,))
            db.commit()
        logger.info("✅ Saved session file %s to DB", session_file)
    except Exception as e:
        logger.exception("Error saving session to DB")
