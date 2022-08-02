from Bot import OWNER_ID, encoder
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
import asyncio

encoder.start()


try:
    encoder.send_message(OWNER_ID, text='Bot Started', reply_markup=IKM([[IKB('ᴄʜᴇᴄᴋ sᴛᴀᴛs', 'answer_help'), IKB('ᴅᴇᴠᴇʟᴏᴘᴇʀ', 'answer_about_dev')]]))
except:
    pass    

loop = asyncio.get_event_loop()
loop.run_forever()