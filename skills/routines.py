import json
import logging
from datetime import datetime

from core.context import set_pending
from core.database import favorite_hour
from core.paths import DATA_DIR
from core.text_utils import normalize
from skills.apps import KNOWN_ALIASES, open_target

logger = logging.getLogger("routines")

ROUTINES_PATH = DATA_DIR / "routines.json"


def load_routines():
    try:
        with open(ROUTINES_PATH, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Arquivo de rotinas não encontrado: {ROUTINES_PATH}")
        return {}
    except json.JSONDecodeError as error:
        logger.error(f"routines.json com erro de formato: {error}")
        return {}


def invalid_targets(routines, known_aliases):
    problems = []
    for name, routine in routines.items():
        for target in routine.get("open", []):
            if target not in known_aliases:
                problems.append((name, target))
    return problems


def find_routine(text, routines):
    words = set(normalize(text))
    for name in routines:
        if name in words:
            return name
    return None


def plan_routine(routine, known_aliases):
    valid = []
    skipped = []
    for target in routine.get("open", []):
        if target in known_aliases:
            valid.append(target)
        else:
            skipped.append(target)
    return valid, skipped


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
