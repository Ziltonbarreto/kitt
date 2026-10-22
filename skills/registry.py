"""A lista de comandos do KITT. A ORDEM IMPORTA: gatilhos específicos no alto, genéricos embaixo."""
from core.context import cancel, confirm
from integrations.spotify.commands import (
    spotify_now,
    spotify_play_playlist,
    spotify_play_track,
    spotify_playlists,
)
from skills.apps import list_targets, open_target
from skills.basics import clean, greet, introduce_kitt, tell_day, tell_time, tell_uptime, weekday
from skills.history import tell_history, tell_stats, tell_success_rate, tell_today, tell_unknown
from skills.media import smart_media
from skills.notes import add_note, list_notes
from skills.projects import work_on_project
from skills.routines import run_routine, tell_routines
from skills.search import SEARCH_WORDS, search_web
from skills.system import pc_status
from skills.timers import start_pomodoro, start_timer
from skills.weather import tell_weather


def show_help(text: str) -> str:
    lines = ["Eu sei fazer isto:"]
    for command in COMMANDS:
        lines.append(f" {command['name']} - {command['description']}")
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
            "name": "pc_status",
            "triggers": {"pc", "computador", "cpu", "ram", "memoria"},
            "description": "Mostra CPU, memória, disco e bateria",
            "function": pc_status,
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
