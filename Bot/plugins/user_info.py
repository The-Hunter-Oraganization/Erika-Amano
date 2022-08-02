from pyrogram import Client, filters  
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from Bot import TRIGGERS, OWNER_ID, LOG
from Bot.utils.user_info import get_users, user_check_template


@Client.on_message(filters.command('info', prefixes=TRIGGERS))
async def info_check(client: Client, msg: Message):
    if msg.reply_to_message:
        reply = msg.reply_to_message
        user_id = reply.from_user.id   
        try:
            get_u = await get_users(user_id)
            pic_user = await client.download_media(get_u[5], file_name=f"downloads/user.png")
            TEXTS = await user_check_template(get_u[0],get_u[1],get_u[2],get_u[3],get_u[4],get_u[6])
            try:
                await msg.reply_photo(pic_user, caption="`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS,  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))
            except:
                await msg.reply_photo('https://telegra.ph/file/3784551858cfbe6f4152e.jpg',"`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))  
        except Exception as e:
            LOG.info(f'Error While Fetching User Info From Telegram Server\n{e}')  
            
    user_id = msg.command[1]
    if user_id.isdigit():
        try:
            get_u = await get_users(user_id)
            pic_user = await client.download_media(get_u[5], file_name=f"user.png")
            TEXTS = await user_check_template(get_u[0],get_u[1],get_u[2],get_u[3],get_u[4],get_u[6])
            try:
                await msg.reply_photo(pic_user, caption="`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS,  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))
            except:
                await msg.reply_photo('https://telegra.ph/file/3784551858cfbe6f4152e.jpg',"`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS,  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))  
        except Exception as e:
            LOG.info(f'Error While Fetching User Info From Telegram Server\n{e}')  
    else:   
        try:
            get_usersd = await client.get_users(msg.command[1])
        except BaseException:
            return await msg.reply("User Not Found")
        user_id = get_usersd.id
        try:
            get_u = await get_users(user_id)
            pic_user = await client.download_media(get_u[5], file_name=f"user.png")
            TEXTS = await user_check_template(get_u[0],get_u[1],get_u[2],get_u[3],get_u[4],get_u[6])
            try:
                await msg.reply_photo(pic_user, caption="`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS,  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))
            except:
                await msg.reply_photo('https://telegra.ph/file/3784551858cfbe6f4152e.jpg',"`-------`**ᴜsᴇʀ**`-------`\n\n"+ TEXTS,  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('ᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_auth-{get_u[6]}'), InlineKeyboardButton('ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ',f'users_unauth-{get_u[6]}')], [InlineKeyboardButton('ʀᴇǫᴜᴇsᴛ', f'users_request-{get_u[6]}')]]))  
        except Exception as e:
            LOG.info(f'Error While Fetching User Info From Telegram Server\n{e}')  