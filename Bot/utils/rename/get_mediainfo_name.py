from pymediainfo import MediaInfo


def get_filename(query: str):
    """Extract the title metadata from a media file."""
    try:
        mediainfo = MediaInfo.parse(query)
        for track in mediainfo.tracks:
            data = track.to_data()
            if data.get("track_type") == "General":
                return data.get("title")
    except Exception:
        pass
    return None