import json
import logging
import os

logger = logging.getLogger("routines")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_PATH = os.path.join(PROJECT_DIR, "routines.json")

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
    for name, routines in routines.items():
        for target in routines.get("open", []):
            if target not in known_aliases:
                problems.append((name, target))
    return problems