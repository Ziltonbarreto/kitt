import subprocess
from datetime import datetime, timedelta
from text_utils import normalize
from urllib.parse import quote_plus
from database import favorite_hour, most_used_commands, unknown_phrases, success_rate, today_summary, last_events
from difflib import get_close_matches
from routines import load_routines, invalid_targets, find_routine, plan_routine
from projects import load_projects, find_project
from weather import fetch_forecast, format_weather
from spotipy.exceptions import SpotifyException
from spotify_client import extract_track_query, format_track, get_spotify, format_playback, playlists_from_response, format_playlists, extract_playlist_query,  match_playlists, pick_device, play_and_confirm
from pathlib import Path
from media import control_media, find_media_action
import requests
import psutil
import webbrowser
import threading
import winsound
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
Assistente pessoal • v0.3
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

NOTES_PATH = Path(__file__).parent / "notes.txt"
NOTE_WORDS = ["anotar", "anota", "anote"]

CONTEXT = {"last_engine": None, "pending_action": None}

KNOWN_ALIASES = {alias for item in SITES + APPS for alias in item["aliases"]}

TIME_UNITS = {
    "segundo": 1, "segundos": 1, "seg": 1,
    "minuto": 60, "minutos": 60, "min": 60,
    "hora": 3600, "horas": 3600,
}

POMODORO_FOCUS = 25 * 60
POMODORO_CYCLES = 4
POMODORO_STATE = {"timer": None}


MAX_TIMER_SECONDS = 24 * 3600

SPOTIFY_ERRORS = (SpotifyException, requests.RequestException)


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
    if query in {"", "a musica", "a música", "musica", "música"}:
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

def smart_media(text):
    action = find_media_action(text)
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

def bytes_to_gb(value):
    return value / 1024 ** 3


def pc_status(text):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")

    lines = [
        "Status do PC:",
        f"  CPU: {cpu:.0f}%",
        f"  RAM: {bytes_to_gb(ram.used):.1f} de {bytes_to_gb(ram.total):.1f} GB ({ram.percent:.0f}%)",
        f"  Disco C: {bytes_to_gb(disk.used):.0f} de {bytes_to_gb(disk.total):.0f} GB ({disk.percent:.0f}%)",
    ]

    battery = psutil.sensors_battery()
    if battery is not None:
        plug = "carregando 🔌" if battery.power_plugged else "na bateria 🔋"
        lines.append(f"  Bateria: {battery.percent:.0f}% ({plug})")

    if ram.percent > 90:
        lines.append("⚠️ A memória está quase cheia. Vale fechar alguns programas.")
    return "\n".join(lines)

