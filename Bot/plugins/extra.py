import os
import sys

from telethon import events, Button

from Bot import bot, OWNER_ID


@bot.on(events.NewMessage(pattern=r"^[/!]restart$", from_users=OWNER_ID))
async def restart_bot(event):
    await event.reply(
        "**Restarting...**",
        buttons=[[Button.url("Dev", "https://t.me/sohailkhan_indianime")]],
    )
    os.execl(sys.executable, sys.executable, "-m", "Bot")