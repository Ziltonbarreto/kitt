import logging

import pyautogui

from core.text_utils import normalize
from integrations.spotify.client import SPOTIFY_ERRORS, get_spotify
from integrations.spotify.player import change_spotify_volume


logger = logging.getLogger("media")


VOLUME_STEPS = 5


MEDIA_ACTIONS = {
    "pausa": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "pausar": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "toca": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "continua": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "proxima": ("nexttrack", 1, "⏭️ Próxima faixa."),
    "pula": ("nexttrack", 1, "⏭️ Próxima faixa."),
    "anterior": ("prevtrack", 1, "⏮️ Faixa anterior."),
    "aumenta": ("volumeup", VOLUME_STEPS, "🔊 Aumentei o volume."),
    "sobe": ("volumeup", VOLUME_STEPS, "🔊 Aumentei o volume."),
    "abaixa": ("volumedown", VOLUME_STEPS, "🔉 Abaixei o volume."),
    "diminui": ("volumedown", VOLUME_STEPS, "🔉 Abaixei o volume."),
    "muta": ("volumemute", 1, "🔇 Mudo ligado/desligado."),
    "mudo": ("volumemute", 1, "🔇 Mudo ligado/desligado."),
    "tocar": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "toque": ("playpause", 1, "⏯️ Pausei/continuei a música."),
    "desmuta": ("volumemute", 1, "🔇 Mudo ligado/desligado."),
    "desmutar": ("volumemute", 1, "🔇 Mudo ligado/desligado."),
    "mutar": ("volumemute", 1, "🔇 Mudo ligado/desligado."),
    "aumentar": ("volumeup", VOLUME_STEPS, "🔊 Aumentei o volume."),
    "abaixar": ("volumedown", VOLUME_STEPS, "🔉 Abaixei o volume."),
    "diminuir": ("volumedown", VOLUME_STEPS, "🔉 Abaixei o volume."),
    "proximo": ("nexttrack", 1, "⏭️ Próxima faixa."),
}


def find_media_action(text):
    for word in normalize(text):
        if word in MEDIA_ACTIONS:
            return MEDIA_ACTIONS[word]
    return None


def control_media(text):
    action = find_media_action(text)
    if action is None:
        return "O que eu faço? Pausar, próxima, anterior, aumentar, abaixar ou mutar?"
    key, presses, message = action
    pyautogui.press(key, presses=presses)
    logger.info(f"Mídia: {key} x{presses}")
    return message


def smart_media(text):
    action = find_media_action(text)
    if "volume" in normalize(text) or (action is not None and action[0] in ("volumeup", "volumedown")):
        return handle_volume(text)
    if action is not None and action[0] in ("playpause", "nexttrack", "prevtrack"):
        try:
            sp = get_spotify()
            playback = sp.current_playback()
            if playback:
                key = action[0]
                if key == "nexttrack":
                    sp.next_track()
                    return "⏭️ Próxima faixa."
                if key == "prevtrack":
                    sp.previous_track()
                    return "⏮️ Faixa anterior."
                wants_pause = "pausa" in normalize(text) or "pausar" in normalize(text)
                if playback.get("is_playing"):
                    if not wants_pause and normalize(text)[0] in ("toca", "tocar", "continua"):
                        return "▶️ Já está tocando."
                    sp.pause_playback()
                    return "⏸️ Pausei a música."
                if wants_pause:
                    return "⏸️ Já está pausada."
                sp.start_playback()
                return "▶️ Continuando a música."
        except SPOTIFY_ERRORS as error:
            logger.warning(f"Spotify indisponível, usando as teclas: {error}")
    return control_media(text)


PC_WORDS = {"pc", "computador", "windows", "sistema"}
VOLUME_UP_WORDS = {"aumenta", "aumentar", "aumente", "sobe", "subir", "suba"}
VOLUME_DOWN_WORDS = {"abaixa", "abaixar", "abaixe", "diminui", "diminuir", "diminua", "baixa", "baixar"}
SET_WORDS = {"para", "pra"}
DEFAULT_VOLUME_STEP = 10


def parse_volume_request(text):
    """Função pura: devolve (alvo, modo, valor). Alvo: pc, spotify ou auto. Modo: up, down, set ou None."""
    words = normalize(text)
    word_set = set(words)
    if word_set & PC_WORDS:
        target = "pc"
    elif "spotify" in word_set:
        target = "spotify"
    else:
        target = "auto"

    number = next((int(word) for word in words if word.isdigit()), None)
    if number is not None:
        number = max(0, min(100, number))

    if word_set & (VOLUME_UP_WORDS | VOLUME_DOWN_WORDS):
        mode = "up" if word_set & VOLUME_UP_WORDS else "down"
        if number is None:
            return target, mode, DEFAULT_VOLUME_STEP
        if word_set & SET_WORDS:
            return target, "set", number
        return target, mode, number
    if number is not None:
        return target, "set", number
    return target, None, None


def change_pc_volume(mode, value):
    if mode == "set":
        return "No PC eu só consigo aumentar ou abaixar, sem porcentagem exata. Ex.: 'aumenta o volume do pc em 20'."
    key = "volumeup" if mode == "up" else "volumedown"
    presses = max(1, round(value / 2))
    pyautogui.press(key, presses=presses)
    logger.info(f"Volume do PC: {key} x{presses}")
    verb = "Aumentei" if mode == "up" else "Abaixei"
    return f"🔊 {verb} o volume do PC em cerca de {presses * 2}%."


def handle_volume(text):
    target, mode, value = parse_volume_request(text)
    if mode is None:
        return "O que eu faço com o volume? Ex.: 'aumenta o volume', 'volume do spotify em 30', 'aumenta o volume do pc'."

    if target != "pc":
        try:
            sp = get_spotify()
            playback = sp.current_playback()
            if playback and (target == "spotify" or playback.get("is_playing")):
                new = change_spotify_volume(sp, playback, mode, value)
                if new is None:
                    return "Esse dispositivo do Spotify não deixa mudar o volume pelo KITT."
                logger.info(f"Volume do Spotify: {new}%")
                return f"🎵 Volume do Spotify em {new}%."
            if target == "spotify":
                return "O Spotify não está tocando em nenhum dispositivo agora."
        except SPOTIFY_ERRORS as error:
            logger.warning(f"Spotify indisponível para o volume: {error}")
            if target == "spotify":
                return "Não consegui mudar o volume do Spotify agora."

    return change_pc_volume(mode, value)
