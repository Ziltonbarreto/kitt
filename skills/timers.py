import logging
import threading

import winsound

from core.text_utils import normalize

logger = logging.getLogger("timers")


TIME_UNITS = {
    "segundo": 1, "segundos": 1, "seg": 1,
    "minuto": 60, "minutos": 60, "min": 60,
    "hora": 3600, "horas": 3600,
}


POMODORO_FOCUS = 25 * 60


POMODORO_CYCLES = 4


POMODORO_STATE = {"timer": None}


MAX_TIMER_SECONDS = 24 * 3600


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
