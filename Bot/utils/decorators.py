import subprocess

from Bot import LOG, HW_ACCEL
from Bot.plugins.database.mongo_db import (
    check_crf_mdb,
    check_vcodec_settings,
    check_preset_settings,
    check_resolution_settings,
    check_audio_type_mdb,
    get_user_field,
)

# Resolution to FFmpeg scale map
RESOLUTION_MAP = {
    "480p": "640:480",
    "720p": "1280:720",
    "1080p": "1920:1080",
}

# Codec map (software)
VCODEC_MAP = {
    "x264": "libx264",
    "x265": "libx265",
}

# Codec map (nvenc)
NVENC_MAP = {
    "x264": "h264_nvenc",
    "x265": "hevc_nvenc",
}

# Codec map (vaapi)
VAAPI_MAP = {
    "x264": "h264_vaapi",
    "x265": "hevc_vaapi",
}

# Audio bitrate by resolution
AUDIO_BITRATE_MAP = {
    "480p": "64k",
    "720p": "128k",
    "1080p": "256k",
}


def _has_audio_stream(input_path: str) -> bool:
    """Check if input file has an audio stream."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type", "-of", "csv=p=0", input_path],
            capture_output=True, text=True, timeout=30,
        )
        return bool(result.stdout.strip())
    except Exception:
        return True


def _detect_hw_accel() -> str:
    """Detect available hardware acceleration."""
    if HW_ACCEL == "none":
        return "none"
    if HW_ACCEL in ("nvenc", "vaapi"):
        return HW_ACCEL

    # auto-detect
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=10,
        )
        output = result.stdout
        if "h264_nvenc" in output:
            return "nvenc"
        if "h264_vaapi" in output:
            return "vaapi"
    except Exception:
        pass
    return "none"


def _get_stream_info(input_path: str):
    """Get audio and subtitle stream info via ffprobe."""
    info = {"audio_streams": [], "subtitle_streams": []}
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=index,codec_type,codec_name:stream_tags=language,title",
             "-of", "json", input_path],
            capture_output=True, text=True, timeout=30,
        )
        import json
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            tags = stream.get("tags", {})
            entry = {
                "index": stream["index"],
                "codec": stream.get("codec_name", "?"),
                "lang": tags.get("language", "?"),
                "title": tags.get("title", ""),
            }
            if stream["codec_type"] == "audio":
                info["audio_streams"].append(entry)
            elif stream["codec_type"] == "subtitle":
                info["subtitle_streams"].append(entry)
    except Exception as e:
        LOG.warning(f"Failed to get stream info: {e}")
    return info


async def build_ffmpeg_cmd(user_id: int, input_path: str, progress_file: str,
                           trim_start: str = "", trim_end: str = ""):
    """Build the ffmpeg command based on user's DB settings.

    Returns (cmd, output_path).
    """
    resolution_key = await check_resolution_settings(user_id) or "480p"
    audio_type = await check_audio_type_mdb(user_id) or "aac"
    preset = await check_preset_settings(user_id) or "fast"
    vcodec_key = await check_vcodec_settings(user_id) or "x264"
    crf = await check_crf_mdb(user_id)
    if crf is None:
        crf = 26

    # Per-user HW accel override or global
    user_hw = await get_user_field(user_id, "hw_accel", "auto")
    if user_hw == "auto":
        hw = _detect_hw_accel()
    elif user_hw == "none":
        hw = "none"
    else:
        hw = user_hw

    # Select codec based on HW
    if hw == "nvenc":
        vcodec = NVENC_MAP.get(vcodec_key, "h264_nvenc")
        # nvenc doesn't use preset the same way; use -preset p4 for speed
        preset_flag = f"-preset p4 -rc vbr -cq {crf}"
    elif hw == "vaapi":
        vcodec = VAAPI_MAP.get(vcodec_key, "h264_vaapi")
        preset_flag = f"-qp {crf}"
    else:
        vcodec = VCODEC_MAP.get(vcodec_key, "libx264")
        preset_flag = f"-preset {preset} -crf {crf}"

    resolution = RESOLUTION_MAP.get(resolution_key, "640:480")
    audio_bitrate = AUDIO_BITRATE_MAP.get(resolution_key, "128k")

    ext = ".mkv" if input_path.endswith(".mkv") else ".mp4"
    output_path = input_path.rsplit(".", 1)[0] + f"_encoded{ext}"

    # ─── Filters ───
    vf_parts = []

    # Scale (skip for 1080p to preserve original if higher)
    if resolution_key != "1080p":
        if hw == "vaapi":
            vf_parts.append(f"scale_vaapi=w={resolution.split(':')[0]}:h={resolution.split(':')[1]}")
        else:
            vf_parts.append(f"scale={resolution}")

    # Watermark text
    watermark_text = await get_user_field(user_id, "watermark_text", "")
    if watermark_text:
        safe_text = watermark_text.replace("'", "'\\''").replace(":", "\\:")
        vf_parts.append(
            f"drawtext=text='{safe_text}':fontsize=18:fontcolor=white@0.5"
            f":x=w-tw-10:y=h-th-10:borderw=1:bordercolor=black@0.3"
        )

    # Watermark image (overlay)
    watermark_image = await get_user_field(user_id, "watermark_image", "")

    vf_str = ""
    if vf_parts:
        if hw == "vaapi":
            vf_str = f'-vf "{",".join(vf_parts)}"'
        else:
            vf_str = f'-vf "{",".join(vf_parts)}"'

    # ─── HW accel input flags ───
    hw_input = ""
    if hw == "nvenc":
        hw_input = "-hwaccel cuda"
    elif hw == "vaapi":
        hw_input = "-hwaccel vaapi -hwaccel_output_format vaapi -vaapi_device /dev/dri/renderD128"

    # ─── Trim ───
    trim_flags = ""
    if trim_start:
        trim_flags += f" -ss {trim_start}"
    if trim_end:
        trim_flags += f" -to {trim_end}"

    # ─── Audio ───
    strict_flag = "-strict -2" if audio_type == "opus" else ""
    has_audio = _has_audio_stream(input_path)

    # Audio track selection
    audio_tracks = await get_user_field(user_id, "audio_tracks", "")
    subtitle_tracks = await get_user_field(user_id, "subtitle_tracks", "")

    if has_audio:
        if audio_tracks:
            # Map specific audio tracks
            audio_map_parts = " ".join(f"-map 0:a:{t.strip()}" for t in audio_tracks.split(",") if t.strip().isdigit())
            audio_part = f"-c:a {audio_type} -b:a {audio_bitrate} {audio_map_parts}"
        else:
            audio_part = f"-c:a {audio_type} -b:a {audio_bitrate} -map 0:a"
    else:
        audio_part = "-an"

    # Subtitle track selection
    if subtitle_tracks:
        sub_map_parts = " ".join(f"-map 0:s:{t.strip()}" for t in subtitle_tracks.split(",") if t.strip().isdigit())
        sub_part = f"-c:s copy {sub_map_parts}"
    else:
        sub_part = "-c:s copy -map 0:s?"

    # ─── Watermark image overlay (requires second input) ───
    overlay_input = ""
    overlay_filter = ""
    if watermark_image and not watermark_text:
        import os
        if os.path.exists(watermark_image):
            overlay_input = f'-i "{watermark_image}"'
            overlay_filter = '-filter_complex "overlay=W-w-10:H-h-10"'
            vf_str = ""  # overlay_filter replaces vf

    cmd = (
        f'ffmpeg -hide_banner -loglevel quiet {hw_input}{trim_flags} '
        f'-progress "{progress_file}" '
        f'-i "{input_path}" {overlay_input} '
        f"-vcodec {vcodec} {preset_flag} {vf_str} {overlay_filter} "
        f'-metadata title="Encoded by Erika-Amano" '
        f'-metadata:s:v title="Erika - {resolution_key} - {vcodec_key}" '
        f'-metadata:s:a title="Erika-Amano" '
        f"-map 0:v {audio_part} "
        f"{sub_part} {strict_flag} "
        f'"{output_path}" -y'
    )

    return cmd, output_path