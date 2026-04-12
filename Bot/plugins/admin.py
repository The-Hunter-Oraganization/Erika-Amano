import os
import asyncio
from datetime import datetime, timezone

from telethon import events

from Bot import bot, OWNER_ID, LOG
from Bot.plugins.database.mongo_db import (
    get_all_users,
    get_user_count,
    ban_user,
    unban_user,
    is_banned,
    get_all_bans,
    set_bot_state,
    get_bot_state,
    get_all_history,
    get_pending_queue,
)
from Bot.utils.ffmpeg import humanbytes


# ─── /users Command (Owner Only) ───

@bot.on(events.NewMessage(pattern=r"^[/!]users$", from_users=OWNER_ID))
async def users_command(event):
    """List all authorized users."""
    all_users = await get_all_users()
    count = len(all_users)

    if count == 0:
        await event.respond("**No authorized users.**")
        return

    text = f"**👥 Authorized Users ({count})**\n\n"

    for i, user_doc in enumerate(all_users, 1):
        uid = user_doc.get("user_id", "?")
        res = user_doc.get("resolution", "?")
        vcodec = user_doc.get("vcodec", "?")
        try:
            entity = await bot.get_entity(int(uid))
            name = getattr(entity, "first_name", str(uid)) or str(uid)
        except Exception:
            name = str(uid)
        text += f"`{i}.` [{name}](tg://user?id={uid}) — `{res}` / `{vcodec}`\n"

        if len(text) > 3800:
            text += f"\n_...and {count - i} more_"
            break

    await event.respond(text, link_preview=False)


# ─── /broadcast Command (Owner Only) ───

@bot.on(events.NewMessage(pattern=r"^[/!]broadcast", from_users=OWNER_ID))
async def broadcast_command(event):
    """Broadcast a message to all authorized users.

    Usage: /broadcast <message>
    Or reply to a message with /broadcast
    """
    reply = await event.get_reply_message()
    text_parts = event.raw_text.split(None, 1)
    broadcast_text = None

    if reply:
        pass  # Will forward
    elif len(text_parts) > 1:
        broadcast_text = text_parts[1]
    else:
        await event.respond("**Usage:** `/broadcast <message>` or reply to a message with `/broadcast`")
        return

    all_users = await get_all_users()
    success = 0
    failed = 0
    status_msg = await event.respond(f"**Broadcasting to {len(all_users)} users...**")

    for user_doc in all_users:
        uid = user_doc.get("user_id")
        if uid == OWNER_ID:
            continue
        try:
            if reply:
                await bot.forward_messages(uid, reply)
            else:
                await bot.send_message(uid, broadcast_text)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.3)

    await status_msg.edit(
        f"**Broadcast Complete**\n\n"
        f"**Success:** `{success}`\n"
        f"**Failed:** `{failed}`"
    )


# ─── /log Command (Owner Only) ───

@bot.on(events.NewMessage(pattern=r"^[/!]log$", from_users=OWNER_ID))
async def log_command(event):
    """Send the error.log file to the owner."""
    log_path = "error.log"

    if not os.path.exists(log_path):
        await event.respond("**No log file found.**")
        return

    file_size = os.path.getsize(log_path)
    if file_size == 0:
        await event.respond("**Log file is empty.**")
        return

    try:
        await event.respond("**📄 Bot Log File:**", file=log_path)
    except Exception as e:
        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
            tail = "".join(lines[-50:])
            await event.respond(f"**Last 50 log lines:**\n\n```\n{tail[:4000]}\n```")
        except Exception as e2:
            await event.respond(f"**Failed to send log:** `{e2}`")


# ═══════════════════════════════════════════
# /ban & /unban — Ban system (Owner Only)
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]ban", from_users=OWNER_ID))
async def ban_command(event):
    """Ban a user from using the bot.

    Usage: /ban <user_id> [reason]
    """
    parts = event.raw_text.split(None, 2)
    if len(parts) < 2:
        await event.respond("**Usage:** `/ban <user_id> [reason]`")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await event.respond("**Invalid user ID.**")
        return

    if target_id == OWNER_ID:
        await event.respond("**Cannot ban the owner.**")
        return

    reason = parts[2] if len(parts) > 2 else "No reason specified"
    await ban_user(target_id, reason)

    try:
        entity = await bot.get_entity(target_id)
        name = getattr(entity, "first_name", str(target_id))
    except Exception:
        name = str(target_id)

    await event.respond(f"**🚫 Banned** [{name}](tg://user?id={target_id})\n**Reason:** `{reason}`")
    LOG.info(f"Banned user {target_id}: {reason}")


