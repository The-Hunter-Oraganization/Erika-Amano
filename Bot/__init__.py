import os
import sys
import logging

from telethon import TelegramClient
from telethon.sessions import StringSession

if os.path.exists("error.log"):
    os.remove("error.log")

# ─── Logging ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("error.log"), logging.StreamHandler()],
)
LOG = logging.getLogger("Erika-Amano")

# ─── Environment Variables ───
LOG.info("Checking Bot Variables...")

TRIGGERS = os.environ.get("TRIGGERS", "/ !").split(" ")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))
MONGO_DB = os.environ.get("MONGO_DB", "")
FILES_CHANNEL = int(os.environ.get("FILES_CHANNEL", 0))
BOT_NAME = os.environ.get("BOT_NAME", "Erika")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# ─── New feature env vars ───
AUTO_AUTH = os.environ.get("AUTO_AUTH", "false").lower() in ("true", "1", "yes")
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", 1))
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 0))  # bytes, 0 = unlimited
DAILY_QUOTA = int(os.environ.get("DAILY_QUOTA", 0))  # 0 = unlimited
NOTIFICATION_CHANNEL = int(os.environ.get("NOTIFICATION_CHANNEL", 0))
WATERMARK_TEXT = os.environ.get("WATERMARK_TEXT", "")
WATERMARK_IMAGE = os.environ.get("WATERMARK_IMAGE", "")  # path to overlay image
HW_ACCEL = os.environ.get("HW_ACCEL", "auto")  # auto, nvenc, vaapi, none

# ─── Validate required vars ───
_missing = []
if not BOT_TOKEN:
    _missing.append("BOT_TOKEN")
if not API_ID:
    _missing.append("API_ID")
if not API_HASH:
    _missing.append("API_HASH")
if not OWNER_ID:
    _missing.append("OWNER_ID")
if not MONGO_DB:
    _missing.append("MONGO_DB")

if _missing:
    LOG.critical(f"Missing required environment variables: {', '.join(_missing)}")
    sys.exit(1)

# ─── Create dirs ───
os.makedirs("downloads", exist_ok=True)

# ─── Bot client (connected in __main__.py) ───
bot = TelegramClient("ErikaBot", API_ID, API_HASH)

# ─── Optional userbot for 4GB uploads ───
ubot = None
if SESSION_STRING:
    ubot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
