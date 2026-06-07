import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "0"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "200"))
DB_PATH     = os.getenv("DB_PATH", "./data/kassb.db")
EXPORT_DIR  = os.getenv("EXPORT_DIR", "./data/exports")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")
