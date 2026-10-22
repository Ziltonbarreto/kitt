import logging
from datetime import datetime

from core.context import set_pending
from core.paths import PROJECT_ROOT
from core.text_utils import normalize

logger = logging.getLogger("notes")

NOTES_PATH = PROJECT_ROOT / "notes.txt"


NOTE_WORDS = ["anotar", "anota", "anote"]


def extract_note(text):
    lower = text.lower()
    for word in NOTE_WORDS:
        if word in lower:
            return text[lower.index(word) + len(word):].strip(" :")
    return ""


def add_note(text):
    note = extract_note(text)
    if not note:
        return "O que eu anoto? Exemplo: 'anota: comprar café'."
    with NOTES_PATH.open("a", encoding="utf-8") as file:
        file.write(f"{datetime.now():%d/%m %H:%M} | {note}\n")
    logger.info("Nota adicionada")
    return "Anotado! 📝"


def clear_notes(_):
    NOTES_PATH.unlink(missing_ok=True)
    logger.info("Notas apagadas")
    return "Notas apagadas. 🧹"


def list_notes(text):
    if "apaga" in normalize(text) or "apagar" in normalize(text):
        if not NOTES_PATH.exists():
            return "Você não tem notas para apagar."
        set_pending(clear_notes, None)
        return "Apago TODAS as suas notas? Isso não dá para desfazer. (sim / cancela)"

    if not NOTES_PATH.exists():
        return "Você ainda não tem notas. Diga 'anota: ...' para criar uma."

    lines = NOTES_PATH.read_text(encoding="utf-8").splitlines()
    recent = lines[-10:]
    result = ["Suas notas:"]
    for number, line in enumerate(recent, start=len(lines) - len(recent) + 1):
        result.append(f"  {number}. {line}")
    return "\n".join(result)
