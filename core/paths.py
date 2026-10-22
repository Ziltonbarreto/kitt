"""Onde fica cada arquivo do projeto, não importa de onde o KITT seja aberto."""
from pathlib import Path





PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
