import time
import math
import asyncio

from Bot import LOG

PROGRESS_TEMPLATE = """
• {current} of {total}
• Speed: {speed}
• ETA: {eta}
"""


def humanbytes(size) -> str:
    if not size:
        return "0 B"
    power = 1024
    n = 0
    units = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}B"


def time_formatter(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return ", ".join(parts) or "0s"


async def progress_callback(current: int, total: int, event, status_msg, start_time: float, ud_type: str):
    """Telethon-compatible upload/download progress callback."""
    now = time.time()
    diff = now - start_time

    if diff == 0:
        return

    # Only update every ~8 seconds to avoid flood
    if round(diff % 8.0) != 0 and current != total:
        return

    percentage = current * 100 / total
    speed = current / diff
    time_to_completion = round((total - current) / speed) if speed > 0 else 0

    filled = math.floor(percentage / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)

    text = (
        f"{ud_type}\n"
        f"[{progress_bar}]\n"
        + PROGRESS_TEMPLATE.format(
            current=humanbytes(current),
            total=humanbytes(total),
            speed=humanbytes(speed) + "/s",
            eta=time_formatter(time_to_completion) if time_to_completion else "Calculating",
        )
    )

    try:
        await status_msg.edit(text)
    except Exception as e:
        LOG.warning(f"Progress edit error: {e}")

    if current != total:
        await asyncio.sleep(1)
