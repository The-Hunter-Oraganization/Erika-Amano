import random
import os

from telethon import events, Button

from Bot import bot, OWNER_ID, TRIGGERS, LOG
from Bot.plugins.database.mongo_db import (
    check_user_mdb,
    check_crf_mdb,
    check_resolution_settings,
    check_preset_settings,
    check_vcodec_settings,
    check_audio_type_mdb,
    get_user_settings,
    get_user_field,
    update_user_field,
    update_resolution_settings,
    update_preset_settings,
    update_vcodec_settings,
    update_audio_type_mdb,
    update_crf,
    authorize_user,
    unauthorize_user,
)
from Bot.utils.user_info import get_users, user_check_template


async def _send_user_notification(target_id, title, text, buttons):
    """Send a user notification with photo cleanup."""
    user_info = await get_users(target_id)
    if user_info is None:
        return None

    full_text = await user_check_template(user_info[0], user_info[1], user_info[2], user_info[3], user_info[4], user_info[6])
    caption = f"`-------`**{title}**`-------`\n\n" + full_text
    photo_path = None

    try:
        if user_info[5]:
            photo_path = await bot.download_media(user_info[5], file=f"downloads/user_{target_id}.jpg")
            notify = await bot.send_file(OWNER_ID, photo_path, caption=caption, buttons=buttons)
        else:
            notify = await bot.send_message(OWNER_ID, caption, buttons=buttons)
    except Exception:
        notify = await bot.send_message(OWNER_ID, caption, buttons=buttons)
    finally:
        # Clean up downloaded photo
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except Exception:
                pass

    return notify, user_info

# ─── Button Layouts ───

BUTTONS_RESOLUTIONS = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [
        Button.inline("sᴇᴛ 𝟺𝟾𝟶ᴘ", b"settings_encoding_480p"),
        Button.inline("sᴇᴛ 𝟽𝟸𝟶ᴘ", b"settings_encoding_720p"),
        Button.inline("ѕєт 1080ρ", b"settings_encoding_1080p"),
    ],
]

BUTTONS_CRF = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [Button.inline("ᴄʀғ + 𝟷", b"settings_crf_plus"), Button.inline("ᴄʀғ - 𝟷", b"settings_crf_minus")],
]

BUTTONS_AUDIO = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [
        Button.inline("sᴇᴛ ᴀᴀᴄ", b"settings_encoding_aac"),
        Button.inline("ѕєт ᴏᴘᴜs", b"settings_encoding_opus"),
        Button.inline("sᴇᴛ ʟɪʙᴏᴘᴜs", b"settings_encoding_libopus"),
    ],
]

BUTTONS_PRESET = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [Button.inline("sᴇᴛ ғᴀsᴛ", b"settings_encoding_fast"), Button.inline("ѕєт sʟᴏᴡ", b"settings_encoding_slow")],
]

BUTTONS_VCODEC = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [Button.inline("sᴇᴛ x𝟸𝟼𝟺", b"settings_encoding_x264"), Button.inline("ѕєт x𝟸𝟼𝟻", b"settings_encoding_x265")],
]

BUTTONS_DEV = [
    [Button.url("ᴅᴇᴠᴇʟᴏᴘᴇʀ", "https://t.me/sohailkhan_indianime"), Button.url("ɢɪᴛʜᴜʙ", "https://github.com/soheru")],
    [Button.url("ᴡᴇʙsɪᴛᴇ", "https://teamyokai.tech"), Button.url("ᴄʜᴀɴɴᴇʟ", "https://t.me/aboutmesk")],
    [Button.url("ɪɴsᴛᴀɢʀᴀᴍ", "https://instagram.com/_soheru"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
]

BUTTONS_HELP = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev")],
    [
        Button.inline("ʀᴇsᴏʟᴜᴛɪᴏɴ", b"answer_resolution"),
        Button.inline("ᴀᴜᴅɪᴏ", b"answer_audio"),
        Button.inline("ᴄʀғ", b"answer_crf"),
    ],
    [Button.inline("ᴠᴄᴏᴅᴇᴄ", b"answer_vcodec"), Button.inline("ᴘʀᴇsᴇᴛ", b"answer_preset")],
    [Button.inline("ʜᴡ ᴀᴄᴄᴇʟ", b"answer_hwaccel"), Button.inline("ᴡᴀᴛᴇʀᴍᴀʀᴋ", b"answer_watermark")],
    [Button.inline("ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ", b"settings_autodelete_toggle"), Button.inline("ʀᴇɴᴀᴍᴇ", b"answer_rename")],
    [Button.inline("sᴄʜᴇᴅᴜʟᴇ", b"answer_schedule"), Button.inline("ᴛʀᴀᴄᴋs", b"answer_track_info")],
]

BUTTONS_HWACCEL = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [
        Button.inline("ᴀᴜᴛᴏ", b"settings_hwaccel_auto"),
        Button.inline("ɴᴠᴇɴᴄ", b"settings_hwaccel_nvenc"),
        Button.inline("ᴠᴀᴀᴘɪ", b"settings_hwaccel_vaapi"),
        Button.inline("ɴᴏɴᴇ", b"settings_hwaccel_none"),
    ],
]

