"""Login no Spotify (OAuth). O segredo fica no .env e o token no .cache, fora do Git."""
import logging

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from core.paths import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")

CACHE_PATH = PROJECT_ROOT / ".cache"


logger = logging.getLogger("spotify")


SCOPES = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "playlist-read-private"
)


SPOTIFY_STATE = {"client": None}


SPOTIFY_ERRORS = (SpotifyException, requests.RequestException)


def get_spotify():
    if SPOTIFY_STATE["client"] is None:
        auth = SpotifyOAuth(scope=SCOPES, cache_path=str(CACHE_PATH), open_browser=True)
        SPOTIFY_STATE["client"] = spotipy.Spotify(auth_manager=auth, requests_timeout=10)
        logger.info("Cliente do Spotify criado")
    return SPOTIFY_STATE["client"]
