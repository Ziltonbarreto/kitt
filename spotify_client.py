import logging
from pathlib import Path

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

logger = logging.getLogger("spotify")

CACHE_PATH = Path(__file__).parent / ".cache"
SCOPES = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "playlist-read-private"
)
SPOTIFY_STATE = {"client": None}


def get_spotify():
    if SPOTIFY_STATE["client"] is None:
        auth = SpotifyOAuth(scope=SCOPES, cache_path=str(CACHE_PATH), open_browser=True)
        SPOTIFY_STATE["client"] = spotipy.Spotify(auth_manager=auth, requests_timeout=10)
        logger.info("Cliente do Spotify criado")
    return SPOTIFY_STATE["client"]