BUTTONS_SCHEDULE = [
    [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    [
        Button.inline("ᴏғғ-ᴘᴇᴀᴋ", b"settings_schedule_off-peak"),
        Button.inline("ɴɪɢʜᴛ", b"settings_schedule_night"),
        Button.inline("ɪᴍᴍᴇᴅɪᴀᴛᴇ", b"settings_schedule_off"),
    ],
]


# ─── User Authorization Callbacks ───

@bot.on(events.CallbackQuery(pattern=rb"users_"))
async def callback_authorize(event):
    data = event.data.decode("utf-8")
    sender_id = event.sender_id

    if "unauth" in data:
        if sender_id != OWNER_ID:
            await event.answer("You're not authorized to do this.")
            return

        target_id = int(data.split("-")[1])
        await unauthorize_user(target_id)

        buttons = [
            [Button.inline("ᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_auth-{target_id}".encode()), Button.inline("ʜᴇʟᴘ", b"answer_help")],
        ]

        result = await _send_user_notification(target_id, "ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ", "", buttons)
        if result is None:
            await event.answer("User not found.")
            return

        notify, _ = result
        try:
            await bot.forward_messages(target_id, notify)
        except Exception:
            pass

    elif "auth" in data:
        if sender_id != OWNER_ID:
            await event.answer("You're not authorized to do this.")
            return

        target_id = int(data.split("-")[1])
        await authorize_user(target_id)

        buttons = [
            [Button.inline("ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_unauth-{target_id}".encode()), Button.inline("ʜᴇʟᴘ", b"answer_help")],
        ]

        result = await _send_user_notification(target_id, "ᴀᴜᴛʜᴏʀɪᴢᴇᴅ", "", buttons)
        if result is None:
            await event.answer("User not found.")
            return

        notify, _ = result
        try:
            await bot.forward_messages(target_id, notify)
        except Exception:
            pass

    elif "request" in data:
        target_id = int(data.split("-")[1])
        buttons = [
            [
                Button.inline("ᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_auth-{target_id}".encode()),
                Button.inline("ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_unauth-{target_id}".encode()),
            ],
        ]

        result = await _send_user_notification(target_id, "ʀᴇǫᴜᴇsᴛᴇᴅ ᴀᴜᴛʜᴏʀɪᴢᴇ", "", buttons)
        if result is None:
            await event.answer("User not found.")
            return

    await event.answer("Done")


# ─── Settings Callbacks ───

@bot.on(events.CallbackQuery(pattern=rb"settings_"))
async def settings_callback(event):
    data = event.data.decode("utf-8")
    user_id = event.sender_id

    check = await check_user_mdb(user_id)
    if check is None:
        await event.edit(
            "You're not authorized to use this bot. Request Admins to approve you.",
            buttons=[[Button.inline("ʀᴇǫᴜᴇsᴛ", f"users_request-{user_id}".encode())]],
        )
        return

    settings_map = {
        "encoding_480p": ("resolution", "480p", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ʀᴇsᴏʟᴜᴛɪᴏɴ ᴛᴏ 480p", BUTTONS_RESOLUTIONS),
        "encoding_720p": ("resolution", "720p", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ʀᴇsᴏʟᴜᴛɪᴏɴ ᴛᴏ 720p", BUTTONS_RESOLUTIONS),
        "encoding_1080p": ("resolution", "1080p", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ʀᴇsᴏʟᴜᴛɪᴏɴ ᴛᴏ 1080p", BUTTONS_RESOLUTIONS),
        "encoding_aac": ("audio", "aac", "ᴜᴘᴅᴀᴛᴇᴅ ᴀᴜᴅɪᴏ ᴛʏᴘᴇ ᴛᴏ ᴀᴀᴄ", BUTTONS_AUDIO),
        "encoding_opus": ("audio", "opus", "ᴜᴘᴅᴀᴛᴇᴅ ᴀᴜᴅɪᴏ ᴛʏᴘᴇ ᴛᴏ ᴏᴘᴜs", BUTTONS_AUDIO),
        "encoding_libopus": ("audio", "libopus", "ᴜᴘᴅᴀᴛᴇᴅ ᴀᴜᴅɪᴏ ᴛʏᴘᴇ ᴛᴏ ʟɪʙᴏᴘᴜs", BUTTONS_AUDIO),
        "encoding_x264": ("vcodec", "x264", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴄᴏᴅᴇᴄ ᴛᴏ x264", BUTTONS_VCODEC),
        "encoding_x265": ("vcodec", "x265", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴄᴏᴅᴇᴄ ᴛᴏ x265", BUTTONS_VCODEC),
        "encoding_fast": ("preset", "fast", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴘʀᴇsᴇᴛ ᴛᴏ ғᴀsᴛ", BUTTONS_PRESET),
        "encoding_slow": ("preset", "slow", "ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴘʀᴇsᴇᴛ ᴛᴏ sʟᴏᴡ", BUTTONS_PRESET),
    }

    # Check simple settings updates
    for key, (setting_type, value, msg_text, buttons) in settings_map.items():
        if key in data:
            updater = {
                "resolution": update_resolution_settings,
                "audio": update_audio_type_mdb,
                "vcodec": update_vcodec_settings,
                "preset": update_preset_settings,
            }[setting_type]
            await updater(user_id, value)
            await event.edit(msg_text, buttons=buttons)
            return

    # CRF adjustments
    if "crf_plus" in data:
        current_crf = await check_crf_mdb(user_id) or 26
        new_crf = min(current_crf + 1, 51)
        await update_crf(user_id, new_crf)
        await event.edit(f"ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴄʀғ ᴛᴏ {new_crf}", buttons=BUTTONS_CRF)

    elif "crf_minus" in data:
        current_crf = await check_crf_mdb(user_id) or 26
        new_crf = max(current_crf - 1, 0)
        await update_crf(user_id, new_crf)
        await event.edit(f"ᴜᴘᴅᴀᴛᴇᴅ ᴠɪᴅᴇᴏ ᴄʀғ ᴛᴏ {new_crf}", buttons=BUTTONS_CRF)

    # HW acceleration
    elif "hwaccel_" in data:
        mode = data.split("hwaccel_")[1]
        await update_user_field(user_id, "hw_accel", mode)
        await event.edit(f"ᴜᴘᴅᴀᴛᴇᴅ ʜᴡ ᴀᴄᴄᴇʟᴇʀᴀᴛɪᴏɴ ᴛᴏ `{mode}`", buttons=BUTTONS_HWACCEL)

    # Schedule
    elif "schedule_" in data:
        value = data.split("schedule_")[1]
        if value == "off":
            await update_user_field(user_id, "schedule", "")
            await event.edit("sᴄʜᴇᴅᴜʟᴇ ᴅɪsᴀʙʟᴇᴅ — ᴇɴᴄᴏᴅɪɴɢ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ", buttons=BUTTONS_SCHEDULE)
        else:
            await update_user_field(user_id, "schedule", value)
            await event.edit(f"ᴜᴘᴅᴀᴛᴇᴅ sᴄʜᴇᴅᴜʟᴇ ᴛᴏ `{value}`", buttons=BUTTONS_SCHEDULE)

    # Auto-delete toggle
    elif "autodelete_toggle" in data:
        current = await get_user_field(user_id, "auto_delete", False)
        new_val = not current
        await update_user_field(user_id, "auto_delete", new_val)
        status = "ᴏɴ" if new_val else "ᴏғғ"
        await event.edit(f"ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴏʀɪɢɪɴᴀʟs: `{status}`", buttons=BUTTONS_HELP)


# ─── Answer / Help Callbacks ───

@bot.on(events.CallbackQuery(pattern=rb"answer_"))
async def callback_answer(event):
    data = event.data.decode("utf-8")
    user_id = event.sender_id

    check = await check_user_mdb(user_id)
    if check is None:
        await event.edit(
            "You're not authorized to use this bot. Request Admins to approve you.",
            buttons=[[Button.inline("ʀᴇǫᴜᴇsᴛ", f"users_request-{user_id}".encode())]],
        )
        return

    sender = await event.get_sender()
    first_name = getattr(sender, "first_name", "User")

    if "help" in data:
        text = (
            f"**Hi There** `{first_name}`,\n\n"
            "I am a video encoder bot, which reduces the size of the video "
            "and gives it in good quality.\n\n"
            "To see all my features, click the buttons below"
        )
        await event.edit(text, buttons=BUTTONS_HELP)

    elif "crf" in data:
        crf_val = await check_crf_mdb(user_id)
        text = "**To change the video CRF, use the buttons below**.\n\n"
        text += f"**Your current CRF:** `{crf_val}`"
        await event.edit(text, buttons=BUTTONS_CRF)

    elif "resolution" in data:
        res_val = await check_resolution_settings(user_id)
        text = "**To change the video resolution, use the buttons below**.\n\n"
        text += f"**Your current resolution:** `{res_val}`"
        await event.edit(text, buttons=BUTTONS_RESOLUTIONS)

    elif "audio" in data:
        audio_val = await check_audio_type_mdb(user_id)
        text = "**To change the audio type, use the buttons below**.\n\n"
        text += f"**Your current audio type:** `{audio_val}`"
        await event.edit(text, buttons=BUTTONS_AUDIO)

    elif "vcodec" in data:
        vcodec_val = await check_vcodec_settings(user_id)
        text = "**To change the video codec, use the buttons below**.\n\n"
        text += f"**Your current video codec:** `{vcodec_val}`"
        await event.edit(text, buttons=BUTTONS_VCODEC)

    elif "preset" in data:
        preset_val = await check_preset_settings(user_id)
        text = "**To change the video preset, use the buttons below**.\n\n"
        text += f"**Your current preset:** `{preset_val}`"
        await event.edit(text, buttons=BUTTONS_PRESET)

    elif "about_dev" in data:
        text = f"Hello `{first_name}`,\n\nI'm Sohail\nTo connect with me, check the buttons below."
        await event.edit(text, buttons=BUTTONS_DEV)

    elif "hwaccel" in data:
        hw_val = await get_user_field(user_id, "hw_accel", "auto")
        text = "**To change hardware acceleration, use the buttons below**.\n\n"
        text += f"**Your current mode:** `{hw_val}`"
        await event.edit(text, buttons=BUTTONS_HWACCEL)

    elif "watermark" in data:
        wm_text = await get_user_field(user_id, "watermark_text", "")
        wm_img = await get_user_field(user_id, "watermark_image", "")
        status = wm_text if wm_text else ("image set" if wm_img else "none")
        text = (
            "**🔖 Watermark Settings**\n\n"
            f"**Current:** `{status}`\n\n"
            "Use `/watermark <text>` to set text watermark\n"
            "Reply to an image with `/watermark` for image watermark\n"
            "`/watermark off` to remove"
        )
        await event.edit(text, buttons=BUTTONS_HELP)

    elif "rename" in data:
        rename_val = await get_user_field(user_id, "rename_pattern", "")
        text = (
            "**📝 Rename Pattern**\n\n"
            f"**Current:** `{rename_val or 'disabled'}`\n\n"
            "Use `/rename [Erika] {title} [{res}].{ext}` to set\n"
            "**Placeholders:** `{title}`, `{res}`, `{codec}`, `{ext}`\n"
            "`/rename off` to disable"
        )
        await event.edit(text, buttons=BUTTONS_HELP)

    elif "schedule" in data:
        sched_val = await get_user_field(user_id, "schedule", "")
        text = "**To change encoding schedule, use the buttons below**.\n\n"
        text += f"**Your current schedule:** `{sched_val or 'immediate'}`"
        await event.edit(text, buttons=BUTTONS_SCHEDULE)

    elif "track_info" in data:
        audio_t = await get_user_field(user_id, "audio_tracks", "")
        sub_t = await get_user_field(user_id, "subtitle_tracks", "")
        text = (
            "**🎵 Track Selection**\n\n"
            f"**Audio tracks:** `{audio_t or 'all'}`\n"
            f"**Subtitle tracks:** `{sub_t or 'all'}`\n\n"
            "Use `/tracks audio 0,1` to select audio tracks\n"
            "Use `/tracks sub 0` to select subtitle tracks\n"
            "Reply to a video with `/tracks` to see available streams"
        )
        await event.edit(text, buttons=BUTTONS_HELP)

    await event.answer("Done")


# ─── Blank Callback ───

@bot.on(events.CallbackQuery(pattern=rb"blankquery"))
async def blank_callback(event):
    await event.answer("Nothing here!")


# ─── /start and /help Commands ───

@bot.on(events.NewMessage(pattern=r"^[/!](start|help)$"))
async def start_command(event):
    user_id = event.sender_id
    sender = await event.get_sender()
    first_name = getattr(sender, "first_name", "User")

    buttons = [
        [Button.inline("ᴅᴇᴠᴇʟᴏᴘᴇʀ", b"answer_about_dev"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
    ]

    caption = (
        f"**Hi There** `{first_name}`,\n\n"
        "I am a video encoder bot, which reduces the size of the video "
        "and gives it in good quality.\n"
        "To see all my features, click the buttons below"
    )

    # Try to send a random wallpaper
    wallpaper_dir = "./wallpapers"
    try:
        images = os.listdir(wallpaper_dir)
        if images:
            chosen = os.path.join(wallpaper_dir, random.choice(images))
            await event.respond(caption, file=chosen, buttons=buttons)
            return
    except Exception:
        pass

    await event.respond(caption, buttons=buttons)


# ─── /settings Command ───

BUTTONS_SETTINGS = [
    [Button.inline("ʀᴇsᴏʟᴜᴛɪᴏɴ", b"answer_resolution"), Button.inline("ᴄʀғ", b"answer_crf")],
    [Button.inline("ᴀᴜᴅɪᴏ", b"answer_audio"), Button.inline("ᴘʀᴇsᴇᴛ", b"answer_preset")],
    [Button.inline("ᴠᴄᴏᴅᴇᴄ", b"answer_vcodec"), Button.inline("ʜᴡ ᴀᴄᴄᴇʟ", b"answer_hwaccel")],
    [Button.inline("ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ", b"settings_autodelete_toggle"), Button.inline("sᴄʜᴇᴅᴜʟᴇ", b"answer_schedule")],
    [Button.inline("ᴡᴀᴛᴇʀᴍᴀʀᴋ", b"answer_watermark"), Button.inline("ᴛʀᴀᴄᴋs", b"answer_track_info")],
    [Button.inline("ʀᴇɴᴀᴍᴇ", b"answer_rename"), Button.inline("ʜᴇʟᴘ", b"answer_help")],
]


@bot.on(events.NewMessage(pattern=r"^[/!]settings$"))
async def settings_command(event):
    """Show all current encoding settings at a glance."""
    user_id = event.sender_id
    doc = await get_user_settings(user_id)

    if doc is None:
        await event.respond(
            "You're not authorized to use this bot.",
            buttons=[[Button.inline("ʀᴇǫᴜᴇsᴛ", f"users_request-{user_id}".encode())]],
        )
        return

    hw_accel = doc.get("hw_accel", "auto")
    rename_p = doc.get("rename_pattern", "")
    auto_del = "On" if doc.get("auto_delete", False) else "Off"
    schedule = doc.get("schedule", "") or "immediate"
    wm_text = doc.get("watermark_text", "")
    wm_img = doc.get("watermark_image", "")
    wm_status = wm_text if wm_text else ("image" if wm_img else "none")
    audio_t = doc.get("audio_tracks", "") or "all"
    sub_t = doc.get("subtitle_tracks", "") or "all"

    text = (
        "**⚙️ Your Encoding Settings**\n\n"
        f"**Resolution:** `{doc.get('resolution', '480p')}`\n"
        f"**CRF:** `{doc.get('crf', 26)}`\n"
        f"**Preset:** `{doc.get('preset', 'fast')}`\n"
        f"**Video Codec:** `{doc.get('vcodec', 'x264')}`\n"
        f"**Audio Type:** `{doc.get('audio_type', 'aac')}`\n"
        f"**HW Accel:** `{hw_accel}`\n\n"
        f"**Rename:** `{rename_p or 'disabled'}`\n"
        f"**Auto-Delete:** `{auto_del}`\n"
        f"**Schedule:** `{schedule}`\n"
        f"**Watermark:** `{wm_status}`\n"
        f"**Audio Tracks:** `{audio_t}`\n"
        f"**Subtitle Tracks:** `{sub_t}`\n\n"
        "Use the buttons below to change settings:"
    )
    await event.respond(text, buttons=BUTTONS_SETTINGS)
