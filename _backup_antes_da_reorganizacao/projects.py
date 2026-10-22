import json
import logging
import os

from text_utils import normalize

logger = logging.getLogger("projects")

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_PATH = os.path.join(PROJECT_DIR, "projects.json")


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