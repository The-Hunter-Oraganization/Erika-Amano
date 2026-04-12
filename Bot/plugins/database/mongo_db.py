import time
from datetime import datetime, timezone

import motor.motor_asyncio

from Bot import MONGO_DB as DB_URL, BOT_NAME, OWNER_ID, LOG

# ─── Async MongoDB Client ───
cluster = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
db = cluster["Encoding"]
users = db[BOT_NAME]
history_col = db[f"{BOT_NAME}_history"]
profiles_col = db[f"{BOT_NAME}_profiles"]
queue_col = db[f"{BOT_NAME}_queue"]
bans_col = db[f"{BOT_NAME}_bans"]
bot_state = db[f"{BOT_NAME}_state"]

# Default user settings
DEFAULT_SETTINGS = {
    "resolution": "480p",
    "preset": "fast",
    "audio_type": "aac",
    "vcodec": "x264",
    "crf": 26,
    "rename_pattern": "",
    "auto_delete": False,
    "watermark_text": "",
    "watermark_image": "",
    "hw_accel": "auto",
    "audio_tracks": "",     # e.g. "0,1" or empty for all
    "subtitle_tracks": "",  # e.g. "0" or empty for all
    "schedule": "",         # "", "off-peak", "night", "custom HH:MM-HH:MM"
}


# ═══════════════════════════════════════════
# USER CRUD
# ═══════════════════════════════════════════

