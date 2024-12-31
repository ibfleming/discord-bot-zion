import re


def is_url(query):
    youtube_regex = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=[\w-]+|playlist\?list=[\w-]+|[a-zA-Z0-9_-]+)"
    )
    return re.match(youtube_regex, query) is not None


def format_duration(duration):
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    return f"{minutes}m {seconds}s"
