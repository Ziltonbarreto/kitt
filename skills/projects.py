import json
import logging
import os
import subprocess

from core.paths import DATA_DIR
from core.text_utils import normalize
from skills.apps import KNOWN_ALIASES, find_app, open_target
from skills.routines import plan_routine

logger = logging.getLogger("projects")

PROJECTS_PATH = DATA_DIR / "projects.json"


def load_projects():
    try:
        with open(PROJECTS_PATH, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Arquivo de projetos não encontrado: {PROJECTS_PATH}")
        return {}
    except json.JSONDecodeError as error:
        logger.error(f"projects.json com erro de formato: {error}")
        return {}


def find_project(text, projects):
    words = set(normalize(text))
    for key, project in projects.items():
        if set(project.get("aliases", [])) & words:
            return key
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
