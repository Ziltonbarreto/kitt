"""Os comandos do Spotify que o KITT entende."""
import logging

from core.text_utils import normalize
from integrations.spotify.client import SPOTIFY_ERRORS, get_spotify
from integrations.spotify.parsing import (
    extract_playlist_query,
    extract_track_query,
    format_playback,
    format_playlists,
    format_track,
    match_playlists,
    playlists_from_response,
)
from integrations.spotify.player import pick_device, play_and_confirm
from skills.apps import open_target
from skills.media import smart_media

logger = logging.getLogger("spotify")


def spotify_now(text):
    try:
        playback = get_spotify().current_playback()
    except SPOTIFY_ERRORS as error:
        logger.error(f"Spotify (tocando agora): {error}")
        return "Não consegui falar com o Spotify agora."
    return format_playback(playback)


def spotify_playlists(text):
    try:
        response = get_spotify().current_user_playlists(limit=50)
    except SPOTIFY_ERRORS as error:
        logger.error(f"Spotify (playlists): {error}")
        return "Não consegui buscar suas playlists agora."
    return format_playlists(playlists_from_response(response))


def spotify_play_playlist(text):
    query = extract_playlist_query(text)
    if not query:
        return "Qual playlist? Diga 'minhas playlists' para ver a lista."

    try:
        sp = get_spotify()
        playlists = playlists_from_response(sp.current_user_playlists(limit=50))
        matches = match_playlists(query, playlists)
        if not matches:
            return f'Não achei nenhuma playlist com "{" ".join(query)}".'
        if len(matches) > 1:
            options = "\n".join(f"  • {name}" for name, _ in matches)
            return f"Achei mais de uma:\n{options}\nQual delas? Fala uma palavra a mais."

        name, uri = matches[0]
        device = pick_device(sp)
        if device is None:
            open_target("spotify")
            return "O Spotify não estava aberto. Abri agora: me pede de novo em alguns segundos."

        playing = play_and_confirm(sp, device, context_uri=uri)
    except SPOTIFY_ERRORS as error:
        logger.error(f"Spotify (tocar playlist): {error}")
        return "Não consegui tocar no Spotify agora."

    if not playing:
        logger.warning(f"Spotify aceitou o play da playlist {name}, mas não começou a tocar")
        return "Mandei tocar, mas o Spotify não começou. Dá um play manual uma vez e me pede de novo?"

    logger.info(f"Spotify: tocando a playlist {name}")
    return f"▶️ Tocando a playlist {name}."


def spotify_play_track(text):
    query = extract_track_query(text)
    if query in {"", "a musica", "a música", "musica", "música"} or "volume" in normalize(text):
        return smart_media(text)

    try:
        sp = get_spotify()
        results = sp.search(q=query, type="track", limit=3, market="BR")
        tracks = results.get("tracks", {}).get("items", [])
        if not tracks:
            return f'Não achei nenhuma música com "{query}".'

        device = pick_device(sp)
        if device is None:
            open_target("spotify")
            return "O Spotify não estava aberto. Abri agora: me pede de novo em alguns segundos."

        track = tracks[0]
        playing = play_and_confirm(
            sp,
            device,
            context_uri=track["album"]["uri"],
            offset={"uri": track["uri"]},
        )
    except SPOTIFY_ERRORS as error:
        logger.error(f"Spotify (tocar música): {error}")
        return "Não consegui tocar no Spotify agora."

    if not playing:
        logger.warning(f"Spotify aceitou o play de {format_track(track)}, mas não começou a tocar")
        return "Mandei tocar, mas o Spotify não começou. Dá um play manual uma vez e me pede de novo?"

    logger.info(f"Spotify: tocando {format_track(track)}")
    response = f"▶️ Tocando {format_track(track)}."
    chosen = format_track(track)
    others = []
    for other in tracks[1:]:
        label = format_track(other)
        if label != chosen and label not in others:
            others.append(label)
    if others:
        response += "\n  Não era essa? Também achei: " + " | ".join(others)
    return response
