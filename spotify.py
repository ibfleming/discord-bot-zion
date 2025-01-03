import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
    )
)


def spotify_url_to_yt_search(track_url):
    track_id = track_url.split("/")[-1].split("?")[0]
    track = sp.track(track_id=track_id)
    release_year = track["album"]["release_date"].split("-")[0]

    return (
        track["name"]
        + " by "
        + ", ".join(artist["name"] for artist in track["artists"])
        + " ("
        + release_year
        + ") Topic"
    )
