from text_utils import normalize
from datetime import datetime
from urllib.parse import quote_plus
import webbrowser
import logging
import random
import os

logger = logging.getLogger("commands")

BANNER = """
██╗  ██╗██╗████████╗████████╗
██║ ██╔╝██║╚══██╔══╝╚══██╔══╝
█████╔╝ ██║   ██║      ██║
██╔═██╗ ██║   ██║      ██║
██║  ██╗██║   ██║      ██║
╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝
Assistente pessoal • v0.1
"""

ASSISTANT_NAME = "KITT"

MORNING_GREETINGS = [
    "Bom dia, chefe! Motores aquecidos e prontos pra rodar.",
    "Bom dia! Café na mão e código na tela? Bora!",
    "E aí, bom dia! Sistemas online, pode mandar.",
    "Bom dia! Hoje o dia tá com cara de deploy sem bug.",
]

AFTERNOON_GREETINGS = [
    "Boa tarde, chefe! Seguimos em velocidade de cruzeiro.",
    "Opa, boa tarde! Metade do dia vencida, bora pra outra metade.",
    "Boa tarde! Tô aqui firme, sem superaquecer.",
    "Boa tarde! Pausa pro café ou a gente acelera?",
]

EVENING_GREETINGS = [
    "Boa noite, chefe! Modo noturno ativado.",
    "Boa noite! Programando a essa hora? Respeito.",
    "E aí, boa noite! As melhores ideias aparecem depois das dez.",
    "Boa noite! Faróis ligados, pode mandar.",
]

START_TIME = datetime.now()

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
        "path": r"C:\Users\User\Documents\kitt\atalhos\Claude.lnk",
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
]

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

CONTEXT = {"last_engine": None}

def show_help(text: str) -> str:
    lines = ["Eu sei fazer isto:"]
    for command in COMMANDS:
        lines.append(f" {command['name']} - {command['description']}")
    return "\n".join(lines)

def tell_time(text: str) -> str:
    time_now = datetime.now()
    return f"Agora são {time_now:%H:%M}"

def tell_day(text: str) -> str:
    day_now = datetime.now()
    return f"Hoje é {day_now:%d/%m/%Y}"

def greet(text: str) -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return random.choice(MORNING_GREETINGS)
    elif 12 <= hour < 17:
        return random.choice(AFTERNOON_GREETINGS)
    else:
        return random.choice(EVENING_GREETINGS)

def weekday(text: str) -> str:
    WEEKDAYS = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
    ]

    number = datetime.now().weekday()
    name = WEEKDAYS[number]
    return f"Hoje é {name}"

def introduce_kitt(text: str) -> str:
    return (
        f"Prazer, eu sou o {ASSISTANT_NAME}! 🚗\n"
        "\n"
        "Sou seu assistente pessoal, feito em Python e rodando direto no seu computador.\n"
        "Nasci no terminal, mas tenho planos grandes.\n"
        "\n"
        "O que eu já faço:\n"
        "  • Digo a hora, a data e o dia da semana\n"
        "  • Abro seus programas e sites favoritos\n"
        "  • Pesquiso no Google e no YouTube\n"
        "  • Cumprimento, conto há quanto tempo estou ligado e limpo a tela\n"
        "\n"
        "O que vem por aí:\n"
        "  • Rotinas, timer e Pomodoro\n"
        "  • Clima, notas rápidas e status do PC\n"
        "  • Voz, inteligência artificial e, um dia, a casa inteira\n"
        "\n"
        "Digite 'ajuda' para ver todos os comandos. Bora acelerar? 🏁"
    )

def tell_uptime(text: str) -> str:
    elapsed = datetime.now() - START_TIME 
    seconds = int(elapsed.total_seconds())
    minutes, secs = divmod(seconds, 60)
    return f"Estou ligado há {minutes} minutos e {secs} segundos."

def clean(text: str) -> str:
    os.system("cls")
    logger.info("Limpou a tela")
    return f"Tela limpa com sucesso!\n{BANNER}"

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
    return "Não posso abrir isso.\n" + list_targets(text)

def find_site(text: str) -> dict | None:
    return find_in(text, SITES)

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

COMMANDS = [
        {
        "name": "kitt",
        "triggers": {"quem", "apresente", "apresenta"},
        "description": "Faz a apresentação do Kitt",
        "function": introduce_kitt,
        },
        {
            "name": "help",
            "triggers": {"ajuda", "comandos"},
            "description": "mostrar esta lista",
            "function": show_help,
        },
        {
            "name": "time",
            "triggers": {"hora", "horas", "hr", "hrs"},
            "description": "diz a hora atual",
            "function": tell_time,
        },
        {
        "name": "week",
        "triggers": {"semana"},
        "description": "diz o dia da semana",
        "function": weekday,
        },
        {
            "name": "day",
            "triggers": {"hoje", "data", "hj"},
            "description": "diz o dia atual",
            "function": tell_day,
        },
        {
            "name": "greet",
            "triggers": {"oi", "ola", "bom"},
            "description": "diz oi",
            "function": greet,
        },
        {
            "name": "uptime",
            "triggers": {"quanto", "ligado"},
            "description": "Há quanto tempo o Kitt está funcionando",
            "function": tell_uptime,
        },
        {
            "name": "clean",
            "triggers": {"limpa", "limpar"},
            "description": "Limpa a tela",
            "function": clean,
        },
        {
            "name": "list",
            "triggers": {"programas", "sites", "lista"},
            "description": "mostra os programas e sites que posso abrir",
            "function": list_targets,
        },
        {
            "name": "search",
            "triggers": set(SEARCH_WORDS),
            "description": "Pesquisa no Google ou no Youtube",
            "function": search_web,
        },
        {
            "name": "open",
            "triggers": {"abre", "abrir", "abra"},
            "description": "abre um programa ou site permitido",
            "function": open_target,
        },
    ]