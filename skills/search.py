import logging
import webbrowser
from urllib.parse import quote_plus

from core.context import CONTEXT
from core.text_utils import normalize

logger = logging.getLogger("search")


SEARCH_WORDS = [                 
    "pesquisar", "pesquise", "pesquisa",
    "procurar", "procure", "procura",
    "buscar", "busque", "busca",
]


FILLER_PREFIXES = ["por ", "sobre ", "pra mim ", "para mim "]


FILLER_SUFFIXES = [" por favor", " pfv", " pf"]


SEARCH_ENGINES = {
    "youtube": {
        "aliases": {"youtube", "yt"},
        "url": "https://www.youtube.com/results?search_query=",
    },
        
    "google": {
        "aliases": {"google"},
        "url": "https://www.google.com/search?q=",
    },
}


def extract_query(text: str) -> str:
    """Pega o que vem depois da palavra de busca, sem o 'no youtube'."""
    lower = text.lower()
    query = ""
    for word in sorted(SEARCH_WORDS, key=len, reverse=True):
        if word in lower:
            query = lower.split(word, 1)[1]
            break
    for engine in SEARCH_ENGINES.values():        
        for alias in engine["aliases"]:           
            query = query.replace(f"no {alias}", "") 
    query = query.strip(" ?!.,")               
    for prefix in FILLER_PREFIXES:
        query = query.removeprefix(prefix)
    for suffix in FILLER_SUFFIXES:
        query = query.removesuffix(suffix)
    return query.strip(" ?!.,")


def build_search_url(text: str) -> str:
    """Monta o endereço da busca no buscador escolhido."""
    query = extract_query(text)
    engine = detect_engine(text)
    return SEARCH_ENGINES[engine]["url"] + quote_plus(query)


def search_web(text: str) -> str:
    query = extract_query(text)
    if not query:
        return "o que você quer que eu pesquise?"
    CONTEXT["last_engine"] = detect_engine(text)
    webbrowser.open(build_search_url(text))
    logger.info(f"Pesquisou: {query}")
    return f"Pesquisando \"{query}\" para você!"


def detect_engine(text: str) -> str:
    """Escolhe o buscador: o da frase, senão o último aberto, senão o Google."""
    words = set(normalize(text))
    for name, engine in SEARCH_ENGINES.items():
        if engine["aliases"] & words:
            return name
    if CONTEXT["last_engine"] is not None:
        return CONTEXT["last_engine"]
    return "google"