def pomodoro_durations(text):
    focus = parse_duration(text) or POMODORO_FOCUS
    return focus, max(focus // 5, 1)

def schedule_pomodoro(phase, cycle, focus, pause):
    seconds = focus if phase == "focus" else pause
    timer = threading.Timer(seconds, pomodoro_step, args=(phase, cycle, focus, pause))
    timer.daemon = True
    POMODORO_STATE["timer"] = timer
    timer.start()


def pomodoro_step(phase, cycle, focus, pause):
    winsound.Beep(800, 500)
    if phase == "focus":
        if cycle >= POMODORO_CYCLES:
            POMODORO_STATE["timer"] = None
            message = f"🎉 Pomodoro concluído! {POMODORO_CYCLES} ciclos de foco. Mandou bem!"
        else:
            message = f"🍅 Fim do foco {cycle}/{POMODORO_CYCLES}! Pausa de {format_duration(pause)}."
            schedule_pomodoro("pause", cycle, focus, pause)
    else:
        message = f"☕ Fim da pausa. Foco {cycle + 1}/{POMODORO_CYCLES} começando!"
        schedule_pomodoro("focus", cycle + 1, focus, pause)

    logger.info(f"Pomodoro: {message}")
    print(f"\nKITT: {message}")
    print("Você: ", end="", flush=True)

def start_pomodoro(text):
    words = set(normalize(text))
    running = POMODORO_STATE["timer"]

    if words & {"para", "parar", "pare"}:
        if running is None:
            return "Não tem nenhum pomodoro rodando."
        running.cancel()
        POMODORO_STATE["timer"] = None
        logger.info("Pomodoro interrompido")
        return "Pomodoro parado. Descansa um pouco! 😌"

    if running is not None:
        return "Já tem um pomodoro rodando. Diga 'para o pomodoro' para parar."

    focus, pause = pomodoro_durations(text)
    schedule_pomodoro("focus", 1, focus, pause)
    logger.info(f"Pomodoro iniciado: foco {focus}s, pausa {pause}s")
    return f"🍅 Pomodoro iniciado! Foco 1/{POMODORO_CYCLES}: {format_duration(focus)}."


def timer_done(label):
    winsound.Beep(1000, 600)
    logger.info(f"Timer concluído: {label}")
    print(f"\nKITT: ⏰ Tempo esgotado! ({label})")
    print("Você: ", end="", flush=True)


def start_timer(text):
    seconds = parse_duration(text)
    if seconds is None:
        return "Quanto tempo? Exemplo: 'me avisa em 10 minutos'."
    if not 1 <= seconds <= MAX_TIMER_SECONDS:
        return "Consigo marcar de 1 segundo até 24 horas."

    label = format_duration(seconds)
    timer = threading.Timer(seconds, timer_done, args=(label,))
    timer.daemon = True
    timer.start()
    logger.info(f"Timer iniciado: {label}")
    return f"Beleza! Te aviso em {label}."


def parse_duration(text):
    words = normalize(text)
    for i, word in enumerate(words):
        if word.isdigit() and i + 1 < len(words) and words[i + 1] in TIME_UNITS:
            return int(word) * TIME_UNITS[words[i + 1]]
    return None

def format_duration(seconds):
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}min")
    if secs:
        parts.append(f"{secs}s")
    return " ".join(parts) or "0s"

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
        "  • Abro programas, sites, projetos e rotinas (modo estudo, modo dev)\n"
        "  • Pesquiso no Google e no YouTube\n"
        "  • Timer, Pomodoro e notas rápidas\n"
        "  • Clima de Montes Claros, status do PC e controle de música\n"
        "  • Lembro do que você me pediu e sugiro rotinas no seu horário\n"
        "\n"
        "O que vem por aí:\n"
        "  • Uma interface no navegador\n"
        "  • Voz e inteligência artificial\n"
        "  • E, um dia, a casa inteira\n"
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
    result = suggest_alias(text, SITES + APPS)
    if result is not None:
        typed, suggestion = result
        set_pending(open_target, f"abre o {suggestion}")
        return f"Não achei '{typed}'. Você quis dizer '{suggestion}'?"
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

def tell_stats(text):
    rows = most_used_commands()
    if not rows:
        return "Ainda não tenho dados. Me peça algumas coisas primeiro!"
    lines = ["Seus comandos mais usados:"]
    for command, total in rows:
        lines.append(f"  {command}: {total}x")
    return "\n".join(lines)

def tell_unknown(text):
    rows = unknown_phrases()
    if not rows:
        return "Até agora entendi tudo o que você pediu! 😎"
    lines = ["Frases que não entendi:"]
    for phrase, total in rows:
        lines.append(f"  {phrase}: {total}x")
    return "\n".join(lines)

def tell_success_rate(text):
    total, rate = success_rate()
    if total == 0:
        return "Ainda não tenho pedidos para calcular"
    else:
        return f"Entendi {int(rate)}% dos seus {total} pedidos"

def tell_today(text):
    total, first, top = today_summary()
    if total == 0:
        return "Você ainda não me pediu nada!"
    summary = f"Hoje foram {total} pedidos desde as {first[11:16]}."
    if top is None:
        return summary
    command, count = top
    return f"{summary} Seu comando favorito: {command} ({count}x)."

def suggest_alias(text, items):
    aliases = [alias for item in items for alias in item["aliases"]]
    for word in normalize(text):
        matches = get_close_matches(word, aliases, n=1, cutoff=0.75)
        if matches:
            return word, matches[0]
    return None

CONFIRM_TIMEOUT = timedelta(minutes=1)


def set_pending(function, argument):
    CONTEXT["pending_action"] = (function, argument, datetime.now())


