from Bot import OWNER_ID, encoder, create_ubot
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB
import asyncio

encoder.start()

success = create_ubot()
if success != None:
    ubot = success
    ubot.start()

try:
    encoder.send_message(OWNER_ID, text='Bot Started', reply_markup=IKM([[IKB('ʜᴇʟᴘ', 'answer_help'), IKB('ᴅᴇᴠᴇʟᴏᴘᴇʀ', 'answer_about_dev')]]))
except:
    pass    

loop = asyncio.get_event_loop()
loop.run_forever()
