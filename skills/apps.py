import logging
import os
import webbrowser
from difflib import get_close_matches

from core.context import CONTEXT, set_pending
from core.text_utils import normalize
from skills.search import SEARCH_ENGINES

logger = logging.getLogger("apps")


APPS = [
    {
        "name": "Bloco de Notas",
        "aliases": {"bloco", "notepad"},
        "path": "notepad.exe",
    },
    {
        "name": "Calculadora",
        "aliases": {"calculadora", "calc"},
        "path": "calc.exe",
    },
    {
        "name": "Chrome",
        "aliases": {"chrome", "navegador"},
        "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    },
    {
        "name": "VS Code",
        "aliases": {"vscode", "code"},
        "path": r"C:\Users\User\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    },
    {
        "name": "Spotify",
        "aliases": {"spotify"},
        "path": r"C:\Users\User\AppData\Roaming\Spotify\Spotify.exe",
    },
        {
        "name": "Steam",
        "aliases": {"steam"},
        "path": r"C:\Users\User\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk",
    },
    {
        "name": "Discord",
        "aliases": {"discord", "dc"},
        "path": r"C:\Users\User\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk",
    },
    {
        "name": "CurseForge",
        "aliases": {"curseforge", "curse", "minecraft", "mine"},
        "path": r"C:\Users\User\AppData\Local\Programs\CurseForge Windows\CurseForge.exe",
    },
    {
        "name": "Claude",
        "aliases": {"claude"},
        "path": r"shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude",
    },
]


SITES = [
    {
        "name": "YouTube",
        "aliases": {"youtube", "yt"},
        "url": "https://www.youtube.com",
    },
    {
        "name": "GitHub",
        "aliases": {"github", "git"},
        "url": "https://github.com",
    },
    {
        "name": "Gmail",
        "aliases": {"gmail", "email"},
        "url": "https://mail.google.com",
    },
    {
        "name": "Notion",
        "aliases": {"notion"},
        "url": "https://www.notion.so",
    },
    {
        "name": "Fiap",
        "aliases": {"fiap"},
        "url": "https://on.fiap.com.br/local/home",
    },
    {
        "name": "Google", 
        "aliases": {"google"},
        "url": "https://www.google.com"
    },
]


KNOWN_ALIASES = {alias for item in SITES + APPS for alias in item["aliases"]}


def find_in(text: str, items: list[dict]) -> dict | None:
    """Retorna o item cujo apelido aparece no texto, ou None."""
    words = set(normalize(text))
    for item in items:
        if item["aliases"] & words:
            return item
    return None


def find_app(text: str) -> dict | None:
    """Retorna o programa cujo apelido aparece no texto, ou None."""
    return find_in(text, APPS)


def format_table(title: str, items: list[dict]) -> str:
    """Monta uma tabela de texto com o nome e os apelidos de cada item."""
    width = max(len(item["name"]) for item in items)
    lines = [title]
    for item in items:
        aliases = ", ".join(sorted(item["aliases"]))
        lines.append(f"  {item['name']:<{width}}  →  {aliases}")
    return "\n".join(lines)


def list_targets(text: str) -> str:
    return format_table("Programas:", APPS) + "\n\n" + format_table("Sites:", SITES)


def open_target(text: str) -> str:
    app = find_app(text)

    site = find_site(text)
    if site is not None:
        webbrowser.open(site["url"])
        if site["name"].lower() in SEARCH_ENGINES:
            CONTEXT["last_engine"] = site["name"].lower()
        logger.info(f"Abriu o site {site["name"]}")
        return f"Abrindo o {site["name"]} no navegador!"

    if app is not None:
        try:
            os.startfile(app["path"])
        except FileNotFoundError:
            logger.error(f"Programa não encontrado: {app["name"]} {app["path"]}")
            return f"Não encontrei o {app["name"]} no seu computador. Confere o caminho na lista APPS."
        logger.info(f"Abriu o programa {app["name"]}")
        return f"Abrindo o {app["name"]}!"
    
    logger.warning(f"Pedido para abrir algo fora da lista: {text}")
    result = suggest_alias(text, SITES + APPS)
    if result is not None:
        typed, suggestion = result
        set_pending(open_target, f"abre o {suggestion}")
        return f"Não achei '{typed}'. Você quis dizer '{suggestion}'?"
    return "Não posso abrir isso.\n" + list_targets(text)


def find_site(text: str) -> dict | None:
    return find_in(text, SITES)


def suggest_alias(text, items):
    aliases = [alias for item in items for alias in item["aliases"]]
    for word in normalize(text):
        matches = get_close_matches(word, aliases, n=1, cutoff=0.75)
        if matches:
            return word, matches[0]
    return None
