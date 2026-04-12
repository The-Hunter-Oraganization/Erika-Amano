import time
import math
import os
import re
import asyncio
import subprocess

from telethon import Button

from Bot import LOG


def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    parts = []
    if weeks:
        parts.append(f"{weeks}w")
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return ":".join(parts) or "0s"


def humanbytes(size) -> str:
    if size in [None, "", 0]:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"


def get_total_frames(file_path: str) -> int:
    """Get total frames using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-count_packets",
                "-show_entries", "stream=nb_read_packets",
                "-of", "csv=p=0",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        frames = result.stdout.strip()
        if frames.isdigit():
            return int(frames)
    except Exception as e:
        LOG.warning(f"ffprobe frame count failed: {e}")

    # Fallback: estimate from duration and fps
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=duration,r_frame_rate",
                "-of", "csv=p=0",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        parts = result.stdout.strip().split(",")
        if len(parts) >= 2:
            fps_parts = parts[0].split("/")
            fps = int(fps_parts[0]) / int(fps_parts[1]) if len(fps_parts) == 2 else float(fps_parts[0])
            duration = float(parts[1])
            return int(fps * duration)
    except Exception:
        pass

    return 0


async def ffmpeg_progress(cmd: str, file_path: str, progress_file: str, start_time: float, status_msg, ps_name: str, proc_holder: dict = None):
    """Run FFmpeg and update progress in a Telethon message.
    
    If proc_holder dict is provided, the subprocess is stored under proc_holder["process"]
    so it can be cancelled externally.
    """
    total_frames = get_total_frames(file_path)
    if total_frames == 0:
        total_frames = 1  # prevent division by zero

    # Create empty progress file
    with open(progress_file, "w") as f:
        pass

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    if proc_holder is not None:
        proc_holder["process"] = process

    last_edit_time = 0

    while process.returncode is None:
        await asyncio.sleep(5)

        try:
            with open(progress_file, "r") as f:
                text = f.read()
        except FileNotFoundError:
            await process.wait()
            break

        frames = re.findall(r"frame=(\d+)", text)
        sizes = re.findall(r"total_size=(\d+)", text)

        if not frames:
            if process.returncode is not None:
                break
            continue

        current_frame = int(frames[-1])
        current_size = int(sizes[-1]) if sizes else 0
        time_diff = time.time() - start_time

        if time_diff == 0:
            continue

        speed = current_frame / time_diff
        if speed == 0:
            continue

        percentage = min(current_frame * 100 / total_frames, 100)
        eta_ms = ((total_frames - current_frame) / speed) * 1000

        filled = math.floor(percentage / 5)
        progress_bar = "█" * filled + "░" * (20 - filled)
        size_text = f"{humanbytes(current_size)} of ~{humanbytes((current_size / max(percentage, 0.01)) * 100)}"
        eta_text = time_formatter(eta_ms)

        # Rate-limit edits to once every 8 seconds
        now = time.time()
        if now - last_edit_time < 8:
            continue
        last_edit_time = now

        try:
            await status_msg.edit(
                f"{ps_name}\n\n"
                f"**[{progress_bar}]** `{percentage:.1f}%`\n\n"
                f"**Size:** `{size_text}`\n"
                f"**ETA:** `{eta_text}`\n"
                f"**Speed:** `{speed:.1f} fps`",
            )
        except Exception as e:
            LOG.warning(f"Error editing FFmpeg status: {e}")

        # Check if process ended
        if process.returncode is not None:
            break

    await process.wait()
    return process.returncode


async def generate_sample(input_path: str, duration: int = 30, start_at: str = "00:00:30"):
    """Generate a short sample clip from a video. Returns output path or None."""
    output = input_path.rsplit(".", 1)[0] + f"_sample.mp4"
    cmd = (
        f'ffmpeg -hide_banner -loglevel error '
        f'-ss {start_at} -i "{input_path}" -t {duration} '
        f'-c copy "{output}" -y'
    )
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0 and os.path.exists(output):
            return output
        LOG.warning(f"Sample generation failed: {stderr.decode()}")
    except Exception as e:
        LOG.warning(f"Sample generation error: {e}")
    return None


def get_video_duration(file_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", file_path],
            capture_output=True, text=True, timeout=30,
        )
        val = result.stdout.strip()
        if val:
            return float(val)
    except Exception:
        pass
    return 0.0