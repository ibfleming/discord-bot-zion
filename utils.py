import re
import utils


def is_yt_url(query):
    youtube_regex = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=[\w-]+|playlist\?list=[\w-]+|[a-zA-Z0-9_-]+)"
    )
    return re.match(youtube_regex, query) is not None


def is_spotify_url(query):
    spotify_track_regex = r"(https?://)?(open\.)?spotify\.com/track/[\w-]+(\?.*)?"
    return re.match(spotify_track_regex, query) is not None


def format_duration(duration):
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    return f"{minutes}m {seconds}s"


def sanitize_filename(filename):
    # Remove or replace problematic characters
    filename = re.sub(
        r"[^\w.-]", "", filename
    )  # Remove non-alphanumeric, non-dot, non-dash characters
    return filename
