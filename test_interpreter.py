from interpreter import identify
from commands import greet, MORNING_GREETINGS, AFTERNOON_GREETINGS, EVENING_GREETINGS, find_app, find_site, extract_query, build_search_url
from commands import CONTEXT, detect_engine


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

print("Todos os testes passaram!")