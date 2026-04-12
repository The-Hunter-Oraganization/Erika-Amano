import time
import os
import re
import asyncio
from collections import deque
from datetime import datetime, timezone

from telethon import events, Button
from telethon.tl.types import DocumentAttributeFilename

from Bot import (
    bot, ubot, OWNER_ID, LOG, FILES_CHANNEL,
    MAX_CONCURRENT, MAX_FILE_SIZE, DAILY_QUOTA, NOTIFICATION_CHANNEL, AUTO_AUTH,
)
from Bot.plugins.database.mongo_db import (
    check_user_mdb, check_resolution_settings,
    get_user_field, is_banned, get_bot_state,
    increment_daily_usage, get_daily_usage,
    persist_queue_item, remove_queue_item,
    add_history, authorize_user,
)
from Bot.utils.decorators import build_ffmpeg_cmd
from Bot.utils.ffmpeg import ffmpeg_progress, humanbytes, get_video_duration
from Bot.utils.progress_pyro import progress_callback

# ─── Task Queue ───
_task_queue: deque = deque()
_active_tasks = 0  # number of currently encoding tasks
_active_lock = asyncio.Lock()
_proc_holders = {}  # {user_id: {"process": ...}} for cancel
_current_user_ids = set()  # set of user_ids currently encoding

VIDEO_MIMETYPES = {
    "video/x-flv", "video/mp4", "application/x-mpegURL",
    "video/MP2T", "video/3gpp", "video/quicktime",
    "video/x-msvideo", "video/x-ms-wmv", "video/x-matroska",
    "video/webm", "video/x-m4v", "video/mpeg",
}


def _is_video(event) -> bool:
    """Check if the message contains a video file."""
    if event.video:
        return True
    if event.document:
        mime = event.document.mime_type or ""
        if mime in VIDEO_MIMETYPES or mime.startswith("video/"):
            return True
    return False


def _apply_rename_pattern(pattern: str, original_name: str, resolution: str) -> str:
    """Apply rename pattern to generate output filename.

    Supported placeholders: {title}, {res}, {codec}, {ext}
    """
    if not pattern:
        return original_name
    name_part = original_name.rsplit(".", 1)[0]
    ext_part = original_name.rsplit(".", 1)[1] if "." in original_name else "mp4"
    result = pattern.replace("{title}", name_part)
    result = result.replace("{res}", resolution)
    result = result.replace("{ext}", ext_part)
    # Sanitize filename
    result = re.sub(r'[<>:"/\\|?*]', '_', result)
    if not result.endswith(f".{ext_part}"):
        result += f".{ext_part}"
    return result


def _is_scheduled_ok(schedule: str) -> bool:
    """Check if current time is within the user's schedule window. Empty = always OK."""
    if not schedule:
        return True

    now = datetime.now(timezone.utc)
    hour = now.hour

    if schedule == "off-peak":
        # Off-peak: 00:00 - 08:00 UTC
        return 0 <= hour < 8
    elif schedule == "night":
        # Night: 20:00 - 06:00 UTC
        return hour >= 20 or hour < 6
    elif "-" in schedule:
        # Custom: "HH:MM-HH:MM" (24h UTC)
        try:
            parts = schedule.split("-")
            start_h = int(parts[0].split(":")[0])
            end_h = int(parts[1].split(":")[0])
            if start_h <= end_h:
                return start_h <= hour < end_h
            else:
                return hour >= start_h or hour < end_h
        except (ValueError, IndexError):
            return True
    return True


async def _process_queue():
    """Process encoding tasks, respecting MAX_CONCURRENT."""
    global _active_tasks

    while _task_queue:
        async with _active_lock:
            if _active_tasks >= MAX_CONCURRENT:
                return
            _active_tasks += 1

        task_data = _task_queue.popleft()
        asyncio.create_task(_run_encode_task(task_data))

        # Small delay to let the lock release
        await asyncio.sleep(0.1)


