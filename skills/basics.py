import os
import random
from datetime import datetime


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


import logging

logger = logging.getLogger("basics")
