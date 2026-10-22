import string
import unicodedata

def normalize(text: str) -> list[str]:
    """Deixa o texto em minúsculas, sem acentos e sem pontuação, e separa em palavras."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    for symbol in string.punctuation:
        text = text.replace(symbol, " ")
    return text.split()