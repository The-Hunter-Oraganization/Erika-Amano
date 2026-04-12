import os
import asyncio

from telethon import events, Button

from Bot import bot, OWNER_ID, LOG
from Bot.plugins.database.mongo_db import (
    check_user_mdb,
    get_user_field,
    update_user_field,
    save_profile,
    load_profile,
    delete_profile,
    list_profiles,
    get_history,
)
from Bot.utils.decorators import _get_stream_info
from Bot.utils.ffmpeg import generate_sample, humanbytes, get_video_duration


# ═══════════════════════════════════════════
# /rename — Custom rename pattern
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]rename"))
async def rename_command(event):
    """Set a custom rename pattern for encoded files.

    Usage: /rename [Erika] {title} [{res}].{ext}
    Placeholders: {title}, {res}, {codec}, {ext}
    Use /rename off to disable.
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    parts = event.raw_text.split(None, 1)
    if len(parts) < 2:
        current = await get_user_field(user_id, "rename_pattern", "")
        text = "**Custom Rename Pattern**\n\n"
        text += f"**Current:** `{current or 'disabled'}`\n\n"
        text += "**Usage:** `/rename [Erika] {title} [{res}].{ext}`\n"
        text += "**Placeholders:** `{title}`, `{res}`, `{codec}`, `{ext}`\n"
        text += "**Disable:** `/rename off`"
        await event.respond(text)
        return

    pattern = parts[1].strip()
    if pattern.lower() == "off":
        await update_user_field(user_id, "rename_pattern", "")
        await event.respond("**Rename pattern disabled.** Using original filenames.")
    else:
        await update_user_field(user_id, "rename_pattern", pattern)
        await event.respond(f"**Rename pattern set:** `{pattern}`")


# ═══════════════════════════════════════════
# /profile — Preset profiles
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]profile"))
async def profile_command(event):
    """Manage encoding profiles.

    Usage:
      /profile save <name> — Save current settings as a profile
      /profile load <name> — Load a saved profile
      /profile delete <name> — Delete a profile
      /profile list — List all profiles
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    parts = event.raw_text.split()
    if len(parts) < 2:
        await event.respond(
            "**Profile Manager**\n\n"
            "`/profile save <name>` — Save current settings\n"
            "`/profile load <name>` — Load a profile\n"
            "`/profile delete <name>` — Delete a profile\n"
            "`/profile list` — List all profiles"
        )
        return

    action = parts[1].lower()

    if action == "save" and len(parts) >= 3:
        name = parts[2]
        result = await save_profile(user_id, name)
        if result:
            await event.respond(f"**Profile `{name}` saved!**")
        else:
            await event.respond("**Failed to save profile.** Are you authorized?")

    elif action == "load" and len(parts) >= 3:
        name = parts[2]
        result = await load_profile(user_id, name)
        if result:
            text = f"**Profile `{name}` loaded!**\n\n"
            for k, v in result.items():
                text += f"**{k}:** `{v}`\n"
            await event.respond(text)
        else:
            await event.respond(f"**Profile `{name}` not found.**")

    elif action == "delete" and len(parts) >= 3:
        name = parts[2]
        result = await delete_profile(user_id, name)
        if result:
            await event.respond(f"**Profile `{name}` deleted.**")
        else:
            await event.respond(f"**Profile `{name}` not found.**")

    elif action == "list":
        profiles = await list_profiles(user_id)
        if not profiles:
            await event.respond("**No saved profiles.**")
            return
        text = "**Your Profiles:**\n\n"
        for p in profiles:
            text += f"• `{p['name']}` — {p.get('resolution', '?')} / {p.get('vcodec', '?')} / CRF {p.get('crf', '?')}\n"
        await event.respond(text)

    else:
        await event.respond("**Invalid usage.** Try `/profile` for help.")


