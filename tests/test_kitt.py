from core.interpreter import identify
from skills.basics import greet, MORNING_GREETINGS, AFTERNOON_GREETINGS, EVENING_GREETINGS
from skills.apps import find_app, find_site
from skills.search import extract_query, build_search_url
from skills.search import detect_engine
from skills.apps import suggest_alias
from core.context import confirm, cancel
from skills.history import tell_today
from datetime import timedelta
from skills.apps import SITES, APPS
from core.context import CONTEXT
from skills.routines import load_routines, invalid_targets, find_routine, plan_routine
from datetime import datetime
import os
import tempfile
from core import database
from skills.projects import find_project

from skills.timers import parse_duration, format_duration, pomodoro_durations
from skills.notes import extract_note
from skills.system import bytes_to_gb
from skills.weather import describe_code, format_weather
from integrations.spotify.parsing import extract_track_query, format_track



assert bytes_to_gb(1024 ** 3) == 1
assert bytes_to_gb(512 * 1024 ** 2) == 0.5
assert identify("como está o pc?")["name"] == "pc_status"

assert extract_note("anota: comprar cabo USB-C") == "comprar cabo USB-C"
assert extract_note("kitt anotar estudar SQL") == "estudar SQL"
assert extract_note("anote") == ""

assert pomodoro_durations("pomodoro") == (1500, 300)
assert pomodoro_durations("pomodoro de 10 segundos") == (10, 2)
assert pomodoro_durations("pomodoro de 3 segundos") == (3, 1)

assert parse_duration("me avisa em 10 segundos") == 10
assert parse_duration("timer de 5 minutos") == 300
assert parse_duration("me avisa em 1 hora") == 3600
assert parse_duration("me avisa daqui a pouco") is None
assert parse_duration("me avisa em 10") is None

assert format_duration(300) == "5min"
assert format_duration(3725) == "1h 2min 5s"
assert format_duration(10) == "10s"

assert identify("me avisa em 2 horas")["name"] == "timer"

projects = {"fiscaliza": {"aliases": ["fiscaliza", "volpe"]}, "next": {"aliases": ["next"]}}
assert find_project("vou mexer no Fiscaliza", projects) == "fiscaliza"
assert find_project("bora estudar next", projects) == "next"
assert find_project("vou mexer no hackgov", projects) is None

from core.interpreter import strip_wake_word

assert strip_wake_word("kitt vou mexer no fiscaliza") == "vou mexer no fiscaliza"
assert strip_wake_word("KITT, que horas são?") == "que horas são?"
assert strip_wake_word("vou mexer no kitt") == "vou mexer no kitt"
assert strip_wake_word("kitt") == ""

from skills.media import find_media_action

assert find_media_action("pausa a música")[0] == "playpause"
assert find_media_action("próxima música")[0] == "nexttrack"
assert find_media_action("aumenta o volume") == ("volumeup", 5, "🔊 Aumentei o volume.")
assert find_media_action("faz um café") is None
assert identify("aumenta o volume")["name"] == "media"
from integrations.spotify.parsing import format_playback, playlists_from_response, format_playlists

from integrations.spotify.parsing import extract_playlist_query, match_playlists

mine = [
    ("Bruno Mars - As Melhores", "uri1"),
    ("Lofi Study 2026", "uri2"),
    ("MODÃO SERTANEJO RAIZ - SÓ AS MELHORES 🎵", "uri3"),
    ("SERTANEJO ROMÂNTICO 💗(As Melhores  Antigo a 2026)", "uri4"),
    ("The Beatles: Best Of The Best", "uri5"),
]

assert extract_playlist_query("kitt toca a playlist do bruno mars") == ["bruno", "mars"]
assert match_playlists(["bruno", "mars"], mine) == [("Bruno Mars - As Melhores", "uri1")]
assert match_playlists(["lofi"], mine) == [("Lofi Study 2026", "uri2")]
assert match_playlists(["modao"], mine) == [("MODÃO SERTANEJO RAIZ - SÓ AS MELHORES 🎵", "uri3")]
assert len(match_playlists(["sertanejo"], mine)) == 2
assert match_playlists(["funk"], mine) == []
assert identify("toca a playlist lofi")["name"] == "spotify_play"

playing = {
    "is_playing": True,
    "device": {"name": "PC"},
    "item": {"name": "Yellow", "artists": [{"name": "Coldplay"}]},
}
assert format_playback(playing) == "▶️ Tocando: Yellow — Coldplay (em PC)"
assert format_playback(None) == "Nada tocando no Spotify agora."