async def check_user_mdb(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return int(doc["user_id"])
    return None


async def get_user_settings(user_id: int):
    return await users.find_one({"user_id": int(user_id)})


async def check_crf_mdb(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return int(doc.get("crf", 26))
    return None


async def check_resolution_settings(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return doc.get("resolution", "480p")
    return None


async def check_preset_settings(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return doc.get("preset", "fast")
    return None


async def check_vcodec_settings(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return doc.get("vcodec", "x264")
    return None


async def check_audio_type_mdb(user_id: int):
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return str(doc.get("audio_type", "aac"))
    return None


async def update_resolution_settings(user_id: int, new: str):
    await users.update_one({"user_id": int(user_id)}, {"$set": {"resolution": new}})
    return "Success"


async def update_preset_settings(user_id: int, new: str):
    await users.update_one({"user_id": int(user_id)}, {"$set": {"preset": new}})
    return "Success"


async def update_vcodec_settings(user_id: int, new: str):
    await users.update_one({"user_id": int(user_id)}, {"$set": {"vcodec": new}})
    return "Success"


async def update_audio_type_mdb(user_id: int, new: str):
    await users.update_one({"user_id": int(user_id)}, {"$set": {"audio_type": new}})
    return "Success"


async def update_crf(user_id: int, new: int):
    await users.update_one({"user_id": int(user_id)}, {"$set": {"crf": new}})
    return "Success"


async def update_user_field(user_id: int, field: str, value):
    """Generic update for any user settings field."""
    await users.update_one({"user_id": int(user_id)}, {"$set": {field: value}})
    return "Success"


async def get_user_field(user_id: int, field: str, default=None):
    """Generic getter for any user settings field."""
    doc = await users.find_one({"user_id": int(user_id)})
    if doc is not None:
        return doc.get(field, default)
    return default


async def authorize_user(user_id: int):
    existing = await check_user_mdb(user_id)
    if existing is None:
        await users.insert_one({"user_id": int(user_id), **DEFAULT_SETTINGS})
    return "Success"


async def unauthorize_user(user_id: int):
    await users.delete_one({"user_id": int(user_id)})
    return "Success"


async def get_all_users():
    return await users.find().to_list(length=None)


async def get_user_count():
    return await users.count_documents({})


# ═══════════════════════════════════════════
# BAN SYSTEM
# ═══════════════════════════════════════════

async def ban_user(user_id: int, reason: str = ""):
    await bans_col.update_one(
        {"user_id": int(user_id)},
        {"$set": {"user_id": int(user_id), "reason": reason, "banned_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True,
    )
    return "Success"


async def unban_user(user_id: int):
    await bans_col.delete_one({"user_id": int(user_id)})
    return "Success"


async def is_banned(user_id: int):
    doc = await bans_col.find_one({"user_id": int(user_id)})
    return doc


async def get_all_bans():
    return await bans_col.find().to_list(length=None)


# ═══════════════════════════════════════════
# ENCODING HISTORY
# ═══════════════════════════════════════════

async def add_history(user_id: int, filename: str, original_size: int, encoded_size: int, resolution: str, duration_secs: float):
    await history_col.insert_one({
        "user_id": int(user_id),
        "filename": filename,
        "original_size": original_size,
        "encoded_size": encoded_size,
        "resolution": resolution,
        "duration_secs": round(duration_secs, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


async def get_history(user_id: int, limit: int = 10):
    cursor = history_col.find({"user_id": int(user_id)}).sort("_id", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_all_history(limit: int = 20):
    cursor = history_col.find().sort("_id", -1).limit(limit)
    return await cursor.to_list(length=limit)


# ═══════════════════════════════════════════
# PRESET PROFILES
# ═══════════════════════════════════════════

PROFILE_FIELDS = ["resolution", "preset", "audio_type", "vcodec", "crf", "hw_accel"]


async def save_profile(user_id: int, name: str):
    """Save current user settings as a named profile."""
    doc = await get_user_settings(user_id)
    if doc is None:
        return None
    profile_data = {k: doc.get(k, DEFAULT_SETTINGS.get(k)) for k in PROFILE_FIELDS}
    profile_data["user_id"] = int(user_id)
    profile_data["name"] = name.lower().strip()
    await profiles_col.update_one(
        {"user_id": int(user_id), "name": name.lower().strip()},
        {"$set": profile_data},
        upsert=True,
    )
    return "Success"


async def load_profile(user_id: int, name: str):
    """Load a named profile into user settings."""
    doc = await profiles_col.find_one({"user_id": int(user_id), "name": name.lower().strip()})
    if doc is None:
        return None
    update_data = {k: doc[k] for k in PROFILE_FIELDS if k in doc}
    await users.update_one({"user_id": int(user_id)}, {"$set": update_data})
    return update_data


async def delete_profile(user_id: int, name: str):
    result = await profiles_col.delete_one({"user_id": int(user_id), "name": name.lower().strip()})
    return result.deleted_count > 0


async def list_profiles(user_id: int):
    cursor = profiles_col.find({"user_id": int(user_id)})
    return await cursor.to_list(length=50)


# ═══════════════════════════════════════════
# QUEUE PERSISTENCE (resume on restart)
# ═══════════════════════════════════════════

async def persist_queue_item(user_id: int, chat_id: int, message_id: int):
    """Save a pending queue item so it survives restarts."""
    await queue_col.insert_one({
        "user_id": int(user_id),
        "chat_id": int(chat_id),
        "message_id": int(message_id),
        "added_at": time.time(),
    })


async def get_pending_queue():
    """Get all persisted queue items, oldest first."""
    return await queue_col.find().sort("added_at", 1).to_list(length=None)


async def remove_queue_item(chat_id: int, message_id: int):
    await queue_col.delete_one({"chat_id": int(chat_id), "message_id": int(message_id)})


async def clear_queue():
    await queue_col.delete_many({})


# ═══════════════════════════════════════════
# BOT STATE (maintenance mode, etc.)
# ═══════════════════════════════════════════

async def set_bot_state(key: str, value):
    await bot_state.update_one({"key": key}, {"$set": {"key": key, "value": value}}, upsert=True)


async def get_bot_state(key: str, default=None):
    doc = await bot_state.find_one({"key": key})
    if doc:
        return doc.get("value", default)
    return default


# ═══════════════════════════════════════════
# DAILY QUOTA
# ═══════════════════════════════════════════

async def increment_daily_usage(user_id: int):
    """Increment the user's daily encode count. Returns the new count."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"quota_{user_id}_{today}"
    result = await bot_state.find_one_and_update(
        {"key": key},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True,
    )
    return result.get("value", 1)


async def get_daily_usage(user_id: int):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    key = f"quota_{user_id}_{today}"
    doc = await bot_state.find_one({"key": key})
    return doc.get("value", 0) if doc else 0


# ═══════════════════════════════════════════
# OWNER CHECK
# ═══════════════════════════════════════════

async def owner_check():
    check = await check_user_mdb(OWNER_ID)
    if check is None:
        await users.insert_one({"user_id": OWNER_ID, **DEFAULT_SETTINGS})
        LOG.info(f"Owner {OWNER_ID} auto-authorized in database.")