def confirm(text):
    action = CONTEXT["pending_action"]
    CONTEXT["pending_action"] = None
    if action is None:
        return "Não tenho nada para confirmar agora."

    function, argument, created_at = action
    if datetime.now() - created_at > CONFIRM_TIMEOUT:
        return "Essa pergunta expirou. Me peça de novo."
    return function(argument)


def cancel(text):
    if CONTEXT["pending_action"] is None:
        return "Não tem nada para cancelar."
    CONTEXT["pending_action"] = None
    return "Ok, cancelado."

def tell_routines(text):
    routines = load_routines()
    if not routines:
        return "Você ainda não tem rotinas (ou o routines.json tem erro)."

    lines = ["Suas rotinas:"]
    for name, routine in routines.items():
        lines.append(f" {name} -> {routine.get('description', 'sem descrição')}")

    problems = invalid_targets(routines, KNOWN_ALIASES)
    for name, target in problems:
        lines.append(f"⚠️ Na rotina '{name}', não conheço '{target}'.")

    return "\n".join(lines)

MAX_WITHOUT_CONFIRM = 3


def execute_routine(name):
    routine = load_routines().get(name)
    if routine is None:
        return f"A rotina {name} não existe mais."

    valid, skipped = plan_routine(routine, KNOWN_ALIASES)
    results = [open_target(target) for target in valid]
    for target in skipped:
        logger.warning(f'Rotina "{name}": apelido desconhecido "{target}"')
        results.append(f'⚠️ Pulei "{target}": não está na minha lista.')

    message = routine.get("message", f"Ativando o modo {name}!")
    logger.info(f"Rotina executada: {name}")
    return message + "\n  " + "\n  ".join(results)

def run_routine(text):
    routines = load_routines()
    if not routines:
        return "Você ainda não tem rotinas (ou o routines.json tem erro)."

    name = find_routine(text, routines)
    if name is None:
        names = ", ".join(routines)
        return f"Qual modo? Eu conheço: {names}."

    valid, _ = plan_routine(routines[name], KNOWN_ALIASES)
    if len(valid) > MAX_WITHOUT_CONFIRM or routines[name].get("confirm", False):
        set_pending(execute_routine, name)
        return f"O modo {name} vai abrir {len(valid)} coisas. Confirma? (sim / cancela)"

    return execute_routine(name)

def routine_suggestion():
    now_hour = datetime.now().strftime("%H")
    for name in load_routines():
        if favorite_hour(name) == now_hour:
            set_pending(execute_routine, name)    
            return f"São {now_hour}h, horário em que você costuma ativar o modo {name}. Quer ativar? (responda 'sim')"
    return None

def work_on_project(text):
    projects = load_projects()
    if not projects:
        return "Você ainda não tem projetos (ou o projects.json tem erro)."

    key = find_project(text, projects)
    if key is None:
        names = ", ".join(project["name"] for project in projects.values())
        return f"Qual projeto? Eu conheço: {names}."

    project = projects[key]
    results = []

    folder = project.get("folder", "")
    if os.path.isdir(folder):
        vscode = find_app("vscode")
        subprocess.Popen(
            [vscode["path"], folder],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS,
        )
        results.append("Abrindo a pasta do projeto no VS Code")
    else:
        logger.warning(f'Pasta do projeto "{key}" não existe: {folder}')
        results.append(f"⚠️ Não achei a pasta do {project['name']}.")

    valid, skipped = plan_routine(project, KNOWN_ALIASES)
    results += [open_target(target) for target in valid]
    for target in skipped:
        results.append(f'⚠️ Pulei "{target}": não está na minha lista.')

    logger.info(f"Projeto aberto: {key}")
    message = project.get("message", f"Bora trabalhar no {project['name']}!")
    return message + "\n  " + "\n  ".join(results)

def tell_weather(text):
    data = fetch_forecast()
    if data is None:
        return "Não consegui ver o clima agora. Confere se a internet está funcionando."
    return format_weather(data)

def tell_history(text):
    rows = last_events()
    if not rows:
        return "Você ainda não me pediu nada"

    lines = ["Seus últimos pedidos:"]
    for created_at, phrase, success in rows:
        icon = "✅" if success else "❌"
        lines.append(f"  {created_at[11:16]}  {icon} {phrase}")
    return "\n".join(lines)