podcast = {"is_playing": False, "device": {"name": "PC"}, "item": {"name": "Episódio 42"}}
assert format_playback(podcast) == "⏸️ Pausado: Episódio 42 (em PC)"

fake_response = {"items": [{"name": "Estudo", "uri": "spotify:playlist:abc"}, None]}
assert playlists_from_response(fake_response) == [("Estudo", "spotify:playlist:abc")]
assert format_playlists([("Estudo", "x"), ("Treino", "y")]) == "Suas playlists:\n  1. Estudo\n  2. Treino"

assert identify("qual música está tocando?")["name"] == "spotify_now"
assert identify("minhas playlists")["name"] == "spotify_playlists"


def test_database():
    test_db = os.path.join(tempfile.gettempdir(), "kitt_test.db")
    if os.path.exists(test_db):
        os.remove(test_db)
    database.DB_PATH = test_db

    database.init_db()
    assert tell_today("o que eu fiz hoje") == "Você ainda não me pediu nada!"
    database.log_event("uai", None, False)
    assert tell_today("o que eu fiz hoje").startswith("Hoje foram 1 pedidos")
    os.remove(test_db)
    database.init_db()

    database.log_event("oi", "greet", True)
    database.log_event("uai", None, False)
    database.log_event("uai", None, False)

    result = database.unknown_phrases()
    assert result == [("uai", 2)], f"Veio: {result} | Banco: {database.DB_PATH}"
    assert database.most_used_commands() == [("greet", 1)]
    assert database.success_rate() == (3, 33.0)

    database.log_event("modo estudo", "routine", True)
    database.log_event("modo estudo", "routine", True)
    assert database.favorite_hour("estudo") is None

    database.log_event("Modo ESTUDO", "routine", True)
    assert database.favorite_hour("estudo") == datetime.now().strftime("%H")
    
    rows = database.last_events(2)
    assert len(rows) == 2
    assert rows[0][1] == "Modo ESTUDO"


all_greetings = MORNING_GREETINGS + AFTERNOON_GREETINGS + EVENING_GREETINGS
for _ in range(20):
    assert greet("oi") in all_greetings

assert identify("KITT, ajuda")["name"] == "help"
assert identify("kitt, que horas são?")["name"] == "time"
assert identify("que dia é hoje?")["name"] == "day"
assert identify("qual a data de  hoje?")["name"] == "day"
assert identify("Que dia da semana é hoje?")["name"] == "week"
assert identify("Que HORAS são")["name"] == "time"
assert identify("Quem é voce?")["name"] == "kitt"
assert identify("Há quanto tempo vc está ligado?")["name"] == "uptime"
assert identify("oi Kitt")["name"] == "greet"
assert identify("Limpa a tela")["name"] == "clean"
assert identify("kitt, abre o vs code")["name"] == "open"
assert identify("kitt, abre o youtube")["name"] == "open"
assert find_site("abre o youtube")["name"] == "YouTube"
assert find_site("abre o vs code") is None
assert find_app("abre o vs code")["name"] == "VS Code"
assert find_app("abre o discord")["name"] == "Discord"
assert find_app("abre o minecraft")["name"] == "CurseForge"
assert identify("quais programas você abre?")["name"] == "list"
assert identify("abre o gmail no chrome")["name"] == "open"
assert find_site("abre o gmail no chrome")["name"] == "Gmail"
assert find_app("abre o word") is None
assert identify("faça um café") is None
assert identify("") is None

assert identify("kitt, procure uma receita de bolo")["name"] == "search"
assert extract_query("kitt, procure uma receita de bolo") == "uma receita de bolo"
assert extract_query("busque lofi no youtube") == "lofi"
assert extract_query("procurar python") == "python"
assert extract_query("pesquisa receita de bolo no youtube") == "receita de bolo"
assert extract_query("pesquisa no youtube") == ""
assert build_search_url("pesquisa lofi no youtube").startswith("https://www.youtube.com")
assert build_search_url("pesquisa lofi").startswith("https://www.google.com")
assert extract_query("busque por bolo de cenoura") == "bolo de cenoura"
assert extract_query("pesquise por como fazer um esp32 por favor") == "como fazer um esp32"
assert extract_query("pesquisa receita de bolo por quilo") == "receita de bolo por quilo"
assert extract_query("pesquisa receita de bolo, por favor") == "receita de bolo"

CONTEXT["last_engine"] = None
assert detect_engine("busque por esp32") == "google"
assert detect_engine("pesquise no yt por lofi") == "youtube"
assert extract_query("pesquise no yt por lofi") == "lofi"

