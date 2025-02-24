import os
import asyncio
from Bot import OWNER_ID, encoder, create_ubot
from pyrogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB

# Fetch bot token from environment variables
bot_token = os.getenv("bot_token")

if not bot_token:
    print("Error: Bot token not found in environment variables.")
    exit(1)

# Start encoder
encoder.start()

# Create ubot
success = create_ubot()
if success is not None:
    ubot = success
    ubot.start()

# Send startup message to OWNER_ID
try:
    encoder.send_message(OWNER_ID, text='Bot Started', reply_markup=IKM([[IKB('ʜᴇʟᴘ', 'answer_help'), IKB('ᴅᴇᴠᴇʟᴏᴘᴇʀ', 'answer_about_dev')]]))
except Exception as e:
    print(f"Error sending startup message: {e}")

# Start event loop
loop = asyncio.get_event_loop()
loop.run_forever()