COMMANDS = [
        {
            "name": "confirm", 
            "triggers": {"sim", "exatamente", "exato"},
            "description": "Confirma a última sugestão", 
            "function": confirm,
        },
        {   
            "name": "cancel", 
            "triggers": {"cancela", "cancelar"},
            "description": "Cancela a última pergunta", 
            "function": cancel,
        },
        {
            "name": "timer",
            "triggers": {"avisa", "timer", "cronometro"},
            "description": "Avisa depois de um tempo (ex.: me avisa em 10 minutos)",
            "function": start_timer,
        },
        {
            "name": "pomodoro",
            "triggers": {"pomodoro"},
            "description": "Ciclos de foco e pausa (ex.: pomodoro, para o pomodoro)",
            "function": start_pomodoro,
        },
        {
            "name": "did",
            "triggers": {"fiz"},
            "description": "Mostra oque você fez hoje",
            "function": tell_today,
        },
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
            "name": "note",
            "triggers": {"anota", "anote", "anotar"},
            "description": "Anota algo (ex.: anota: comprar café)",
            "function": add_note,
        },
        {
            "name": "notes",
            "triggers": {"notas"},
            "description": "Mostra ou apaga suas notas",
            "function": list_notes,
        },
        {
            "name": "weather",
            "triggers": {"clima", "chover", "chuva", "temperatura", "calor", "frio"},
            "description": "Clima de agora e previsão de hoje em Montes Claros",
            "function": tell_weather,
        },
        {
            "name": "day",
            "triggers": {"hoje", "data", "hj"},
            "description": "diz o dia atual",
            "function": tell_day,
        },
        {
            "name": "greet",
            "triggers": {"oi", "ola", "bom", "eae", "eai"},
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
            "name": "stats",
            "triggers": {"uso", "usado", "estatisticas"},
            "description": "Mostra os comandos que você mais usa", 
            "function": tell_stats,
        },
        {
            "name": "missed_report",
            "triggers": {"entendeu"},
            "description": "Mostra as frases que ele não entendeu",
            "function": tell_unknown,
        },
        {
            "name": "right",
            "triggers": {"acerta", "acerto", "acertos"},
            "description": "Mostra quantos acertos ele tem",
            "function": tell_success_rate,
        },
        {
            "name": "routines",
            "triggers": {"rotina", "rotinas"},
            "description": "Mostra as rotinas suas",
            "function": tell_routines,
        },
        {
            "name": "routine", 
            "triggers": {"modo"},
            "description": "Executa uma rotina (ex.: modo estudo)", 
            "function": run_routine,
        },
        {
            "name": "project", 
            "triggers": {"mexer", "trabalhar", "projeto"},
            "description": "Abre um projeto (ex.: vou mexer no fiscaliza)", 
            "function": work_on_project,
        },
        {
            "name": "pc_status",
            "triggers": {"pc", "computador", "cpu", "ram", "memoria"},
            "description": "Mostra CPU, memória, disco e bateria",
            "function": pc_status,
        },
        {
            "name": "spotify_now",
            "triggers": {"tocando"},
            "description": "Mostra o que está tocando no Spotify",
            "function": spotify_now,
        },
        {
            "name": "spotify_play",
            "triggers": {"playlist"},
            "description": "Toca uma playlist do Spotify (ex.: toca a playlist lofi)",
            "function": spotify_play_playlist,
        },
        {
            "name": "spotify_playlists",
            "triggers": {"playlists"},
            "description": "Lista suas playlists do Spotify",
            "function": spotify_playlists,
        },
        {
            "name": "spotify_track",
            "triggers": {"spotify", "toca", "tocar", "toque", "coloca", "bota"},
            "description": "Busca e toca uma música (ex.: toca yellow no spotify)",
            "function": spotify_play_track,
        },
        {
            "name": "media",
            "triggers": {"musica", "volume", "som", "faixa", "mudo", "muta"},
            "description": "Controla música e volume (ex.: pausa a música, aumenta o volume)",
            "function": smart_media,
        },
        {
            "name": "history",
            "triggers": {"pedi", "historico"},
            "description": "Mostra seus últimos pedidos",
            "function": tell_history,
        },
            {
            "name": "open",
            "triggers": {"abre", "abrir", "abra"},
            "description": "abre um programa ou site permitido",
            "function": open_target,
        },
    ]