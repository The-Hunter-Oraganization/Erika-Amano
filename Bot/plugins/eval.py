import io
import sys
import os
import re
import traceback
import subprocess
import asyncio

from telethon import events

from Bot import bot, OWNER_ID, LOG


# ─── /eval - Execute Python code ───

@bot.on(events.NewMessage(pattern=r"^[/!]eval\s+", from_users=OWNER_ID))
async def eval_handler(event):
    cmd = event.raw_text.split(None, 1)[1]
    status_msg = await event.reply("**Processing...**")

    reply_to = event.reply_to_msg_id or event.id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()

    stdout, stderr, exc = None, None, None
    try:
        await _aexec(cmd, bot, event)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = exc or stderr or stdout or "Success"

    final_output = f"**EVAL:** `{cmd}`\n\n**OUTPUT:**\n`{evaluation.strip()}`"

    if len(final_output) > 4096:
        with io.BytesIO(final_output.encode()) as out_file:
            out_file.name = "eval.txt"
            await bot.send_file(
                event.chat_id,
                out_file,
                caption=f"`{cmd[:100]}`",
                reply_to=reply_to,
            )
    else:
        await event.respond(final_output, reply_to=reply_to)

    await status_msg.delete()


async def _aexec(code, client, event):
    exec(
        "async def __aexec(client, event): "
        + "".join(f"\n {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](client, event)


# ─── /term - Execute shell commands ───

@bot.on(events.NewMessage(pattern=r"^[/!]term\s+", from_users=OWNER_ID))
async def terminal_handler(event):
    cmd_text = event.raw_text.split(None, 1)
    if len(cmd_text) < 2:
        await event.reply("**Usage:** `/term echo hello`")
        return

    command = cmd_text[1]

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        output = stdout.decode("utf-8", errors="replace").strip()
        error = stderr.decode("utf-8", errors="replace").strip()

        result = ""
        if output:
            result += f"**stdout:**\n```\n{output}\n```\n"
        if error:
            result += f"**stderr:**\n```\n{error}\n```\n"
        if not result:
            result = "**No output.**"

    except asyncio.TimeoutError:
        result = "**Error:** Command timed out (120s)."
    except Exception as e:
        result = f"**Error:**\n```\n{traceback.format_exc()}\n```"

    if len(result) > 4096:
        filename = "output.txt"
        with open(filename, "w") as f:
            f.write(result)
        await bot.send_file(event.chat_id, filename, reply_to=event.id, caption="`Output`")
        os.remove(filename)
    else:
        await event.respond(result)