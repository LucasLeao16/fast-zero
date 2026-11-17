"""Exercício 25: tarefas do taskipy para migrações."""

import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"


def tarefas():
    config = tomllib.loads(PYPROJECT.read_text("utf-8"))
    return config["tool"]["taskipy"]["tasks"]


def test_task_migrate():
    assert tarefas()["migrate"] == "alembic upgrade head"


def test_task_makemigrations():
    assert tarefas()["makemigrations"] == "alembic revision --autogenerate -m"