# ═══════════════════════════════════════════
# /trim — Trim video before encoding
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]trim"))
async def trim_command(event):
    """Reply to a video with /trim <start> <end> to encode only a portion.

    Usage: /trim 00:05:00 00:45:00
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    reply = await event.get_reply_message()
    if not reply or not (reply.video or reply.document):
        await event.respond("**Reply to a video** with `/trim <start> <end>`\n\nExample: `/trim 00:05:00 00:45:00`")
        return

    parts = event.raw_text.split()
    if len(parts) < 3:
        await event.respond("**Usage:** `/trim <start_time> <end_time>`\n\nExample: `/trim 00:05:00 00:45:00`")
        return

    trim_start = parts[1]
    trim_end = parts[2]

    # Validate time format (basic check)
    import re
    time_pattern = r"^\d{1,2}(:\d{2}){0,2}(\.\d+)?$"
    if not re.match(time_pattern, trim_start) or not re.match(time_pattern, trim_end):
        await event.respond("**Invalid time format.** Use `HH:MM:SS` or `MM:SS` or seconds.")
        return

    await event.respond(f"**Trimming:** `{trim_start}` → `{trim_end}` and encoding...")

    # Use the encoder's _check_and_enqueue with trim params
    from Bot.plugins.encoder import _check_and_enqueue
    await _check_and_enqueue(reply, trim_start=trim_start, trim_end=trim_end)


# ═══════════════════════════════════════════
# /sample — Generate a preview clip
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]sample"))
async def sample_command(event):
    """Reply to a video with /sample [duration] to get a preview clip.

    Usage: /sample 30  (default: 30 seconds)
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    reply = await event.get_reply_message()
    if not reply or not (reply.video or reply.document):
        await event.respond("**Reply to a video** with `/sample [duration_seconds]`")
        return

    parts = event.raw_text.split()
    duration = 30
    if len(parts) >= 2:
        try:
            duration = int(parts[1])
            duration = max(5, min(duration, 120))
        except ValueError:
            pass

    status_msg = await event.respond("**Generating sample clip...**")

    try:
        # Download video
        filepath = await bot.download_media(reply.message, file="downloads/")
        if not filepath:
            await status_msg.edit("**Download failed.**")
            return

        # Get duration to calculate start point (start at 30s or 10% in)
        vid_duration = get_video_duration(filepath)
        start_at = "00:00:30"
        if vid_duration > 0:
            start_sec = max(0, int(vid_duration * 0.1))
            start_at = f"{start_sec // 3600:02d}:{(start_sec % 3600) // 60:02d}:{start_sec % 60:02d}"

        sample_path = await generate_sample(filepath, duration, start_at)

        if sample_path:
            await bot.send_file(
                event.chat_id,
                sample_path,
                caption=f"**Sample clip** ({duration}s)",
                reply_to=reply.id,
            )
            await status_msg.delete()
            os.remove(sample_path)
        else:
            await status_msg.edit("**Failed to generate sample.**")

        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)

    except Exception as e:
        LOG.error(f"Sample generation error: {e}")
        await status_msg.edit(f"**Error:** `{e}`")