CONTEXT["last_engine"] = "youtube"
assert detect_engine("busque por como fazer um sistema no ESP32") == "youtube"
assert detect_engine("busque esp32 no google") == "google"

assert identify("quantas hrs?")["name"] == "time"
assert identify("que dia é hj?")["name"] == "day"

CONTEXT["last_engine"] = None

assert suggest_alias("abre o yotube", SITES + APPS) == ("yotube", "youtube")
assert suggest_alias("abre o discrd", SITES + APPS) == ("discrd", "discord")
assert suggest_alias("abre o word", SITES + APPS) is None

CONTEXT["pending_action"] = None
assert confirm("sim") == "Não tenho nada para confirmar agora."

CONTEXT["pending_action"] = (lambda arg: f"fiz {arg}", "x", datetime.now())
assert confirm("sim") == "fiz x"
CONTEXT["pending_action"] = (lambda arg: f"fiz {arg}", "x", datetime.now() - timedelta(minutes=2))
assert confirm("sim") == "Essa pergunta expirou. Me peça de novo."
CONTEXT["pending_action"] = (lambda arg: "ok", "x", datetime.now())
assert cancel("cancela") == "Ok, cancelado."
assert confirm("sim") == "Não tenho nada para confirmar agora."

assert identify("pesquise o que é isso")["name"] == "search"

assert invalid_targets({"x": {"open": ["vscod", "github"]}}, {"github"}) == [("x", "vscod")]
assert invalid_targets({"y": {"description": "sem open"}}, {"github"}) == []

assert find_routine("kitt, modo estudo", {"estudo": {}, "dev": {}}) == "estudo"
assert find_routine("modo DEV", {"estudo": {}, "dev": {}}) == "dev"
assert find_routine("modo festa", {"estudo": {}, "dev": {}}) is None
assert plan_routine({"open": ["fiap", "vscod"]}, {"fiap"}) == (["fiap"], ["vscod"])
assert plan_routine({}, {"fiap"}) == ([], [])

assert describe_code(63) == "chuva"
assert describe_code(12345) == "tempo indefinido"

fake = {
    "current": {"temperature_2m": 28.3, "weather_code": 1},
    "daily": {
        "temperature_2m_min": [19.2],
        "temperature_2m_max": [33.1],
        "precipitation_probability_max": [70],
    },
}
result = format_weather(fake)
assert "28°C, predominantemente limpo" in result
assert "☔ Leva guarda-chuva!" in result
assert "🥵 Vai fazer calor" in result

assert identify("vai chover hoje?")["name"] == "weather"
assert identify("há quanto tempo você está ligado?")["name"] == "uptime"


assert extract_track_query("toca yellow do coldplay no spotify") == "yellow do coldplay"
assert extract_track_query("kitt, tocar a música bohemian rhapsody no spotify") == "bohemian rhapsody"
assert extract_track_query("abre o spotify") == ""
assert format_track({"name": "Yellow", "artists": [{"name": "Coldplay"}]}) == "Yellow — Coldplay"
assert identify("toca yellow no spotify")["name"] == "spotify_track"
assert identify("toca a playlist lofi no spotify")["name"] == "spotify_play"
assert identify("o que está tocando no spotify?")["name"] == "spotify_now"

# ---- Volume do Spotify e do PC (reorganização) ----
from skills.media import parse_volume_request
from integrations.spotify.player import compute_new_volume

assert parse_volume_request("aumenta o volume") == ("auto", "up", 10)
assert parse_volume_request("abaixa o volume do spotify") == ("spotify", "down", 10)
assert parse_volume_request("aumenta o volume em 31") == ("auto", "up", 31)
assert parse_volume_request("volume do spotify em 29") == ("spotify", "set", 29)
assert parse_volume_request("aumenta o volume para 40") == ("auto", "set", 40)
assert parse_volume_request("aumenta o volume do pc") == ("pc", "up", 10)
assert parse_volume_request("volume 150") == ("auto", "set", 100)
assert parse_volume_request("volume") == ("auto", None, None)

assert compute_new_volume(50, "up", 31) == 81
assert compute_new_volume(50, "down", 29) == 21
assert compute_new_volume(90, "up", 20) == 100
assert compute_new_volume(10, "down", 30) == 0
assert compute_new_volume(70, "set", 29) == 29

assert identify("aumenta o volume do pc")["name"] == "media"
assert identify("volume do spotify em 30")["name"] == "spotify_track"
assert identify("como está o pc?")["name"] == "pc_status"

test_database()
print("Todos os testes passaram!")