from Bot import bot, LOG


async def get_users(user_id):
    """Fetch user info from Telegram. Returns (username, first_name, last_name, dc_id, status, photo, id)."""
    try:
        user = await bot.get_entity(int(user_id))

        username = user.username or "None"
        user_id_val = user.id
        first_name = user.first_name or "None"
        last_name = user.last_name or "None"

        # Telethon user objects don't have dc_id directly accessible in all cases
        dc_id = "N/A"
        if hasattr(user, "photo") and user.photo:
            dc_id = getattr(user.photo, "dc_id", "N/A")

        # User status
        status = "None"
        if user.status:
            status_type = type(user.status).__name__
            status = status_type.replace("UserStatus", "")

        # Profile photo
        photo = None
        try:
            photos = await bot.get_profile_photos(user)
            if photos:
                photo = photos[0]
        except Exception:
            pass

        return username, first_name, last_name, dc_id, status, photo, user_id_val
    except Exception as e:
        LOG.warning(f"Error fetching user {user_id}: {e}")
        return None


async def user_check_template(username, first_name, last_name, dc_id, status, user_id=None):
    text = f"**ᴜsᴇʀ's ғɪʀsᴛ ɴᴀᴍᴇ**: `{first_name}`\n"
    text += f"**ᴜsᴇʀ's ʟᴀsᴛ ɴᴀᴍᴇ**: `{last_name}`\n"
    text += f"**ᴜsᴇʀ's ᴜsᴇʀɴᴀᴍᴇ**: @{username}\n"
    text += f"**ᴜsᴇʀ's ɪᴅ**: `{user_id}`\n"
    text += f"**ᴜsᴇʀ's ᴅᴀᴛᴀᴄᴇɴᴛᴇʀ**: `{dc_id}`\n"
    text += f"**ᴜsᴇʀ's sᴛᴀᴛᴜs**: `{status}`\n"
    return text