# ═══════════════════════════════════════════
# /tracks — Audio/subtitle track selection
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]tracks"))
async def tracks_command(event):
    """View/set audio and subtitle track preferences.

    Usage:
      /tracks — Show current settings
      /tracks audio 0,1 — Keep audio tracks 0 and 1
      /tracks sub 0 — Keep subtitle track 0
      /tracks audio all — Keep all audio tracks
      /tracks sub all — Keep all subtitle tracks
    Or reply to a video with /tracks to see available streams.
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    parts = event.raw_text.split()

    # If replying to a video, show stream info
    reply = await event.get_reply_message()
    if reply and (reply.video or reply.document) and len(parts) == 1:
        status_msg = await event.respond("**Analyzing streams...**")
        try:
            filepath = await bot.download_media(reply.message, file="downloads/")
            if filepath:
                info = _get_stream_info(filepath)
                text = "**📋 Available Streams:**\n\n"

                if info["audio_streams"]:
                    text += "**Audio Tracks:**\n"
                    for a in info["audio_streams"]:
                        text += f"  `{a['index']}` — {a['codec']} / {a['lang']} / {a['title']}\n"
                else:
                    text += "**Audio:** None found\n"

                if info["subtitle_streams"]:
                    text += "\n**Subtitle Tracks:**\n"
                    for s in info["subtitle_streams"]:
                        text += f"  `{s['index']}` — {s['codec']} / {s['lang']} / {s['title']}\n"
                else:
                    text += "\n**Subtitles:** None found\n"

                text += "\n**Set tracks:** `/tracks audio 0,1` or `/tracks sub 0`"
                await status_msg.edit(text)
                os.remove(filepath)
            else:
                await status_msg.edit("**Failed to download for analysis.**")
        except Exception as e:
            await status_msg.edit(f"**Error:** `{e}`")
        return

    if len(parts) == 1:
        # Show current settings
        audio_tracks = await get_user_field(user_id, "audio_tracks", "")
        sub_tracks = await get_user_field(user_id, "subtitle_tracks", "")
        text = (
            "**🎵 Track Settings**\n\n"
            f"**Audio tracks:** `{audio_tracks or 'all'}`\n"
            f"**Subtitle tracks:** `{sub_tracks or 'all'}`\n\n"
            "**Set:** `/tracks audio 0,1` or `/tracks sub 0`\n"
            "**Reset:** `/tracks audio all` or `/tracks sub all`\n"
            "**Analyze:** Reply to a video with `/tracks`"
        )
        await event.respond(text)
        return

    if len(parts) >= 3:
        track_type = parts[1].lower()
        value = parts[2].strip()

        if track_type in ("audio", "a"):
            if value.lower() == "all":
                await update_user_field(user_id, "audio_tracks", "")
                await event.respond("**Audio tracks reset to all.**")
            else:
                await update_user_field(user_id, "audio_tracks", value)
                await event.respond(f"**Audio tracks set to:** `{value}`")

        elif track_type in ("sub", "subtitle", "s"):
            if value.lower() == "all":
                await update_user_field(user_id, "subtitle_tracks", "")
                await event.respond("**Subtitle tracks reset to all.**")
            else:
                await update_user_field(user_id, "subtitle_tracks", value)
                await event.respond(f"**Subtitle tracks set to:** `{value}`")
        else:
            await event.respond("**Invalid track type.** Use `audio` or `sub`.")
    else:
        await event.respond("**Usage:** `/tracks audio 0,1` or `/tracks sub 0`")


# ═══════════════════════════════════════════
# /watermark — Set text/image watermark
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]watermark"))
async def watermark_command(event):
    """Set or remove watermark.

    Usage:
      /watermark <text> — Set text watermark
      /watermark off — Remove watermark
    Reply to an image with /watermark to set image watermark.
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    reply = await event.get_reply_message()
    parts = event.raw_text.split(None, 1)

    # Reply to image = set image watermark
    if reply and reply.photo:
        status_msg = await event.respond("**Saving watermark image...**")
        try:
            wm_dir = "watermarks_user"
            os.makedirs(wm_dir, exist_ok=True)
            wm_path = os.path.join(wm_dir, f"wm_{user_id}.png")
            await bot.download_media(reply.photo, file=wm_path)
            await update_user_field(user_id, "watermark_image", wm_path)
            await update_user_field(user_id, "watermark_text", "")
            await status_msg.edit("**Image watermark saved!** It will overlay on your encoded videos.")
        except Exception as e:
            await status_msg.edit(f"**Error:** `{e}`")
        return

    if len(parts) < 2:
        current_text = await get_user_field(user_id, "watermark_text", "")
        current_img = await get_user_field(user_id, "watermark_image", "")
        status = "text" if current_text else ("image" if current_img else "none")
        text = (
            "**🔖 Watermark Settings**\n\n"
            f"**Type:** `{status}`\n"
            f"**Text:** `{current_text or 'none'}`\n"
            f"**Image:** `{'set' if current_img else 'none'}`\n\n"
            "**Commands:**\n"
            "`/watermark <text>` — Text watermark\n"
            "`/watermark off` — Remove all\n"
            "Reply to image with `/watermark` — Image watermark"
        )
        await event.respond(text)
        return

    wm_text = parts[1].strip()
    if wm_text.lower() == "off":
        await update_user_field(user_id, "watermark_text", "")
        await update_user_field(user_id, "watermark_image", "")
        await event.respond("**Watermark removed.**")
    else:
        await update_user_field(user_id, "watermark_text", wm_text)
        await update_user_field(user_id, "watermark_image", "")
        await event.respond(f"**Text watermark set:** `{wm_text}`")


