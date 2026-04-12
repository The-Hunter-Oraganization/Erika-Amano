from telethon import events, Button

from Bot import bot, OWNER_ID, LOG
from Bot.utils.user_info import get_users, user_check_template


@bot.on(events.NewMessage(pattern=r"^[/!]info"))
async def info_check(event):
    target_id = None

    # Check if replying to someone
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id:
            target_id = reply_msg.sender_id

    # Check if argument provided
    if target_id is None:
        args = event.raw_text.split(None, 1)
        if len(args) > 1:
            arg = args[1].strip().lstrip("@")
            if arg.isdigit():
                target_id = int(arg)
            else:
                # Try to resolve username
                try:
                    entity = await bot.get_entity(arg)
                    target_id = entity.id
                except Exception:
                    await event.reply("**User not found.**")
                    return

    if target_id is None:
        await event.reply("**Usage:** `/info <user_id or @username>` or reply to a message.")
        return

    try:
        user_info = await get_users(target_id)
        if user_info is None:
            await event.reply("**User not found.**")
            return

        text = await user_check_template(user_info[0], user_info[1], user_info[2], user_info[3], user_info[4], user_info[6])

        buttons = [
            [
                Button.inline("ᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_auth-{user_info[6]}".encode()),
                Button.inline("ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ", f"users_unauth-{user_info[6]}".encode()),
            ],
            [Button.inline("ʀᴇǫᴜᴇsᴛ", f"users_request-{user_info[6]}".encode())],
        ]

        caption = "`-------`**ᴜsᴇʀ**`-------`\n\n" + text

        if user_info[5]:
            photo_path = await bot.download_media(user_info[5], file=f"downloads/user_{target_id}.jpg")
            await event.respond(caption, file=photo_path, buttons=buttons)
        else:
            await event.respond(caption, buttons=buttons)

    except Exception as e:
        LOG.warning(f"Error fetching user info: {e}")
        await event.reply(f"**Error:** `{e}`")