async def _run_encode_task(task_data):
    """Wrapper that manages active task count."""
    global _active_tasks
    try:
        event = task_data["event"]
        trim_start = task_data.get("trim_start", "")
        trim_end = task_data.get("trim_end", "")
        await _encode_video(event, trim_start=trim_start, trim_end=trim_end)
    except Exception as e:
        LOG.error(f"Encoding task failed: {e}")
        try:
            await task_data["event"].respond(f"**Encoding failed:** `{e}`")
        except Exception:
            pass
    finally:
        async with _active_lock:
            _active_tasks -= 1
        # Check if more tasks to process
        if _task_queue:
            await _process_queue()


async def _encode_video(event, trim_start: str = "", trim_end: str = ""):
    """Download, encode, and upload a single video."""
    user_id = event.sender_id
    _current_user_ids.add(user_id)
    proc_holder = {}
    _proc_holders[user_id] = proc_holder

    encode_start = time.time()
    progress_file = f"progress-{encode_start}.txt"
    filepath = None
    output_path = None
    thumb_path = None

    status_msg = await event.reply("**Downloading...**")

    try:
        # Download
        filepath = await bot.download_media(
            event.message,
            file="downloads/",
            progress_callback=lambda c, t: progress_callback(c, t, event, status_msg, encode_start, "**Downloading...**"),
        )

        if not filepath:
            await status_msg.edit("**Download failed.**")
            return

        # Build FFmpeg command (with trim support)
        cmd, output_path = await build_ffmpeg_cmd(user_id, filepath, progress_file,
                                                   trim_start=trim_start, trim_end=trim_end)

        await status_msg.edit("**Encoding...**")

        # Run FFmpeg with progress
        return_code = await ffmpeg_progress(cmd, filepath, progress_file, encode_start, status_msg, "**Encoding in progress**", proc_holder)

        if return_code != 0:
            await status_msg.edit("**Encoding failed.** FFmpeg returned an error.")
            return

        if not os.path.exists(output_path):
            await status_msg.edit("**Encoding failed.** Output file not found.")
            return

        # Get resolution for caption
        resolution = await check_resolution_settings(user_id) or "480p"

        # Get original filename
        original_name = os.path.basename(filepath)
        file_name_base = original_name.rsplit(".", 1)[0]
        ext = original_name.rsplit(".", 1)[1] if "." in original_name else "mp4"

        # Apply custom rename pattern
        rename_pattern = await get_user_field(user_id, "rename_pattern", "")
        if rename_pattern:
            # Also support {codec} placeholder
            vcodec = await get_user_field(user_id, "vcodec", "x264")
            display_name = rename_pattern.replace("{title}", file_name_base)
            display_name = display_name.replace("{res}", resolution)
            display_name = display_name.replace("{codec}", vcodec or "x264")
            display_name = display_name.replace("{ext}", ext)
            display_name = re.sub(r'[<>:"/\\|?*]', '_', display_name)
            if not display_name.endswith(f".{ext}"):
                display_name += f".{ext}"
        else:
            display_name = f"{file_name_base}.{ext}"

        # File size comparison
        original_size = os.path.getsize(filepath)
        encoded_size = os.path.getsize(output_path)
        saved = original_size - encoded_size
        saved_pct = (saved / original_size * 100) if original_size > 0 else 0
        duration_secs = time.time() - encode_start

        caption = (
            f"**{resolution}** | `{display_name}`\n\n"
            f"**Original:** `{humanbytes(original_size)}`\n"
            f"**Encoded:** `{humanbytes(encoded_size)}`\n"
            f"**Saved:** `{humanbytes(abs(saved))} ({saved_pct:.1f}%)`\n"
            f"**Time:** `{int(duration_secs)}s`"
        )

        await status_msg.edit("**Uploading...**")

        upload_start = time.time()

        # Extract thumbnail from the encoded video
        thumb_path = filepath.rsplit(".", 1)[0] + "_thumb.jpg"
        try:
            thumb_proc = await asyncio.create_subprocess_shell(
                f'ffmpeg -i "{output_path}" -ss 00:00:01 -vframes 1 -q:v 2 "{thumb_path}" -y',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await thumb_proc.wait()
            if not os.path.exists(thumb_path):
                thumb_path = None
        except Exception:
            thumb_path = None

        # Upload to files channel (use ubot for 4GB+ support if available)
        uploader = ubot if ubot else bot
        upload_msg = await uploader.send_file(
            FILES_CHANNEL,
            output_path,
            caption=caption,
            thumb=thumb_path,
            force_document=True,
            progress_callback=lambda c, t: progress_callback(c, t, event, status_msg, upload_start, "**Uploading...**"),
            attributes=[DocumentAttributeFilename(display_name)],
        )

        # Forward to user
        await bot.forward_messages(event.chat_id, upload_msg)

        # Clean up status message
        await status_msg.delete()

        # ─── Post-encode actions ───

        # Save to history
        try:
            await add_history(user_id, display_name, original_size, encoded_size, resolution, duration_secs)
        except Exception as e:
            LOG.warning(f"Failed to save history: {e}")

        # Increment daily usage
        try:
            await increment_daily_usage(user_id)
        except Exception:
            pass

        # Remove from persistent queue
        try:
            await remove_queue_item(event.chat_id, event.id)
        except Exception:
            pass

        # Notification channel
        if NOTIFICATION_CHANNEL:
            try:
                await bot.send_message(
                    NOTIFICATION_CHANNEL,
                    f"✅ **Encode Complete**\n"
                    f"**User:** `{user_id}`\n"
                    f"**File:** `{display_name}`\n"
                    f"**{humanbytes(original_size)}** → **{humanbytes(encoded_size)}** ({saved_pct:.1f}% saved)\n"
                    f"**Time:** `{int(duration_secs)}s`",
                )
            except Exception:
                pass

        # Auto-delete original message
        auto_delete = await get_user_field(user_id, "auto_delete", False)
        if auto_delete:
            try:
                await event.delete()
            except Exception:
                pass

    except Exception as e:
        LOG.error(f"Error in encode pipeline: {e}")
        try:
            await status_msg.edit(f"**Error:** `{e}`")
        except Exception:
            pass
    finally:
        _proc_holders.pop(user_id, None)
        _current_user_ids.discard(user_id)
        # Clean up files
        for f in [filepath, output_path, progress_file, thumb_path]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass


async def _check_and_enqueue(event, trim_start: str = "", trim_end: str = ""):
    """Common authorization/quota/ban/maintenance/size/schedule checks, then enqueue."""
    user_id = event.sender_id

    # Check ban
    ban_doc = await is_banned(user_id)
    if ban_doc:
        reason = ban_doc.get("reason", "No reason given")
        await event.respond(f"**You are banned.** Reason: `{reason}`")
        return

    # Check maintenance mode
    maintenance = await get_bot_state("maintenance", False)
    if maintenance and user_id != OWNER_ID:
        maint_msg = await get_bot_state("maintenance_msg", "Bot is under maintenance. Please try later.")
        await event.respond(f"**🔧 Maintenance Mode**\n\n{maint_msg}")
        return

    # Check authorization (+ auto-auth)
    check = await check_user_mdb(user_id)
    if check is None:
        if AUTO_AUTH:
            await authorize_user(user_id)
        else:
            await event.respond(
                "You're not authorized to use this bot. Request Admins to approve you.",
                buttons=[[Button.inline("ʀᴇǫᴜᴇsᴛ", f"users_request-{user_id}".encode())]],
            )
            return

    # Check daily quota
    if DAILY_QUOTA > 0 and user_id != OWNER_ID:
        usage = await get_daily_usage(user_id)
        if usage >= DAILY_QUOTA:
            await event.respond(f"**Daily quota reached.** Limit: `{DAILY_QUOTA}` encodes/day.")
            return

    # Check file size limit
    if MAX_FILE_SIZE > 0 and event.document:
        file_size = event.document.size or 0
        if file_size > MAX_FILE_SIZE:
            await event.respond(
                f"**File too large.** Max: `{humanbytes(MAX_FILE_SIZE)}`, "
                f"yours: `{humanbytes(file_size)}`"
            )
            return

    # Check schedule
    schedule = await get_user_field(user_id, "schedule", "")
    if schedule and not _is_scheduled_ok(schedule):
        await event.respond(
            f"**Scheduled encoding active.** Your schedule: `{schedule}`\n"
            "Your video will be queued and processed when the window opens."
        )
        # Still enqueue but mark it - it will be processed when schedule is checked

    # Persist queue item for restart resilience
    try:
        await persist_queue_item(user_id, event.chat_id, event.id)
    except Exception:
        pass

    _task_queue.append({"event": event, "trim_start": trim_start, "trim_end": trim_end})

    if len(_task_queue) > 1 or _active_tasks >= MAX_CONCURRENT:
        pos = len(_task_queue)
        await event.reply(f"**Added to queue.** Position: `{pos}` | Active: `{_active_tasks}/{MAX_CONCURRENT}`")

    await _process_queue()


@bot.on(events.NewMessage(func=lambda e: e.is_private and (e.video or e.document)))
async def encoder_handler(event):
    """Handle incoming video/document messages for encoding."""
    if not _is_video(event):
        return
    await _check_and_enqueue(event)


# ─── /cancel Command ───

@bot.on(events.NewMessage(pattern=r"^[/!]cancel$"))
async def cancel_command(event):
    """Cancel the current encoding task."""
    user_id = event.sender_id
    check = await check_user_mdb(user_id)
    if check is None:
        return

    # Owner can cancel any, users can cancel their own
    if user_id == OWNER_ID:
        # Cancel all active
        cancelled = 0
        for uid, holder in list(_proc_holders.items()):
            proc = holder.get("process")
            if proc:
                try:
                    proc.kill()
                    cancelled += 1
                except Exception:
                    pass
        if cancelled:
            await event.respond(f"**Cancelled {cancelled} task(s).**")
        else:
            await event.respond("**No active encoding tasks found.**")
        return

    holder = _proc_holders.get(user_id)
    if not holder:
        await event.respond("**You don't have an active encoding task.**")
        return

    proc = holder.get("process")
    if proc is None:
        await event.respond("**Process not found. It may be downloading or uploading.**")
        return

    try:
        proc.kill()
        await event.respond("**Encoding cancelled!**")
    except Exception as e:
        await event.respond(f"**Failed to cancel:** `{e}`")


# ─── /queue Command ───

@bot.on(events.NewMessage(pattern=r"^[/!]queue$"))
async def queue_command(event):
    """Show the current encoding queue status."""
    user_id = event.sender_id
    check = await check_user_mdb(user_id)
    if check is None:
        return

    queue_len = len(_task_queue)
    if _active_tasks == 0 and queue_len == 0:
        await event.respond("**Queue is empty.** No tasks running.")
        return

    text = f"**📋 Encoding Queue**\n\n"
    text += f"**Active encoders:** `{_active_tasks}/{MAX_CONCURRENT}`\n"
    if _current_user_ids:
        text += f"**Encoding for:** `{', '.join(str(u) for u in _current_user_ids)}`\n"
    text += f"**Waiting in queue:** `{queue_len}` task(s)"
    await event.respond(text)


async def resume_pending_queue():
    """Called at startup to re-enqueue persisted tasks."""
    from Bot.plugins.database.mongo_db import get_pending_queue, clear_queue
    pending = await get_pending_queue()
    if not pending:
        return
    LOG.info(f"Resuming {len(pending)} pending queue items from database...")
    for item in pending:
        try:
            chat_id = item["chat_id"]
            message_id = item["message_id"]
            # Try to get the original message
            msg = await bot.get_messages(chat_id, ids=message_id)
            if msg and (msg.video or msg.document):
                _task_queue.append({"event": msg, "trim_start": "", "trim_end": ""})
            else:
                await remove_queue_item(chat_id, message_id)
        except Exception as e:
            LOG.warning(f"Failed to resume queue item: {e}")
    if _task_queue:
        LOG.info(f"Resumed {len(_task_queue)} tasks. Starting processing...")
        await _process_queue()
    # Clear old entries that couldn't be resumed
    await clear_queue()
