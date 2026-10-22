import logging

import pyautogui

from text_utils import normalize

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