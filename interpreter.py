from text_utils import normalize
from commands import COMMANDS

WAKE_WORDS = {"kitt"}



def identify(text: str) -> dict | None:
    """Retorna o comando cujo gatilho aparece no texto, ou None."""
    words = normalize(text)
    if words and words[0] in WAKE_WORDS:
        words = words[1:]

    for command in COMMANDS:
        if command["triggers"] & set(words):
            return command
    return None