@bot.on(events.NewMessage(pattern=r"^[/!]unban", from_users=OWNER_ID))
async def unban_command(event):
    """Unban a user.

    Usage: /unban <user_id>
    """
    parts = event.raw_text.split()
    if len(parts) < 2:
        await event.respond("**Usage:** `/unban <user_id>`")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await event.respond("**Invalid user ID.**")
        return

    result = await unban_user(target_id)
    if result:
        await event.respond(f"**✅ Unbanned** `{target_id}`")
    else:
        await event.respond(f"**User `{target_id}` was not banned.**")


@bot.on(events.NewMessage(pattern=r"^[/!]bans$", from_users=OWNER_ID))
async def bans_command(event):
    """List all banned users."""
    bans = await get_all_bans()
    if not bans:
        await event.respond("**No banned users.**")
        return

    text = f"**🚫 Banned Users ({len(bans)})**\n\n"
    for b in bans:
        uid = b.get("user_id", "?")
        reason = b.get("reason", "?")
        ts = b.get("banned_at", "?")
        if hasattr(ts, "strftime"):
            ts = ts.strftime("%Y-%m-%d")
        text += f"• `{uid}` — {reason} ({ts})\n"

        if len(text) > 3800:
            text += f"\n_...and more_"
            break

    await event.respond(text)


# ═══════════════════════════════════════════
# /maintenance — Maintenance mode (Owner Only)
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]maintenance", from_users=OWNER_ID))
async def maintenance_command(event):
    """Toggle maintenance mode.

    Usage:
      /maintenance on [message] — Enable maintenance
      /maintenance off — Disable maintenance
    """
    parts = event.raw_text.split(None, 2)
    if len(parts) < 2:
        current = await get_bot_state("maintenance")
        status = "enabled" if current else "disabled"
        msg = ""
        if current and isinstance(current, dict):
            msg = current.get("message", "")
        await event.respond(
            f"**🔧 Maintenance Mode:** `{status}`\n"
            f"**Message:** `{msg or 'default'}`\n\n"
            "`/maintenance on [message]` — Enable\n"
            "`/maintenance off` — Disable"
        )
        return

    action = parts[1].lower()
    if action == "on":
        message = parts[2] if len(parts) > 2 else "Bot is under maintenance. Please try again later."
        await set_bot_state("maintenance", {"enabled": True, "message": message})
        await event.respond(f"**🔧 Maintenance mode ENABLED.**\n**Message:** `{message}`")
        LOG.info("Maintenance mode enabled")
    elif action == "off":
        await set_bot_state("maintenance", None)
        await event.respond("**✅ Maintenance mode DISABLED.**")
        LOG.info("Maintenance mode disabled")
    else:
        await event.respond("**Usage:** `/maintenance on [message]` or `/maintenance off`")


# ═══════════════════════════════════════════
# /stats — Enhanced statistics (Owner Only)
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]stats$", from_users=OWNER_ID))
async def stats_command(event):
    """Show comprehensive bot statistics."""
    user_count = await get_user_count()
    log_size = os.path.getsize("error.log") if os.path.exists("error.log") else 0

    dl_dir = "downloads"
    dl_count = len(os.listdir(dl_dir)) if os.path.exists(dl_dir) else 0

    from Bot.plugins.encoder import _task_queue, _active_tasks, MAX_CONCURRENT

    # Ban count
    bans = await get_all_bans()
    ban_count = len(bans) if bans else 0

    # Pending queue in DB
    pending_queue = await get_pending_queue()
    persist_count = len(pending_queue) if pending_queue else 0

    # Encoding history stats
    all_history = await get_all_history(limit=1000)
    total_encodes = len(all_history) if all_history else 0
    total_saved = 0
    for rec in (all_history or []):
        orig = rec.get("original_size", 0)
        enc = rec.get("encoded_size", 0)
        if orig > enc:
            total_saved += orig - enc

    # Maintenance status
    maint = await get_bot_state("maintenance")
    maint_status = "ON" if maint else "OFF"

    text = (
        "**📊 Bot Statistics**\n\n"
        f"**Authorized Users:** `{user_count}`\n"
        f"**Banned Users:** `{ban_count}`\n"
        f"**Maintenance Mode:** `{maint_status}`\n\n"
        f"**Queue Size:** `{len(_task_queue)}`\n"
        f"**Active Encodes:** `{_active_tasks}/{MAX_CONCURRENT}`\n"
        f"**Persistent Queue:** `{persist_count}`\n"
        f"**Files in Downloads:** `{dl_count}`\n\n"
        f"**Total Encodes (history):** `{total_encodes}`\n"
        f"**Total Space Saved:** `{humanbytes(total_saved)}`\n"
        f"**Log File Size:** `{humanbytes(log_size)}`"
    )
    await event.respond(text)