# ═══════════════════════════════════════════
# /schedule — Scheduled encoding
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]schedule"))
async def schedule_command(event):
    """Set encoding schedule.

    Usage:
      /schedule off-peak — Encode only during 00:00-08:00 UTC
      /schedule night — Encode only during 20:00-06:00 UTC
      /schedule 02:00-10:00 — Custom UTC window
      /schedule off — Encode immediately (default)
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    parts = event.raw_text.split(None, 1)
    if len(parts) < 2:
        current = await get_user_field(user_id, "schedule", "")
        await event.respond(
            "**⏰ Encoding Schedule**\n\n"
            f"**Current:** `{current or 'immediate (no schedule)'}`\n\n"
            "**Options:**\n"
            "`/schedule off-peak` — 00:00-08:00 UTC\n"
            "`/schedule night` — 20:00-06:00 UTC\n"
            "`/schedule HH:MM-HH:MM` — Custom UTC window\n"
            "`/schedule off` — Encode immediately"
        )
        return

    value = parts[1].strip().lower()
    if value == "off":
        await update_user_field(user_id, "schedule", "")
        await event.respond("**Schedule disabled.** Videos will encode immediately.")
    elif value in ("off-peak", "night") or "-" in value:
        await update_user_field(user_id, "schedule", value)
        await event.respond(f"**Schedule set:** `{value}`")
    else:
        await event.respond("**Invalid schedule.** Use `off-peak`, `night`, `HH:MM-HH:MM`, or `off`.")


# ═══════════════════════════════════════════
# /history — Encoding history
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]history"))
async def history_command(event):
    """Show recent encoding history."""
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    records = await get_history(user_id, limit=10)
    if not records:
        await event.respond("**No encoding history found.**")
        return

    text = "**📜 Recent Encodes (last 10)**\n\n"
    for i, rec in enumerate(records, 1):
        orig = humanbytes(rec.get("original_size", 0))
        enc = humanbytes(rec.get("encoded_size", 0))
        name = rec.get("filename", "?")
        res = rec.get("resolution", "?")
        dur = rec.get("duration_secs", 0)
        ts = rec.get("timestamp", "?")[:10]
        text += f"`{i}.` **{name[:30]}** — {res}\n"
        text += f"    {orig} → {enc} | {int(dur)}s | {ts}\n"

    await event.respond(text)


# ═══════════════════════════════════════════
# /autodelete — Toggle auto-delete originals
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]autodelete"))
async def autodelete_command(event):
    """Toggle auto-delete of original video after encoding."""
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    current = await get_user_field(user_id, "auto_delete", False)
    new_value = not current
    await update_user_field(user_id, "auto_delete", new_value)
    status = "enabled" if new_value else "disabled"
    await event.respond(f"**Auto-delete original messages:** `{status}`")


# ═══════════════════════════════════════════
# /hwaccel — Hardware acceleration toggle
# ═══════════════════════════════════════════

@bot.on(events.NewMessage(pattern=r"^[/!]hwaccel"))
async def hwaccel_command(event):
    """Set hardware acceleration mode.

    Usage: /hwaccel <auto|nvenc|vaapi|none>
    """
    user_id = event.sender_id
    if not await check_user_mdb(user_id):
        return

    parts = event.raw_text.split()
    valid_modes = ("auto", "nvenc", "vaapi", "none")

    if len(parts) < 2:
        current = await get_user_field(user_id, "hw_accel", "auto")
        await event.respond(
            "**🖥️ Hardware Acceleration**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**Options:** `{'`, `'.join(valid_modes)}`\n"
            "**Usage:** `/hwaccel nvenc`"
        )
        return

    mode = parts[1].lower()
    if mode not in valid_modes:
        await event.respond(f"**Invalid mode.** Choose from: `{'`, `'.join(valid_modes)}`")
        return

    await update_user_field(user_id, "hw_accel", mode)
    await event.respond(f"**Hardware acceleration set to:** `{mode}`")
