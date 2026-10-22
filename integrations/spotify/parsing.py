"""Funções puras do Spotify: não acessam a internet, então dá para testar com assert."""
from core.text_utils import normalize


STOP_WORDS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "minha", "meu", "aquela", "musica"}


PLAY_WORDS = ["tocar", "toque", "toca", "coloca", "bota"]


TRACK_PREFIXES = ["a musica ", "a música ", "musica ", "música "]


def format_playback(playback):
    if not playback or not playback.get("item"):
        return "Nada tocando no Spotify agora."
    item = playback["item"]
    artists = ", ".join(artist["name"] for artist in item.get("artists", []))
    state = "▶️ Tocando" if playback.get("is_playing") else "⏸️ Pausado"
    device = playback.get("device", {}).get("name", "dispositivo desconhecido")
    title = f"{item['name']} — {artists}" if artists else item["name"]
    return f"{state}: {title} (em {device})"


def playlists_from_response(response):
    return [(item["name"], item["uri"]) for item in response.get("items", []) if item]


def format_playlists(playlists):
    if not playlists:
        return "Você não tem playlists (ou não consegui ver nenhuma)."
    lines = ["Suas playlists:"]
    for number, (name, _) in enumerate(playlists, start=1):
        lines.append(f"  {number}. {name}")
    return "\n".join(lines)


def extract_playlist_query(text):
    words = normalize(text)
    if "playlist" in words:
        words = words[words.index("playlist") + 1:]
    return [word for word in words if word not in STOP_WORDS]


def match_playlists(query_words, playlists):
    if not query_words:
        return []
    query = set(query_words)
    scored = []
    for name, uri in playlists:
        score = len(query & set(normalize(name)))
        if score:
            scored.append((score, name, uri))
    if not scored:
        return []
    best = max(score for score, _, _ in scored)
    return [(name, uri) for score, name, uri in scored if score == best]


def extract_track_query(text):
    lower = text.lower()
    for word in PLAY_WORDS:
        if word in lower:
            query = lower.split(word, 1)[1]
            break
    else:
        return ""
    query = query.replace("no spotify", "").strip()
    for prefix in TRACK_PREFIXES:
        query = query.removeprefix(prefix)
    return query.strip(" ?!.,")


def format_track(track):
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    return f"{track['name']} — {artists}" if artists else track["name"]
